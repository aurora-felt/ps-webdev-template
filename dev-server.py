import io
import aiohttp
from aiohttp import web
import asyncio
from watchfiles import awatch
import subprocess

# change these to whatever
hostName = "localhost"
serverPort = 8080

async def index_handler(_):
    return web.Response(text=io.open("index.html","r").read(),content_type="text/html")

async def index_js_handler(_):
    return web.Response(text=io.open("index.js","r").read(),content_type="text/javascript")

CLIENTS = set()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    CLIENTS.add(ws)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())
            CLIENTS.remove(ws)
    return ws

async def watch_recompile():
   async for _ in awatch("./src"):
       subprocess.run(["spago","bundle-app","-y"])
       await broadcast("reload")

async def broadcast(message):
    for websocket in CLIENTS.copy():
        try:
            await websocket.send_str(message)
        except:
            CLIENTS.remove(websocket)

def create_runner():
    app = web.Application()
    app.add_routes([
        web.get('/',   index_handler),
        web.get('/index.js', index_js_handler),
        web.get('/ws', websocket_handler),
    ])
    return web.AppRunner(app)

async def start_server(host=hostName, port=serverPort):
    print("Server started http://%s:%s" % (hostName, serverPort))
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())
    loop.run_until_complete(watch_recompile())
    loop.run_forever()

