"""Command line entry point for Project 103 run and video infrastructure."""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

from .artifacts import read_manifest, register_media, verify_registered_media
from .core import create_run, load_run, record_repair
from .media import probe_media, sha256_file
from .remotion import generate_remotion_timeline
from .remotion_template import write_consumer
from .timeline import generate_srt, import_subtitles, remotion_frames, validate_timeline, align_tts_cues, parse_cues, NarrationLine, Timeline, SCHEMA_VERSION
from .tts import generate_edge_tts
from .video_qa import create_contact_sheet, extract_keyframes, verify_video


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="p103", description="Manage Project 103 production runs")
    p.add_argument("--workspace", type=Path, default=Path.cwd(), help="Project 103 workspace (default: cwd)")
    p.add_argument("--verbose", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)
    for mode in ("video", "interactive"):
        cmd = sub.add_parser(mode, help=f"create a {mode} run from source text")
        cmd.add_argument("source", type=Path)
        cmd.add_argument("--run-id")
        cmd.add_argument("--model", default="sol")
    resume = sub.add_parser("resume", help="inspect/resume an existing run")
    resume.add_argument("run_id")
    resume.add_argument("--set-state", choices=["PLANNING", "BUILDING", "RENDERING", "VERIFYING", "REPAIRING", "FINAL", "FAILED"])
    resume.add_argument("--note", default="")
    status = sub.add_parser("status", help="show run status")
    status.add_argument("run_id")
    artifact = sub.add_parser("artifact", help="print a safe artifact path")
    artifact.add_argument("run_id")
    artifact.add_argument("relative_path")
    timeline = sub.add_parser("timeline", help="import VTT/SRT into the run narration timeline")
    timeline.add_argument("run_id")
    timeline.add_argument("subtitle_file", type=Path)
    timeline.add_argument("--scene", default="scene-01")
    timeline.add_argument("--fps", type=int, default=30)
    timeline.add_argument("--display-texts", type=Path)
    timeline.add_argument("--audio", type=Path)
    timeline.add_argument("--anchors", type=Path)
    timeline.add_argument("--tts-texts", type=Path, help="optional JSON array of exact per-segment TTS text")
    tts = sub.add_parser("tts", help="generate audio plus sentence subtitles via edge-tts")
    tts.add_argument("run_id")
    tts.add_argument("text_file", type=Path)
    tts.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    tts.add_argument("--rate", default="+0%")
    align = sub.add_parser("align-tts", help="validate provider cue text coverage and attach sentence timing")
    align.add_argument("run_id")
    align.add_argument("--cue-vtt", default="audio/provider-cues.vtt")
    probe = sub.add_parser("probe", help="identify a media file and probe duration/streams")
    probe.add_argument("media_file", type=Path)
    consumer = sub.add_parser("remotion-consumer", help="generate a configurable Remotion shell")
    consumer.add_argument("run_id")
    consumer.add_argument("--audio-static-path", default="audio/narration.mp3")
    consumer.add_argument("--scene-spec", type=Path)
    verify_media = sub.add_parser("verify-media", help="recheck registered asset hashes before rendering")
    verify_media.add_argument("run_id")
    render = sub.add_parser("render", help="render run composition into attempt-1")
    render.add_argument("run_id")
    render.add_argument("--composition", default="P103TimelineConsumer")
    render.add_argument("--output", default="attempt-1/attempt-1.mp4")
    render.add_argument("--codec", default="h264")
    render.add_argument("--crf", default="18")
    qa = sub.add_parser("video-qa", help="verify video and generate keyframes/contact sheet")
    qa.add_argument("run_id")
    qa.add_argument("video", nargs="?", default="attempt-1/attempt-1.mp4")
    qa.add_argument("--fps", type=float, default=30)
    qa.add_argument("--width", type=int, default=1920)
    qa.add_argument("--height", type=int, default=1080)
    qa.add_argument("--keyframes", type=int, default=8)
    finalize = sub.add_parser("finalize", help="promote a verified attempt to final")
    finalize.add_argument("run_id")
    finalize.add_argument("--input", default="attempt-1/attempt-1.mp4")
    return p


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def import_subtitles_from_manifest(manifest: dict) -> Timeline:
    cues = tuple(NarrationLine(c["id"], c["scene_id"], c["display_text"], c["narration_text"], c["tts_text"], c["start_ms"], c["end_ms"], c.get("tts_cue_text", ""), c.get("source", "imported")) for c in manifest.get("cues", []))
    return Timeline(manifest.get("schema_version", SCHEMA_VERSION), manifest.get("duration_ms", 0), cues, manifest.get("source_format", "vtt"), fps=manifest.get("fps", 30), tts=manifest.get("tts"), vtt=manifest.get("vtt"), segments=tuple(manifest.get("segments", [])))


