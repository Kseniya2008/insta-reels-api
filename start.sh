#!/bin/bash
echo "Starting browser installation"
python3 -m playwright install chromium
echo "Running app"
gunicorn -w 1 -b 0.0.0.0:10000 api:app
