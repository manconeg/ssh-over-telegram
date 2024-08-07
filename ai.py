from openai import OpenAI 
import os
import json
from client import Client
import logging

log = logging.getLogger("ai")

openAi = OpenAI(
    api_key = os.environ["openaiToken"]
)

assistant = openAi.beta.assistants.retrieve("asst_O8HrTJBPKc7Xiw87aFct8ehi")

class Ai:
    callback = False
    user_data: dict[str, str] = {}
    thread = openAi.beta.threads.create()

    def __init__(self, client: Client):
        self.client = client
        self.available_functions = {
            'send_command_to_terminal': client.send,
        }

    async def turn_into_command(self, chat: str):
        log.info (f'Got command {chat}')
	
        message = openAi.beta.threads.messages.create(
            thread_id=self.thread.id,
            role='user',
            content=chat,
        )        

        run = openAi.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=assistant.id,
            #instructions="Please address the user as Jane Doe. The user has a premium account.",
        )

        while run.status != 'completed':
            log.info(f'Run status: {run.status}')

            if run.status == 'requires_action':
                tool_outputs = []
                for tool in run.required_action.submit_tool_outputs.tool_calls:
                    log.info(f'Calling tool {tool.id}')
                    log.debug(tool)
                    function_name = tool.function.name
                    function_to_call = self.available_functions[function_name]
                    function_args = json.loads(tool.function.arguments)
                    result = await function_to_call(**function_args)

                    log.info(f'Tool responded: {result}')

                    tool_outputs.append({
                        "tool_call_id": tool.id,
                        "output": result,
                    })

                log.info(f'Sending to gpt')

                run = openAi.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=self.thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

                log.info(f'gpt received')

        messages = openAi.beta.threads.messages.list(
            thread_id=self.thread.id
        )
        log.debug(messages)
        message = messages.data[0].content[0].text.value
        log.info(message)
        return f'{self.thread.id} - {message}'
