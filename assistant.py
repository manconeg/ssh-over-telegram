import logging

systemPrompt = [
    'You are inbetween the user and their terminal - they tell you what thye would like to do on their remote system and you turn it into valid bash commands and send the command to the terminal.',
    'You will show the user the result of the command. In the case of some sort of markup, you may make it human readable. Otherwise do not omit information from the response.',
    'You must ask the user for clarification if necessary.',
    'Invalid bash commands should never be sent to the terminal.',
    'If a command is invalid due to the requirement of an API key, you must ask the user',
    'Assume only commonly available utilities',
    'Do not send any placeholder values to the terminal, such as API_KEY',
]

system = ' '.join(systemPrompt)

log.debug(system)

functions = [
    # {
    #     'name': 'set_user_data',
    #     'description': 'Set some data about the user',
    #     'parameters': {
    #         'type': 'object',
    #         'properties': {
    #             'key': {
    #                 'type': 'string',
    #                 'description': 'the name of the data being set',
    #             },
    #             'value': {
    #                 'type': 'string',
    #                 'description': 'the value of the data',
    #             }
    #             # 'unit': {'type': 'string', 'enum': ['celsius', 'fahrenheit']},
    #         },
    #         'required': ['location'],
    #     },
    # }
]

# assistant = client.beta.assistants.create(
#     instructions = system,
#     model = 'gpt-3.5-turbo',
#     tools = functions,
# )