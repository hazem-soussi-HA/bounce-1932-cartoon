#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8765}"
if ! ss -tln 2>/dev/null | grep -q ":$PORT "; then
  python3 -m http.server "$PORT" --bind 127.0.0.1 >/tmp/bounce_server.log 2>&1 &
  sleep 1
fi
URL="http://127.0.0.1:$PORT/watch.html"
echo "BOUNCE! player: $URL"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 || true
fi
