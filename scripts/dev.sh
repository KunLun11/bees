#!/bin/bash

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

exec granian \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --loop asyncio \
    --interface asgi \
    --reload \
    --log-level debug \
    src.main:app