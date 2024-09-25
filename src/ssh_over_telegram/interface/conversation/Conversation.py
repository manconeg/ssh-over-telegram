from abc import ABC, abstractmethod


class Conversation(ABC):

    @abstractmethod
    async def send(self, message: str) -> None:
        pass
