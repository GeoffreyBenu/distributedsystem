# heartbeat_monitor.py

import asyncio
from aiohttp import web
import time

# Dictionary to store server status: {server_id: last_heartbeat_time}
active_servers = {}  # {server_id: {"port": port, "timestamp": last_time}}

# Timeout for considering a server as "dead" (in seconds)
HEARTBEAT_TIMEOUT = 10

# ---------- HTTP ENDPOINTS ----------

async def receive_heartbeat(request):
    data = await request.json()
    server_id = data.get("server_id")
    port = data.get("port")
    if server_id and port:
        active_servers[server_id] = {"port": port, "timestamp": time.time()}
        return web.Response(text=f"Heartbeat received from {server_id}")
    return web.Response(status=400, text="Missing server_id or port")

async def get_active_servers(request):
    now = time.time()
    dead_servers = [
        sid for sid, info in active_servers.items()
        if now - info["timestamp"] > HEARTBEAT_TIMEOUT
    ]
    for sid in dead_servers:
        del active_servers[sid]

    # Return list of server addresses
    server_addresses = [
        f"localhost:{info['port']}" for info in active_servers.values()
    ]
    return web.json_response({"active_servers": server_addresses})

# ---------- BACKGROUND TASK ----------

async def cleanup_expired_servers():
    while True:
        await asyncio.sleep(HEARTBEAT_TIMEOUT)
        now = time.time()
        for server_id in list(active_servers):
            if now - active_servers[server_id] > HEARTBEAT_TIMEOUT:
                print(f"[Monitor] Server {server_id} is considered DEAD.")
                del active_servers[server_id]

# ---------- APP SETUP ----------

def create_app():
    app = web.Application()
    app.add_routes([
        web.post('/heartbeat', receive_heartbeat),
        web.get('/servers', get_active_servers),
    ])
    app.on_startup.append(start_cleanup_task)
    return app

async def start_cleanup_task(app):
    app['cleanup_task'] = asyncio.create_task(cleanup_expired_servers())

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=9000)
