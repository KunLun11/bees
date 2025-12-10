#!/bin/bash

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

exec granian \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --loop asyncio \
    --interface asgi \
    --log-level info \
    src.main:app