#!/bin/bash
set -e

LAN_IP=$(python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(('8.8.8.8', 80))
    print(s.getsockname()[0])
finally:
    s.close()
" 2>/dev/null || echo "localhost")

echo ""
echo "  BYOF starting..."
echo "  Local:   http://localhost:5173"
echo "  Network: http://$LAN_IP:5173"
echo ""

uv run python api.py &
API_PID=$!
trap "kill $API_PID 2>/dev/null" EXIT

cd frontend && npm run dev
