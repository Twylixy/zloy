#!/bin/sh

echo "Starting bot"
# If need debug whole start progress
# python -m debugpy --wait-for-client --listen 0.0.0.0:5678 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
# Don't wait for client, run immediately
python3 -m debugpy --listen 0.0.0.0:5678 -m app --host 0.0.0.0 --port 8000 --reload
