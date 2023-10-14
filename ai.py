import openai 
import os

openai.api_key = os.environ["openaiToken"]

system1 = "The user will speak to the assistant and the assistant will respond with bash commands that perform the user's requested action. The complete response should be valid bash. No text that is not valid bash should be used. "
system2 = "There is no reason to explain what the commands do in English. Act as if the commands are being entered directly into a shell. "
system3 = "If files or directories are mentioned, the files should be located on the disk - their location should not be assumed. "
system4 = "NEVER reply using invalid bash commands."

system = system1 + system2 + system3 + system4


class Ai:
    messages = [ {"role": "system", "content": system} ]

    def turn_into_command(self, chat: str):
        self.messages.append( 
                {"role": "user", "content": chat}, 
            )

        response = openai.ChatCompletion.create( 
                model="gpt-3.5-turbo", messages=self.messages 
            )

        command = response.choices[0].message.content

        self.messages.append({"role": "assistant", "content": command})

        return command
    
    def add_result(self, result: str):
        self.messages.append( 
                {"role": "system", "content": result}, 
            )