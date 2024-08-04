import asyncio
import sys
import logging
from ai import Ai

log = logging.getLogger()
logging.basicConfig()
log.setLevel(logging.INFO)

class Client:
    async def send(self, command):
        print (command)
        return ''

ai = Ai(Client())
if __name__ == '__main__':
    asyncio.run(ai.turn_into_command(' '.join(sys.argv[1:])))
