import sys, asyncio
import random
if sys.version_info[0]==3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from Backups.CNP1_all_files.server import server


server.port = random.randrange(8506, 9000)
server.launch()


