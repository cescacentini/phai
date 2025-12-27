#!/bin/bash
# Script to run the PHAI GUI application

cd "$(dirname "$0")"
source PHAIenv/bin/activate
python gui_app.py


