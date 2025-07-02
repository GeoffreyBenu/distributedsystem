# client.py

import asyncio
import aiohttp

LOAD_BALANCER_URL = "http://localhost:8080"

async def send_request(session, i):
    try:
        async with session.get(LOAD_BALANCER_URL) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"[Client] Request {i}: Response from {data['from_server']}: {data['data']}")
            else:
                print(f"[Client] Request {i}: Error {resp.status} - {await resp.text()}")
    except Exception as e:
        print(f"[Client] Request {i}: Failed to reach load balancer: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, i) for i in range(1, 11)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
