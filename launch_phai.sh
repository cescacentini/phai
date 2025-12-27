#!/bin/bash
# Simple launcher script for PHAI

cd "$(dirname "$0")"
source PHAIenv/bin/activate
python gui_app.py

