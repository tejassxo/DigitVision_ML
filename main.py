"""
DigitVision AI — Main Application Entrypoint
"""

import os
import sys
import uvicorn

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.app.server import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting DigitVision AI production server on http://127.0.0.1:{port}...")
    uvicorn.run("src.app.server:app", host="0.0.0.0", port=port, log_level="info")
