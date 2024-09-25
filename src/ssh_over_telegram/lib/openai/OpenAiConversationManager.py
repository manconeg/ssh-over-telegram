import logging
import os

from openai import AsyncOpenAI
from typing_extensions import override

from ...interface.conversation.Conversation import Conversation
from ...interface.conversation.ConversationManager import ConversationManager, TextCallback
from ...lib.openai.OpenAiConversation import OpenAiConversation

openai = AsyncOpenAI(
    api_key=os.environ["openaiToken"]
)

assistant_id = "asst_O8HrTJBPKc7Xiw87aFct8ehi"

log = logging.getLogger("ai")


class OpenAiConversationManager(ConversationManager):
    def __init__(self, function_src):
        self.function_src = function_src

    @override
    async def load_thread(self, callback: TextCallback, thread_id: str) -> Conversation:
        thread = await openai.beta.threads.retrieve(
            thread_id=thread_id,
        )

        assistant = await openai.beta.assistants.retrieve(
            assistant_id=assistant_id,
        )

        return OpenAiConversation(
            openai=openai,
            assistant=assistant,
            thread=thread,
            function_src=self.function_src,
            callback=callback,
        )

    @override
    async def create_thread(self, callback: TextCallback) -> Conversation:
        thread = await openai.beta.threads.create()

        assistant = await openai.beta.assistants.retrieve(
            assistant_id=assistant_id,
        )

        return OpenAiConversation(
            openai=openai,
            assistant=assistant,
            thread=thread,
            function_src=self.function_src,
            callback=callback,
        )
