import json
import logging
from json import JSONDecodeError
from typing import Callable, Coroutine

from openai import AsyncAssistantEventHandler
from openai.types.beta.threads import Text, Run
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput
from openai.types.beta.threads.runs import ToolCall, RunStep
from typing_extensions import override, List

from ...lib.openai.FunctionSource import FunctionSource

TextCallback = Callable[[Text], Coroutine]

ToolOutputCallback = Callable[[Run, List[ToolOutput]], Coroutine]

log = logging.getLogger("event_handler")


class EventHandler(AsyncAssistantEventHandler):
    def __init__(self, text_callback: TextCallback, tool_callback: ToolOutputCallback, function_src: FunctionSource):
        super().__init__()
        self.text_callback = text_callback
        self.tool_callback = tool_callback
        self.function_src = function_src
        self.tool_outputs: List[ToolOutput] = []

    @override
    async def on_end(self) -> None:
        log.info("end")
        if self.tool_outputs:
            log.info(f"Sending {len(self.tool_outputs)} tool outputs")
            await self.tool_callback(self.current_run, self.tool_outputs)

    @override
    async def on_run_step_done(self, run_step: RunStep) -> None:
        log.info("run step done")

    @override
    async def on_text_done(self, text: Text):
        await self.text_callback(text)

    @override
    async def on_tool_call_done(self, tool_call: ToolCall):
        try:
            function_args = json.loads(tool_call.function.arguments)
        except JSONDecodeError:
            return

        output = json.dumps(await getattr(self.function_src, tool_call.function.name)(**function_args))

        self.tool_outputs.append(ToolOutput(
            output=output,
            tool_call_id=tool_call.id,
        ))
