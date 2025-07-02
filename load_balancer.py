# load_balancer.py

import asyncio
import random
from aiohttp import web, ClientSession

# Heartbeat Monitor API
HEARTBEAT_MONITOR_URL = "http://localhost:9000/servers"

# Server list cache and index for round-robin
active_servers = []
server_index = 0

# ---------- HTTP ENDPOINT ----------

async def handle_client_request(request):
    global server_index

    # Update list of active servers
    await refresh_active_servers()

    if not active_servers:
        return web.Response(status=503, text="No servers available")

    # Select server using round-robin
    server_url = active_servers[server_index]
    server_index = (server_index + 1) % len(active_servers)

    print(f"[Balancer] Forwarding request to: {server_url}")

    async with ClientSession() as session:
        try:
            async with session.get(f"http://{server_url}/process") as resp:
                data = await resp.json()
                return web.json_response({"from_server": server_url, "data": data})
        except Exception as e:
            return web.Response(status=502, text=f"Error forwarding to server: {e}")

# ---------- HELPER ----------

async def refresh_active_servers():
    global active_servers
    try:
        async with ClientSession() as session:
            async with session.get(HEARTBEAT_MONITOR_URL) as resp:
                result = await resp.json()
                # Assume servers are sending port only (e.g., 8001)
                active_servers = result["active_servers"]
    except Exception as e:
        print(f"[Balancer] Failed to fetch servers: {e}")
        active_servers = []

# ---------- APP SETUP ----------

def create_app():
    app = web.Application()
    app.add_routes([
        web.get('/', handle_client_request),
    ])
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=8080)
