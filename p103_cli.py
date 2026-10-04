"""Convenience launcher for environments where Project 103 is not installed."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from p103.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
