#!/usr/bin/env bash
set -euo pipefail
grep -R "[DONE]" -n src tests docs || true
