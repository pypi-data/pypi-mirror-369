import asyncio

from pWebServer import *
import pytest
import httpx

@pytest.mark.asyncio
async def test_server_start_no_routes():
    loop = asyncio.get_running_loop()
    sv = Server()
    with pytest.raises(NotImplementedError):
        await sv.start(port=14151)

@pytest.mark.asyncio
async def test_server_start_in_asyncio():
    sv = Server()
    sv.add_default_route()
    await sv.start(port=14151)


@pytest.mark.asyncio
async def test_server_start_with_client():
    sv = Server()
    sv.add_default_route()
    await sv.start(port=14151)
    # wait for create_task to complete
    await asyncio.sleep(0.25)
    async with httpx.AsyncClient() as client:
        r = await client.get('http://localhost:14151/',timeout=0.5)


def test_server_start():
    sv = Server()
    sv.add_default_route()
    loop = asyncio.get_event_loop()
    loop.create_task(sv.start(port=14151))
