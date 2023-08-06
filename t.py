import asyncio
from aiohttp import web

async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    print('Request served!')
    return web.Response(text=text)

async def run_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle),
                    web.get('/{name}', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

async def run_other_task():
    while True:
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.create_task(run_web_server())
loop.run_until_complete(run_other_task())
loop.run_forever()