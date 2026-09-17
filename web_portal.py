"""
Web portal proxy module delegating to the complete Grace Outreach Assistant application (main.py).
"""
import os
from wsgiref.simple_server import make_server
from main import app, HOST, PORT, read_shared_state, update_shared_state

if __name__ == "__main__":
    port = int(os.environ.get("PORT", PORT))
    print(f"[ONLINE] Grace Outreach Assistant running on http://{HOST}:{port}")
    with make_server(HOST, port, app) as httpd:
        httpd.serve_forever()
