#!/usr/bin/env bash
# Build the site into dist/: pull syndicated articles, project the Papyrus site, write the legacy redirects.
# Needs `pip install -r requirements.txt` (Python 3.12 or 3.13).
set -euo pipefail
cd "$(dirname "$0")/.."

python scripts/syndicate.py
rm -rf dist
papyrus ops content project --all --from-dir content --static-dir web --out dist
python scripts/write_redirects.py dist
