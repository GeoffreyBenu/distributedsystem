# server.py

import asyncio
from aiohttp import web, ClientSession
import socket
import os

# Server config
SERVER_ID = os.environ.get("SERVER_ID", f"server_{socket.gethostname()}")
SERVER_PORT = int(os.environ.get("SERVER_PORT", 8001))

# Heartbeat monitor location
HEARTBEAT_URL = "http://localhost:9000/heartbeat"

# ---------- HTTP ENDPOINTS ----------

async def handle_request(request):
    return web.json_response({"server_id": SERVER_ID, "message": "Request processed!"})

# ---------- HEARTBEAT TASK ----------

async def send_heartbeat():
    async with ClientSession() as session:
        while True:
            try:
                await session.post(HEARTBEAT_URL, json={"server_id": SERVER_ID, "port": SERVER_PORT})
                print(f"[{SERVER_ID}] Sent heartbeat")
            except Exception as e:
                print(f"[{SERVER_ID}] Heartbeat failed: {e}")
            await asyncio.sleep(5)

# ---------- APP SETUP ----------

def create_app():
    app = web.Application()
    app.add_routes([
        web.get('/process', handle_request),
    ])
    app.on_startup.append(start_heartbeat_task)
    return app

async def start_heartbeat_task(app):
    app['heartbeat_task'] = asyncio.create_task(send_heartbeat())

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=SERVER_PORT)
