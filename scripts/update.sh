#!/usr/bin/env bash
# Rebuild the JSON from saved club pages and copy it into the website seed.
# Usage: ./scripts/update.sh [folder-with-Beazdaa.html-Hever.html-BuyMe.html]
set -euo pipefail
cd "$(dirname "$0")/.."
DUMP="${1:-$HOME/Downloads/Moadonim/2026-11-6}"
BUYME="${2:-$HOME/Downloads/Moadonim/2026-11-07/BuyMe.html}"
if [[ -f "$BUYME" ]]; then
  python3 scripts/build_dataset.py --dump "$DUMP" --buyme "$BUYME"
else
  python3 scripts/build_dataset.py --dump "$DUMP"
fi
echo
echo "Next: commit and push this repo. The website reads these files from GitHub."
echo "A design change still needs ./scripts/deploy.sh in discounts-website."
