import asyncio
import logging
import sys

from .interface.Aggregate import Aggregate
from .lib.local.LocalTerminal import LocalTerminal
from .lib.openai.OpenAiConversationManager import OpenAiConversationManager
from .lib.torrent.TorrentSearch import TorrentSearch

log = logging.getLogger()
logging.basicConfig()
log.setLevel(logging.INFO)


async def output(result: str):
    print(result)


def main():
    asyncio.run(run())


async def run():
    aggregate = Aggregate()
    aggregate.add(LocalTerminal())
    aggregate.add(TorrentSearch())
    thread = await OpenAiConversationManager(aggregate).create_thread(output)

    await thread.send(' '.join(sys.argv[1:]))
