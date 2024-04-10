import openai 
import os
import json
import queue
from client import Client

openai.api_key = os.environ["openaiToken"]

system1 = "The user will speak to the assistant and the assistant will respond with bash commands that perform the user's requested action. The complete response should be valid bash. No text that is not valid bash should be used. "
system2 = "There is no reason to explain what the commands do in English. Act as if the commands are being entered directly into a shell. "
system3 = "If files or directories are mentioned, the files should be located on the disk - their location should not be assumed. "
system4 = "Assume all directories are the current directory unless otherwise stated. Use telegram markup but do not add a preamble."
system5 = "Ask for missing API keys before executing code. Attempt to execute code immediately after recieving key."

system = system1 + system2 + system3 + system4

functions = [
        {
            "name": "send_command_to_terminal",
            "description": "Send a command to the user's terminal",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to run for the user",
                    },
                    # "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
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

class Ai:
    callback = False
    user_data: dict[str, str] = {}
    last_messages = []

    def __init__(self, client: Client):
        self.client = client
        client.callback = self.processClientMessage
        self.available_functions = {
            "send_command_to_terminal": client.send,
            "set_user_data": self.set_user_data,
        }

    async def turn_into_command(self, chat: str):
        self.messages = [ {"role": "system", "content": system} ]
        for key in self.user_data:
            self.messages.append({"role": "system", "content": f'{key}={self.user_data[key]}'})
        for message in self.last_messages:
            self.messages.append(message)
        self.messages.append({"role": "user", "content": chat})

        try:
            response = openai.ChatCompletion.create( 
                model="gpt-3.5-turbo",
                messages=self.messages,
                functions=functions
            )
        except Exception as err:
            response = {
                choices: [
                    { message: e }
                ]
            }

        response_message = response.choices[0].message

        print (f'Response {response_message}')
        self.messages.append(response_message)
        
        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_to_call = self.available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_to_call(**function_args)
        
        return response_message.content
    
    def set_user_data(self, key, value):
        self.user_data[key] = value

    async def processClientMessage(self, clientMessage):
        message = {"role": "function", "name": "send_command_to_terminal", "content": clientMessage}
        self.last_messages.append(message)
        if len(self.last_messages) > 5:
            self.last_messages.pop(0)
        self.messages.append(message)

        response = openai.ChatCompletion.create( 
            model="gpt-3.5-turbo",
            messages=self.messages
        )

        message = response.choices[0].message
        self.messages.append(response.choices[0].message)
        print (message)
        await self.callback(message.content)
