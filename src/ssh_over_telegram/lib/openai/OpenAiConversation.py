import logging

from openai import AsyncOpenAI
from openai.types.beta import Assistant, Thread
from openai.types.beta.threads import Run, Text
from openai.types.beta.threads.run_create_params import AdditionalMessage
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput
from typing_extensions import List, override

from .EventHandler import EventHandler
from .FunctionSource import FunctionSource
from ...interface.conversation.Conversation import Conversation
from ...interface.conversation.ConversationManager import TextCallback

log = logging.getLogger("thread")


class OpenAiConversation(Conversation):
    def __init__(
            self,
            openai: AsyncOpenAI,
            assistant: Assistant,
            function_src: FunctionSource,
            callback: TextCallback,
            thread: Thread,
    ):
        self.openai = openai
        self.assistant = assistant
        self.callback = callback
        self.function_src = function_src
        self.thread = thread

    async def chat_response(self, text: Text):
        log.info(f"assistant > {text.value}")
        await self.callback(text.value)

    async def tool_response(self, run: Run, tool_output: List[ToolOutput]):
        log.info(f"tools > {tool_output}")
        async with self.openai.beta.threads.runs.submit_tool_outputs_stream(
            run_id=run.id,
            thread_id=self.thread.id,
            event_handler=EventHandler(
                text_callback=self.chat_response,
                tool_callback=self.tool_response,
                function_src=self.function_src,
            ),
            tool_outputs=tool_output,
        ) as stream:
            await stream.until_done()

    @override
    async def send(self, content: str) -> None:
        log.info(f"user > {content}")
        async with self.openai.beta.threads.runs.stream(
            assistant_id=self.assistant.id,
            thread_id=self.thread.id,
            event_handler=EventHandler(
                text_callback=self.chat_response,
                tool_callback=self.tool_response,
                function_src=self.function_src,
            ),
            tools=self.function_src.functions(),
            additional_messages=[
                AdditionalMessage(
                    role='user',
                    content=content,
                ),
            ],
        ) as stream:
            await stream.until_done()
