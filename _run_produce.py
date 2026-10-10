"""_run_produce.py — ComfyUI embedded python 隔离模式包装器（._pth 忽略 PYTHONPATH/CWD）。
用法与 pipeline.produce 完全一致：
  python _run_produce.py <workdir> --topic <topic.md> --model sol ...
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.argv = ["pipeline.produce"] + sys.argv[1:]

from pipeline.produce import main
raise SystemExit(main())
