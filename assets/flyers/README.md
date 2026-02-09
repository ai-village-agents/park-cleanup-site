# Printable flyers

These are **print-ready Letter (8.5×11 in) flyers** with QR codes for recruiting human volunteers.

Files:
- `flyer_general_letter.pdf` / `.png`
- `flyer_mission_dolores_letter.pdf` / `.png`
- `flyer_devoe_park_letter.pdf` / `.png`

QR destinations:
- **General flyer** → project site, plus a small QR to SF Issue #3
- **Mission Dolores flyer** → Issue #3, plus a small QR to the project site
- **Devoe Park flyer** → Issue #1, plus a small QR to the project site

## Re-generate

From repo root:

```bash
python scripts/make_flyers.py
```

The generator is offline (no network calls) and writes outputs into this folder.
