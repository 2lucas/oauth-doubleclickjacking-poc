#!/usr/bin/env python3
"""
Vercel serverless entry point.
Imports the Flask app from main.py — all routes, templates, and static
files are served through this single function.

Deploy:  vercel
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel uses `app` as the WSGI handler automatically.
# Static files under /static/ and templates are resolved via Flask
# (app.root_path = project root, so templates/ and static/ work).
