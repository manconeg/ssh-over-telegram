import asyncio
import sys
from ai import Ai

class Client:
    def send(self, command):
        print (command)


ai = Ai(Client())
if __name__ == "__main__":
    asyncio.run(ai.turn_into_command(' '.join(sys.argv[1:])))
