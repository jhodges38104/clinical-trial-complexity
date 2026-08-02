#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
#  Clinical Trial Complexity Assessor — Local Launcher
#  Works on macOS and Linux
# ─────────────────────────────────────────────────────────

PORT=8080
DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "  Clinical Trial Complexity Assessor"
echo "  ─────────────────────────────────────"
echo "  Starting local server on http://localhost:$PORT"
echo "  Press Ctrl+C to stop."
echo ""

# Open browser after a short delay
(sleep 1.5 && \
  if command -v xdg-open &>/dev/null; then
    xdg-open "http://localhost:$PORT"
  elif command -v open &>/dev/null; then
    open "http://localhost:$PORT"
  fi
) &

# Start server
if command -v python3 &>/dev/null; then
  python3 -m http.server $PORT --directory "$DIR"
elif command -v python &>/dev/null; then
  cd "$DIR" && python -m SimpleHTTPServer $PORT
else
  echo "ERROR: Python not found. Please install Python 3 or open index.html directly."
  exit 1
fi
