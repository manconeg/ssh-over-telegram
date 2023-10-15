import openai 
import os
import json
from client import Client

openai.api_key = os.environ["openaiToken"]

system1 = "The user will speak to the assistant and the assistant will respond with bash commands that perform the user's requested action. The complete response should be valid bash. No text that is not valid bash should be used. "
system2 = "There is no reason to explain what the commands do in English. Act as if the commands are being entered directly into a shell. "
system3 = "If files or directories are mentioned, the files should be located on the disk - their location should not be assumed. "
system4 = "NEVER reply using invalid bash commands."

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
        }
    ]

class Ai:
    messages = [ {"role": "system", "content": system} ]

    def __init__(self, client: Client, callback):
        self.client = client
        self.callback = callback
        self.client.callback = self.add_result
        self.available_functions = {
            "send_command_to_terminal": client.send,
        }

    def turn_into_command(self, chat: str):
        self.messages.append( 
                {"role": "user", "content": chat}, 
            )

        response = openai.ChatCompletion.create( 
            model="gpt-3.5-turbo",
            messages=self.messages,
            functions=functions
        )

        response_message = response.choices[0].message

        print (f'Response {response_message}')
        self.messages.append(response_message)
        
        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_to_call = self.available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_to_call(function_args.get("command"))
    
    async def add_result(self, result: str):
        self.messages.append( 
                {"role": "system", "content": result}, 
            )
        await self.callback(result)