#!/usr/bin/env python3
"""
Summarize Open ICS lint report (open_ics_report.json).

Outputs simple machine-checked, non-PII counts:
  - files scanned
  - warnings
  - errors

Usage (local):
  python3 .github/scripts/summarize_open_ics_report.py path/to/open_ics_report.json

Usage (GitHub Actions step):
  - name: Summarize Open ICS report
    run: |
      python3 .github/scripts/summarize_open_ics_report.py open_ics_report.json | tee summary.txt
      if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
        echo "$(cat summary.txt)" >> "$GITHUB_STEP_SUMMARY"
      fi
"""
from __future__ import annotations
import json, sys, pathlib

def summarize(p: pathlib.Path) -> str:
    raw = p.read_text(encoding='utf-8').strip() if p.exists() else ''
    try:
        data = json.loads(raw) if raw else []
    except Exception:
        data = []
    if isinstance(data, list):
        files = len(data)
        warnings = sum(len((d or {}).get('warnings', [])) for d in data if isinstance(d, dict))
        errors = sum(len((d or {}).get('errors', [])) for d in data if isinstance(d, dict))
    else:
        files = int(data.get('files_scanned', 0) or 0)
        warnings = int(data.get('warnings', 0) or 0)
        errors = int(data.get('errors', 0) or 0)
    return f"files={files} warnings={warnings} errors={errors}"

if __name__ == '__main__':
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'open_ics_report.json')
    print(summarize(path))
