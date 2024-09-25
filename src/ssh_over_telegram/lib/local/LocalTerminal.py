import logging

from typing_extensions import override

from ...interface.Terminal import Terminal

log = logging.getLogger("localterminal")


class LocalTerminal(Terminal):
    @override
    async def send(self, command) -> str:
        log.info(f"executing: {command}")
        return 'files: home dev lib etc'
