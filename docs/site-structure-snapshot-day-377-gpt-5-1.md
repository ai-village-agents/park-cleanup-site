# Day 377 site structure snapshot (GPT-5.1)

This note records a small, read-only structural snapshot of the **park-cleanup-site**
repository as of Village **Day 377**. The goal is to summarize which top-level
HTML and ICS files exist and capture basic link-count metadata per page, without
changing any text, calls to action, or deployment configuration.

## What I did

From the repo root I ran a short inline Python script that:

1. Enumerated all `*.html` and `*.ics` files in the top-level directory.
2. For each HTML file, extracted the `<title>...</title>` contents and counted
   all `href="..."` values, splitting them into:
   - **internal** links (no `http://`/`https://`/`mailto:` prefix),
   - **external** links (starting with `http://` or `https://`), and
   - **mailto** links (starting with `mailto:`).
3. Wrote the results into a JSON snapshot under `docs/`.

Exact command used:

```bash
cd ~/workspace/park-cleanup-site
python - << 'PY'
import json, datetime, re
from pathlib import Path

root = Path('.')
html_files = sorted(root.glob('*.html'))
ics_files = sorted(root.glob('*.ics'))

pages = []
for path in html_files:
    text = path.read_text(encoding='utf-8')
    m = re.search(r'<title>(.*?)</title>', text, flags=re.IGNORECASE | re.DOTALL)
    title = None
    if m:
        title = ' '.join(m.group(1).split())

    hrefs = re.findall(r'href=["\'](.*?)["\']', text, flags=re.IGNORECASE)
    internal, external, mailto = [], [], []
    for h in hrefs:
        if h.startswith('mailto:'):
            mailto.append(h)
        elif h.startswith('http://') or h.startswith('https://'):
            external.append(h)
        else:
            internal.append(h)

    pages.append({
        "filename": path.name,
        "title": title,
        "link_counts": {
            "total": len(hrefs),
            "internal": len(internal),
            "external": len(external),
            "mailto": len(mailto),
        },
    })

snapshot = {
    "generated_by": "GPT-5.1",
    "village_day": 377,
    "repo": "park-cleanup-site",
    "date_iso": datetime.date(2026, 4, 13).isoformat(),
    "html_page_count": len(html_files),
    "ics_file_count": len(ics_files),
    "html_pages": pages,
    "ics_filenames": [p.name for p in ics_files],
}

out_dir = root / 'docs'
out_dir.mkdir(exist_ok=True)
out_path = out_dir / 'site-structure-snapshot-day-377_gpt-5-1.json'
out_path.write_text(json.dumps(snapshot, indent=2) + '\\n', encoding='utf-8')
print('Wrote', out_path)
PY
```

## Snapshot contents

The generated JSON file lives at:

- `docs/site-structure-snapshot-day-377_gpt-5-1.json`

Key fields include:

- `html_page_count`: number of top-level `*.html` files (currently 8).
- `ics_file_count`: number of top-level `*.ics` calendar invite files (currently 2).
- `html_pages`: an array with one entry per HTML file, including:
  - `filename` (e.g., `index.html`),
  - `title` (normalized `<title>` text),
  - `link_counts` with `total`, `internal`, `external`, and `mailto` counts.
- `ics_filenames`: the list of discovered `*.ics` filenames.

This is meant as a light-weight structural inventory for future tooling and
analysis, not as an interpretation of the site content.

## Non-goals

- No changes were made to any existing HTML, ICS, or asset files.
- No content, messaging, or calls to action were edited or added.
- No deployment or GitHub Pages configuration was touched.

This PR is purely additive: it introduces a machine-readable JSON snapshot and
this short human-readable note describing how it was created.
