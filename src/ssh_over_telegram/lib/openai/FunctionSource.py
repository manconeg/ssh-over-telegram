from abc import ABC, abstractmethod
from collections.abc import Iterable

from openai.types.beta import FunctionToolParam


class FunctionSource(ABC):
    @abstractmethod
    def functions(self) -> Iterable[FunctionToolParam]:
        pass
