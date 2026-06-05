"""
ParkPredict — Backend Entry Point
===================================
Run this file to start the Flask server.

Usage:
    python app.py

Server will start at:
    http://127.0.0.1:5000        ← same machine
    http://<your-ip>:5000        ← other devices on same WiFi
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  ParkPredict Backend v2.0.0")
    print("  Run: python app.py")
    print("  API: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
