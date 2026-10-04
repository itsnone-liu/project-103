"""Small, filesystem-backed run lifecycle for Project 103.

This is deliberately infrastructure, not a teaching/content IR: project.json,
run.json and artifact paths are the only contracts enforced here.
"""
from __future__ import annotations

import json
import logging
import re
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATES = ("CREATED", "PLANNING", "BUILDING", "RENDERING", "VERIFYING", "REPAIRING", "FINAL", "FAILED")
_TRANSITIONS = {
    "CREATED": {"PLANNING", "FAILED"},
    "PLANNING": {"BUILDING", "FAILED"},
    "BUILDING": {"RENDERING", "FAILED"},
    "RENDERING": {"VERIFYING", "FAILED"},
    "VERIFYING": {"FINAL", "REPAIRING", "FAILED"},
    "REPAIRING": {"RENDERING", "FAILED"},
    "FINAL": set(),
    "FAILED": set(),
}
_SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _json_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _json_read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def validate_project(project: dict[str, Any]) -> dict[str, Any]:
    if project.get("mode") not in {"video", "interactive"}:
        raise ValueError("project.mode must be 'video' or 'interactive'")
    if project.get("language", "zh-CN") not in {"zh-CN", "en-US"}:
        raise ValueError("project.language must be zh-CN or en-US")
    repairs = project.get("max_repairs", 1)
    if not isinstance(repairs, int) or isinstance(repairs, bool) or not 0 <= repairs <= 1:
        raise ValueError("project.max_repairs must be 0 or 1")
    duration = project.get("target_duration")
    if duration is not None:
        if (not isinstance(duration, list) or len(duration) != 2 or
                any(not isinstance(n, (int, float)) or isinstance(n, bool) for n in duration) or
                duration[0] <= 0 or duration[1] < duration[0]):
            raise ValueError("project.target_duration must be [positive_min, max>=min]")
    return project


def default_project(run_id: str, mode: str, source: str, model: str = "sol") -> dict[str, Any]:
    return validate_project({
        "id": run_id,
        "mode": mode,
        "language": "zh-CN",
        "source": source,
        "model": model,
        "max_repairs": 1,
    })


@dataclass
class Run:
    root: Path

    @property
    def run_id(self) -> str:
        return self.root.name

    @property
    def project_file(self) -> Path:
        return self.root / "project.json"

    @property
    def state_file(self) -> Path:
        return self.root / "run.json"

    def project(self) -> dict[str, Any]:
        return validate_project(_json_read(self.project_file))

    def state(self) -> dict[str, Any]:
        return _json_read(self.state_file)

    def log_event(self, event: str, detail: str = "") -> None:
        line = f"{_now()}\t{event}\t{detail.replace(chr(9), ' ').replace(chr(10), ' ')}\n"
        log_path = self.root / "run.log"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(line)

    def transition(self, target: str, note: str = "") -> dict[str, Any]:
        if target not in STATES:
            raise ValueError(f"Unknown state: {target}")
        data = self.state()
        current = data["state"]
        if target not in _TRANSITIONS[current]:
            raise ValueError(f"Illegal state transition: {current} -> {target}")
        data["state"] = target
        data["updated_at"] = _now()
        data.setdefault("history", []).append({"state": target, "at": data["updated_at"], "note": note})
        _json_write(self.state_file, data)
        self.log_event("state", f"{current}->{target}; {note}")
        return data

    def artifact(self, relative: str) -> Path:
        # Reject absolute paths and traversal, while allowing normal nested artifact paths.
        candidate = Path(relative)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError("Artifact path must stay inside the run directory")
        result = (self.root / candidate).resolve()
        if self.root.resolve() not in result.parents and result != self.root.resolve():
            raise ValueError("Artifact path escapes run directory")
        result.parent.mkdir(parents=True, exist_ok=True)
        return result

    def status(self) -> dict[str, Any]:
        return {"run_id": self.run_id, "root": str(self.root), **self.state(), "project": self.project()}


def create_run(workspace: Path, mode: str, source: Path, run_id: str | None = None, model: str = "sol") -> Run:
    workspace = workspace.resolve()
    if mode not in {"video", "interactive"}:
        raise ValueError("mode must be video or interactive")
    source = source.resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Source file does not exist: {source}")
    run_id = run_id or f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    if not _SLUG.fullmatch(run_id):
        raise ValueError("run-id must be a short ASCII slug (letters/digits/._-)")
    root = workspace / "runs" / run_id
    if root.exists():
        raise FileExistsError(f"Run already exists: {root}")
    for folder in ("input", "plan", "audio", "scenes", "attempt-1", "verification", "final"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    target_source = root / "input" / source.name
    shutil.copy2(source, target_source)
    project = default_project(run_id, mode, f"input/{source.name}", model=model)
    state = {
        "run_id": run_id,
        "state": "CREATED",
        "created_at": _now(),
        "updated_at": _now(),
        "repair_count": 0,
        "max_repairs": project["max_repairs"],
        "history": [{"state": "CREATED", "at": _now(), "note": "run created"}],
    }
    _json_write(root / "project.json", project)
    _json_write(root / "run.json", state)
    run = Run(root)
    run.log_event("created", f"mode={mode}; source=input/{source.name}")
    logging.getLogger("p103").info("created run %s", run_id)
    return run


def load_run(workspace: Path, run_id: str) -> Run:
    if not _SLUG.fullmatch(run_id):
        raise ValueError("run-id must be a short ASCII slug (letters/digits/._-)")
    root = (workspace.resolve() / "runs" / run_id).resolve()
    if root.parent != (workspace.resolve() / "runs").resolve() or not (root / "run.json").is_file():
        raise FileNotFoundError(f"No run found: {run_id}")
    return Run(root)


def record_repair(run: Run, note: str = "") -> dict[str, Any]:
    state = run.state()
    if state["state"] != "VERIFYING":
        raise ValueError("Repair can only be recorded while VERIFYING")
    if state.get("repair_count", 0) >= state.get("max_repairs", 1):
        raise ValueError("Repair limit reached")
    state["repair_count"] = state.get("repair_count", 0) + 1
    state["updated_at"] = _now()
    _json_write(run.state_file, state)
    run.transition("REPAIRING", note)
    return run.state()