def _run_root(args) -> Path:
    return load_run(args.workspace, args.run_id).root


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")
    try:
        if args.command in {"video", "interactive"}:
            run = create_run(args.workspace, args.command, args.source, args.run_id, args.model)
            print(json.dumps(run.status(), ensure_ascii=False, indent=2))
            return 0
        if args.command == "probe":
            print(json.dumps(probe_media(args.media_file), ensure_ascii=False, indent=2))
            return 0
        run = load_run(args.workspace, args.run_id)
        if args.command == "status":
            print(json.dumps(run.status(), ensure_ascii=False, indent=2))
            return 0
        if args.command == "artifact":
            print(run.artifact(args.relative_path))
            return 0
        if args.command == "timeline":
            display_texts = json.loads(args.display_texts.read_text(encoding="utf-8-sig")) if args.display_texts else None
            if display_texts is not None and (not isinstance(display_texts, list) or not all(isinstance(x, str) for x in display_texts)):
                raise ValueError("--display-texts must be a JSON array of strings")
            if args.fps <= 0:
                raise ValueError("fps must be positive")
            fmt = {".vtt": "vtt", ".srt": "srt"}.get(args.subtitle_file.suffix.lower())
            tts_texts = json.loads(args.tts_texts.read_text(encoding="utf-8-sig")) if args.tts_texts else None
            if tts_texts is not None and (not isinstance(tts_texts, list) or not all(isinstance(x, str) for x in tts_texts)):
                raise ValueError("--tts-texts must be a JSON array of strings")
            timeline = import_subtitles(args.subtitle_file, display_texts=display_texts, tts_texts=tts_texts, scene_id=args.scene, source_format=fmt, fps=args.fps)
            # Preserve run-local copies so render-time hash verification is hermetic.
            audio_copy = None
            if args.audio:
                audio_copy = run.artifact("audio/narration" + args.audio.suffix.lower())
                if args.audio.resolve() != audio_copy.resolve():
                    shutil.copy2(args.audio, audio_copy)
                audio_probe = probe_media(audio_copy)
                timeline.tts = {"path": str(audio_copy.relative_to(run.root)).replace("\\", "/"), "sha256": audio_probe["sha256"], "audio_duration_ms": audio_probe["duration_ms"], "probe": audio_probe["probe"]}
                public_audio = (run.root / "public" / "audio" / audio_copy.name).resolve()
                if run.root.resolve() not in public_audio.parents:
                    raise ValueError("Remotion public audio path escapes run root")
                public_audio.parent.mkdir(parents=True, exist_ok=True)
                if public_audio.resolve() != audio_copy.resolve():
                    shutil.copy2(audio_copy, public_audio)
            # Preserve a run-local copy so manifest paths and render-time hash verification are stable.
            vtt_copy = run.artifact("audio/source-subtitles" + (args.subtitle_file.suffix.lower() if args.subtitle_file.suffix.lower() in {".vtt", ".srt"} else ".txt"))
            shutil.copy2(args.subtitle_file, vtt_copy)
            timeline.vtt["path"] = str(vtt_copy.relative_to(run.root)).replace("\\", "/")
            manifest = timeline.to_dict()
            manifest["tts"] = timeline.tts
            manifest["vtt"] = timeline.vtt
            media_records = register_media(run.root, manifest)
            timeline.tts = manifest.get("tts")
            timeline.vtt = manifest.get("vtt")
            audio_duration = (manifest.get("tts") or {}).get("audio_duration_ms")
            if audio_duration and timeline.duration_ms > audio_duration + 500:
                raise ValueError("Subtitle end exceeds audio duration beyond 500ms tolerance")
            errors = validate_timeline(timeline, frame_rate=args.fps)
            if errors:
                raise ValueError("Timeline validation failed: " + "; ".join(errors))
            _write_json(run.artifact("audio/timeline.json"), manifest)
            generate_srt(timeline, run.artifact("audio/subtitles.srt"), text_layer="display_text")
            anchors = json.loads(args.anchors.read_text(encoding="utf-8-sig")) if args.anchors else []
            remotion = generate_remotion_timeline(timeline, run.artifact("src/generated"), anchors=anchors, audio_duration_ms=audio_duration)
            _write_json(run.artifact("audio/remotion-frames.json"), remotion)
            run.log_event("timeline_imported", f"{len(timeline.cues)} cues; audio={audio_duration}; media={len(media_records)}")
            print(json.dumps({"run_id": run.run_id, "cues": len(timeline.cues), "audio_duration_ms": audio_duration, "duration_frames": remotion["durationInFrames"], "outputs": ["audio/timeline.json", "audio/subtitles.srt", "src/generated/timeline.ts"]}, ensure_ascii=False, indent=2))
            return 0
        if args.command == "align-tts":
            manifest = read_manifest(run.root)
            timeline = import_subtitles_from_manifest(manifest)
            cue_file = run.artifact(args.cue_vtt)
            cue_rows, _ = parse_cues(cue_file.read_text(encoding="utf-8-sig"), source_format="vtt")
            actual_sha = sha256_file(cue_file)
            registered_cues = manifest.get("tts_cues") or {}
            if registered_cues.get("sha256") and registered_cues["sha256"] != actual_sha:
                raise ValueError("E_MEDIA_HASH_MISMATCH: TTS sentence cues changed before alignment")
            aligned = align_tts_cues(timeline, [row[2] for row in cue_rows], [(row[0], row[1]) for row in cue_rows])
            manifest["tts_alignment"] = {"source": args.cue_vtt, "segments": aligned, "coverage": "exact-normalized"}
            manifest["tts_cues"] = {"path": args.cue_vtt.replace("\\", "/"), "sha256": actual_sha}
            _write_json(run.artifact("audio/timeline.json"), manifest)
            print(json.dumps({"segments": len(aligned), "coverage": "exact-normalized"}, ensure_ascii=False, indent=2))
            return 0
        if args.command == "tts":
            text = args.text_file.read_text(encoding="utf-8-sig")
            result = generate_edge_tts(text, run.artifact("audio/narration.mp3"), run.artifact("audio/provider-cues.vtt"), voice=args.voice, rate=args.rate)
            manifest = read_manifest(run.root) if (run.root / "audio" / "timeline.json").is_file() else {}
            manifest["tts"] = {"path": "audio/narration.mp3", "sha256": result["sha256"], "audio_duration_ms": result["audio_duration_ms"], "engine": result["engine"], "voice": result["voice"], "rate": result["rate"]}
            manifest["tts_cues"] = {"path": "audio/provider-cues.vtt", "sha256": sha256_file(run.root / "audio" / "provider-cues.vtt")}
            _write_json(run.artifact("audio/timeline.json"), manifest)
            print(json.dumps({"run_id": run.run_id, **result}, ensure_ascii=False, indent=2))
            return 0
        if args.command == "remotion-consumer":
            scene_specs = json.loads(args.scene_spec.read_text(encoding="utf-8-sig")) if args.scene_spec else None
            write_consumer(run.root, audio_static_path=args.audio_static_path, scene_specs=scene_specs)
            print(json.dumps({"run_id": run.run_id, "consumer": "src/generated/TimelineConsumer.tsx"}, ensure_ascii=False, indent=2))
            return 0
        if args.command == "verify-media":
            manifest = read_manifest(run.root)
            verified = verify_registered_media(run.root, manifest)
            run.log_event("media_verified", f"{len(verified)} assets")
            print(json.dumps({"run_id": run.run_id, "verified": verified}, ensure_ascii=False, indent=2))
            return 0
        if args.command == "render":
            manifest = read_manifest(run.root)
            verified = verify_registered_media(run.root, manifest)
            package_json = run.root / "package.json"
            if not package_json.is_file():
                raise ValueError("Run has no package.json; initialize a Remotion consumer before rendering")
            audio_desc = manifest.get("tts") or {}
            static_path = run.root / "public" / "audio" / Path(audio_desc.get("path", "narration.mp3")).name
            if audio_desc.get("path"):
                registered_audio = (run.root / audio_desc["path"]).resolve()
                if not registered_audio.is_file() or not static_path.is_file() or sha256_file(static_path) != sha256_file(registered_audio):
                    raise ValueError("E_MEDIA_HASH_MISMATCH: Remotion public audio missing or differs from registered narration")
            cli = run.root / "node_modules" / ".bin" / "remotion.cmd"
            if not cli.is_file():
                cli = run.root / "node_modules" / "remotion" / "dist" / "cli.mjs"
            if not cli.is_file():
                raise FileNotFoundError("Remotion CLI not found in run node_modules")
            if cli.suffix.lower() == ".mjs":
                cli_prefix = [shutil.which("node") or "node", str(cli)]
            elif cli.suffix.lower() == ".cmd":
                cli_prefix = ["cmd", "/c", str(cli)]
            else:
                cli_prefix = [str(cli)]
            output = run.artifact(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            command = cli_prefix + ["render", "src/index.ts", args.composition, str(output), f"--codec={args.codec}", f"--crf={args.crf}"]
            subprocess.run(command, cwd=run.root, check=True)
            run.log_event("render_complete", f"{args.composition} -> {args.output}; verified_assets={len(verified)}")
            print(json.dumps({"run_id": run.run_id, "output": str(output.relative_to(run.root)), "verified_assets": verified}, ensure_ascii=False, indent=2))
            return 0
        if args.command == "video-qa":
            video = Path(args.video)
            video = video if video.is_absolute() else run.root / video
            info = verify_video(video, expected_fps=args.fps, expected_width=args.width, expected_height=args.height)
            frames = extract_keyframes(video, run.artifact("verification/keyframes"), count=args.keyframes, tool_root=run.root.parent.parent)
            sheet = create_contact_sheet(frames, run.artifact("verification/contact-sheet.png"), tool_root=run.root.parent.parent)
            report = {"schema_version": "p103.video-qa/v1", "video": str(video.relative_to(run.root)), "video_sha256": sha256_file(video), "probe": info, "keyframes": [str(p.relative_to(run.root)) for p in frames], "contact_sheet": str(sheet.relative_to(run.root)), "passed": True}
            _write_json(run.artifact("verification/report.json"), report)
            run.log_event("video_verified", f"{len(frames)} keyframes; contact sheet produced")
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0
        if args.command == "finalize":
            source = run.artifact(args.input)
            report = json.loads(run.artifact("verification/report.json").read_text(encoding="utf-8"))
            if not report.get("passed") or Path(report.get("video", "")).resolve() != Path(args.input).resolve() or report.get("video_sha256") != sha256_file(source):
                raise ValueError("Cannot finalize: matching passing verification report and unchanged video hash are required")
            target = run.artifact("final/final.mp4")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            run.log_event("finalized", "verified attempt copied to final/final.mp4")
            print(json.dumps({"run_id": run.run_id, "final": str(target.relative_to(run.root))}, ensure_ascii=False, indent=2))
            return 0
        if args.command == "resume":
            if args.set_state == "REPAIRING":
                record_repair(run, args.note)
            elif args.set_state:
                run.transition(args.set_state, args.note or "resume command")
            print(json.dumps(run.status(), ensure_ascii=False, indent=2))
            return 0
        return 2
    except (ValueError, FileNotFoundError, json.JSONDecodeError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"p103: error: {exc}", file=sys.stderr)
        return 2
    except FileExistsError as exc:
        print(f"p103: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
