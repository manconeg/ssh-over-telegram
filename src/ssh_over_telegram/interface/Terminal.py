from abc import ABC, abstractmethod
from collections.abc import Iterable

from openai.types.beta import FunctionToolParam
from openai.types.shared_params import FunctionDefinition
from typing_extensions import override

from ..lib.openai.FunctionSource import FunctionSource


class Terminal(FunctionSource, ABC):
    @override
    def functions(self) -> Iterable[FunctionToolParam]:
        return [
            FunctionToolParam(
                type='function',
                function=FunctionDefinition(
                    name='send',
                    description='Send a command to the user\'s terminal',
                    strict=True,
                    parameters={
                        'type': 'object',
                        'properties': {
                            'command': {
                                'type': 'string',
                                'description': 'The bash command to run for the user',
                            },
                        },
                        'additionalProperties': False,
                        'required': ['command'],
                    },
                ),
            ),
        ]

    @abstractmethod
    async def send(self, message: str) -> str:
        pass
