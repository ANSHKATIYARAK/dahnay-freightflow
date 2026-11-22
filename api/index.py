"""
Vercel Serverless Entry Point for FreightFlow FastAPI
"""

import os
import sys

# Ensure root and dahnay_logistics are in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
dahnay_dir = os.path.join(parent_dir, "dahnay_logistics")
if dahnay_dir not in sys.path:
    sys.path.insert(0, dahnay_dir)

from app import app
