#!/bin/sh
set -eu
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.10 or later is required. See START-HERE.md."
  exit 2
fi
if [ "$#" -eq 0 ]; then set -- install; fi
exec python3 setup.py "$@" --platform macos
