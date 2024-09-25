from abc import ABC, abstractmethod
from typing import Coroutine

from typing_extensions import Callable

from ...interface.conversation.Conversation import Conversation

TextCallback = Callable[[str], Coroutine]


class ConversationManager(ABC):

    @abstractmethod
    def load_thread(self, callback: TextCallback, thread_id: str) -> Conversation:
        pass

    @abstractmethod
    def create_thread(self, callback: TextCallback) -> Conversation:
        pass
