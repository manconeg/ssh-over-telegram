from typing import List, Iterable, Dict

from openai.types.beta import FunctionToolParam
from typing_extensions import override

from ..lib.openai.FunctionSource import FunctionSource


class Aggregate(FunctionSource):
    @override
    def functions(self) -> Iterable[FunctionToolParam]:
        functions: List[FunctionToolParam] = []
        for key in self.store.keys():
            handler = self.store[key]
            for function in handler.functions():
                name = function.get('function').get('name')
                setattr(self, name, getattr(handler, name))
                functions.append(function)
        return functions

    def __init__(self):
        self.store: Dict[str, FunctionSource] = {}

    def add(self, function_source: FunctionSource):
        self.store[type(function_source).__name__] = function_source
