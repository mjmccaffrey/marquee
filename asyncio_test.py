import aiohttp
import asyncio
import requests
import time

DIMMER_ADDRESSES = [
    '192.168.51.111',
    '192.168.51.112',
    '192.168.51.113',
    '192.168.51.114',
    '192.168.51.115',
]

def reboot_all():
    for ip in DIMMER_ADDRESSES:
        requests.get(f"http://{ip}/rpc/Shelly.Reboot")

async def fetch(ip, id, brightness):
    params = {
        'id': id, 
        'brightness': 90 if brightness else 10,
        'transition_duration': 0.5,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'http://{ip}/rpc/Light.Set', 
            params=params,
        ) as response:
            response = await response.text()

async def main():
    async with asyncio.TaskGroup() as tg:
        for i in range(1000):
            for ip in DIMMER_ADDRESSES:
                for id in range(2):
                    tg.create_task(fetch(ip, id, i % 2))
            await asyncio.sleep(2)

if __name__ == '__main__':
    asyncio.run(main())
