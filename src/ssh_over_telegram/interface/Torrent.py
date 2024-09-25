from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import List

from openai.types.beta import FunctionToolParam
from openai.types.shared_params import FunctionDefinition
from typing_extensions import override

from ..lib.openai.FunctionSource import FunctionSource


class TorrentResult:
    def __init__(self, torrent_hash: str, name: str, size: str, seeders: str):
        self.torrent_hash = torrent_hash
        self.name = name
        self.size = size
        self.seeders = seeders

    def to_dict(self):
        """Convert the instance to a dictionary."""
        return {
            'torrent_hash': self.torrent_hash,
            'name': self.name,
            'size': self.size,
            'seeders': self.seeders,
        }


class Torrent(FunctionSource, ABC):
    @override
    def functions(self) -> Iterable[FunctionToolParam]:
        return [
            FunctionToolParam(
                type='function',
                function=FunctionDefinition(
                    name='search',
                    description='Search for a torrent',
                    strict=True,
                    parameters={
                        'type': 'object',
                        'properties': {
                            'term': {
                                'type': 'string',
                                'description': 'Torrent search term',
                            },
                        },
                        'additionalProperties': False,
                        'required': ['term'],
                    },
                ),
            ),
            FunctionToolParam(
                type='function',
                function=FunctionDefinition(
                    name='fetch_magnet_link',
                    description='Get magnet link by previously returned torrent hash',
                    strict=True,
                    parameters={
                        'type': 'object',
                        'properties': {
                            'torrent_hash': {
                                'type': 'string',
                                'description': 'Hash of torrent returned by previous API',
                            },
                        },
                        'additionalProperties': False,
                        'required': ['torrent_hash'],
                    },
                ),
            ),
        ]

    @abstractmethod
    def search(self, search: str) -> List[TorrentResult]:
        pass

    @abstractmethod
    def fetch_magnet_link(self, torrent_hash: str) -> str:
        pass
