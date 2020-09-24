from formation_flying.server import server
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # python-3.8.0a4

server.port = 8522
server.launch()


