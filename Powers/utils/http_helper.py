import requests
from asyncio import gather
from aiohttp import ClientSession

async def post(url: str, *args, **kwargs):
    async with ClientSession().post(url, *args, **kwargs) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = await resp.text()
    return data

def get(url: str, *args, **kwargs):
    resp = requests.get(url, *args, **kwargs)
    try:
        data = resp.json()
    except Exception:
        data = resp.text()
    return data


def head(url: str, *args, **kwargs):
    resp = requests.head(url, *args, **kwargs)
    try:
        data = resp.json()
    except Exception:
        data = resp.text()
    return data


def post(url: str, *args, **kwargs):
    resp = requests.post(url, *args, **kwargs)
    try:
        data = resp.json()
    except Exception:
        data = resp.text()
    return data


async def multiget(url: str, times: int, *args, **kwargs):
    return await gather(*[get(url, *args, **kwargs) for _ in range(times)])


async def multihead(url: str, times: int, *args, **kwargs):
    return await gather(*[head(url, *args, **kwargs) for _ in range(times)])


async def multipost(url: str, times: int, *args, **kwargs):
    return await gather(*[post(url, *args, **kwargs) for _ in range(times)])


def resp_get(url: str, *args, **kwargs):
        return requests.get(url, *args, **kwargs)


def resp_post(url: str, *args, **kwargs):
    return requests.post(url, *args, **kwargs)
