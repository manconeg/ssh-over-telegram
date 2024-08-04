from openai import OpenAI 
import os
import json
import queue
import time
from client import Client
import logging

log = logging.getLogger("ai")

client = OpenAI(
    api_key = os.environ["openaiToken"]
)

#system1 = "The user will speak to the assistant and the assistant will respond with bash commands that perform the user's requested action. The complete response should be valid bash. No text that is not valid bash should be used. "
#system2 = "There is no reason to explain what the commands do in English. Act as if the commands are being entered directly into a shell. "
#system3 = "If files or directories are mentioned, the files should be located on the disk - their location should not be assumed. "
#system4 = "Assume all directories are the current directory unless otherwise stated. Use telegram markup but do not add a preamble."
#system5 = "Ask for missing API keys before executing code. Attempt to execute code immediately after recieving key."

#system = system1 + system2 + system3 + system4

systemPrompt = [
    "You are inbetween the user and their terminal - they tell you what thye would like to do on their remote system and you turn it into valid bash commands and send the command to the terminal.",
    "You must ask the user for clarification if necessary.",
    "Inavlid bash commands should never be sent to the terminal.",
    "If a command is invalid due to the requirement of an API key, you must ask the user",
    "Assume only commonly available utilities",
    "Do not send any placeholder values to the terminal, such as API_KEY",
]

system = " ".join(systemPrompt)

log.debug(system)

functions = [
        {
            "type": "function",
            "function": {
                "name": "send_command_to_terminal",
                "description": "Send a command to the user's terminal",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to run for the user",
                        },
                    },
                    "required": ["command"],
                },
            }
        },
        # {
        #     "name": "set_user_data",
        #     "description": "Set some data about the user",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "key": {
        #                 "type": "string",
        #                 "description": "the name of the data being set",
        #             },
        #             "value": {
        #                 "type": "string",
        #                 "description": "the value of the data",
        #             }
        #             # "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        #         },
        #         "required": ["location"],
        #     },
        # }
    ]

assistant = client.beta.assistants.create(
    instructions = system,
    model = "gpt-3.5-turbo",
    tools = functions,
)

thread = client.beta.threads.create()

class Ai:
    callback = False
    user_data: dict[str, str] = {}

    def __init__(self, client: Client):
        self.client = client
        self.available_functions = {
            "set_user_data": self.set_user_data,
        }
        self.available_functions["send_command_to_terminal"] = client.send

    async def turn_into_command(self, chat: str):
        log.info (f'Got command {chat}')
	
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=chat,
        )        

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            #instructions="Please address the user as Jane Doe. The user has a premium account.",
        )

        while (run.status != 'completed' and run.status != 'requires_action'):
            log.info(run.status)
            time.sleep(1)

        if run.status == 'requires_action':
            for tool in run.required_action.submit_tool_outputs.tool_calls:
                log.info("Calling tool)
                log.debug(tool)
                function_name = tool.function.name
                function_to_call = self.available_functions[function_name]
                function_args = json.loads(tool.function.arguments)
                result = function_to_call(**function_args)

                tool_outputs = []
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": result,
                })

                run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
        
        if run.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            log.debug(messages)
            message = messages.data[0].content[0].text.value
            log.info(message)

    def set_user_data(self, key, value):
        self.user_data[key] = value
