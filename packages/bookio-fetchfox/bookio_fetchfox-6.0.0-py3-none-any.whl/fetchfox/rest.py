import asyncio
import json
import logging
import ssl
from typing import Tuple

import backoff
import certifi
from aiohttp import TCPConnector, ClientSession, ClientTimeout
from aiohttp.client_exceptions import ContentTypeError

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, exception=Exception, max_time=30)
def get(url: str, headers: dict = None, params: dict = None, sleep: float = 0.05, timeout: float = None, check: str = None) -> Tuple[dict, int]:
    headers = {name: value for name, value in (headers or {}).items() if value is not None}
    params = {name: value for name, value in (params or {}).items() if value is not None}

    async def aux():
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = TCPConnector(ssl=ssl_context)

        client = ClientSession(connector=conn, timeout=ClientTimeout(timeout))

        await asyncio.sleep(sleep)

        async with client as session:
            logger.info("REST: GET %s", url)

            async with session.get(url, headers=headers, params=params) as response:
                status_code = response.status

                try:
                    json_content = await response.json()
                except ContentTypeError:
                    json_content = None

            await response.release()

        if status_code == 429:
            if "Retry-After" in response.headers:  # opensea.io
                wait = int(response.headers["Retry-After"]) + 5
                logger.info("too many requests, waiting for %ss", wait)
                await asyncio.sleep(wait)
                response.raise_for_status()
            elif json_content.get("detail") == "Request was throttled.":  # opensea.io
                wait = 90
            else:
                wait = 30

            logger.info("too many requests, waiting for %ss", wait)
            await asyncio.sleep(wait)
            response.raise_for_status()

        if check:
            assert check in json_content

        return json_content, status_code

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(aux())
    loop.close()

    return result


@backoff.on_exception(backoff.expo, exception=Exception, max_time=60)
def post(url: str, body: dict = None, headers: dict = None, params: dict = None, sleep: float = 0.05, timeout: float = None) -> Tuple[dict, int]:
    headers = {name: value for name, value in (headers or {}).items() if value is not None}
    params = {name: value for name, value in (params or {}).items() if value is not None}

    async def aux():
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = TCPConnector(ssl=ssl_context)

        client = ClientSession(connector=conn, timeout=ClientTimeout(timeout))

        await asyncio.sleep(sleep)

        async with client as session:
            logger.info("REST: POST %s", url)

            async with session.post(url, json=body, headers=headers, params=params) as response:
                status_code = response.status

                try:
                    json_content = await response.json()
                except ContentTypeError:
                    json_content = None

                await response.release()

            if status_code == 429:
                if "Retry-After" in response.headers:  # opensea.io
                    wait = int(response.headers["Retry-After"]) + 5
                    logger.info("too many requests, waiting for %ss", wait)
                    await asyncio.sleep(wait)
                    response.raise_for_status()
                elif json_content.get("detail") == "Request was throttled.":  # opensea.io
                    wait = 90
                else:
                    wait = 30

                logger.info("too many requests, waiting for %ss", wait)
                await asyncio.sleep(wait)
                response.raise_for_status()

            return json_content, status_code

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(aux())
    loop.close()

    return result


@backoff.on_exception(backoff.expo, exception=Exception, max_time=60)
def get_stream(
    url: str, headers: dict = None, params: dict = None, sleep: float = 0.05, timeout: float = None, check: str = None
) -> Tuple[dict, int]:
    headers = {name: value for name, value in (headers or {}).items() if value is not None}
    params = {name: value for name, value in (params or {}).items() if value is not None}

    async def aux():
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = TCPConnector(ssl=ssl_context)

        client = ClientSession(connector=conn, timeout=ClientTimeout(timeout))

        await asyncio.sleep(sleep)

        async with client as session:
            logger.info("REST: STREAM %s", url)

            async with session.get(url, headers=headers, params=params) as response:
                status_code = response.status

                try:
                    content = []

                    async for chunk in response.content:
                        content.append(json.loads(chunk.decode("utf-8")))

                    json_content = content
                except ContentTypeError:
                    json_content = None

            await response.release()

        if status_code == 429:
            if "Retry-After" in response.headers:  # opensea.io
                wait = int(response.headers["Retry-After"]) + 5
                logger.info("too many requests, waiting for %ss", wait)
                await asyncio.sleep(wait)
                response.raise_for_status()
            elif json_content.get("detail") == "Request was throttled.":  # opensea.io
                wait = 90
            else:
                wait = 30

            logger.info("too many requests, waiting for %ss", wait)
            await asyncio.sleep(wait)
            response.raise_for_status()

        if check:
            assert json_content.get(check)

        return json_content, status_code

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(aux())
    loop.close()

    return result
