from collections import OrderedDict
from dataclasses import dataclass, field
from typing import List, Dict, Optional

import requests
from dataclass_wizard import JSONWizard
from typing_extensions import override

from ...interface.Torrent import Torrent, TorrentResult

# The API endpoint
url = "http://localhost:8009/api/v1"


@dataclass
class TorrentSearchResult(JSONWizard):
    name: str
    size: str
    date: str
    seeders: str
    leechers: str
    url: str
    uploader: str
    category: str
    files: List[str]
    magnet: str
    hash: str
    screenshot: List[str] = field(default_factory=list)


@dataclass
class TorrentSearchResults(JSONWizard):
    data: List[TorrentSearchResult]
    current_page: int
    time: float
    total: int


class FIFOQueue:
    def __init__(self, limit=100):
        self.queue = OrderedDict[str, TorrentSearchResult]()
        self.limit = limit

    def add(self, key: str, value: TorrentSearchResult):
        if key in self.queue:
            del self.queue[key]  # Remove existing item
        elif len(self.queue) >= self.limit:
            self.queue.popitem(last=False)  # Remove oldest item
        self.queue[key] = value  # Add new item

    def get(self, key) -> TorrentSearchResult:
        return self.queue.get(key)


class TorrentSearch(Torrent):
    def __init__(self):
        self.store = FIFOQueue()

    @override
    async def search(self, term: str) -> List[Dict]:
        search = f'{url}/search?site=1337x&query={term}&limit=10'
        # A GET request to the API
        response = requests.get(search)

        results = TorrentSearchResults.from_dict(response.json())
        print(results)
        return list(map(self.map, results.data))

    @override
    async def fetch_magnet_link(self, torrent_hash: str) -> str:
        return self.store.get(torrent_hash).magnet

    def map(self, torrent_file: TorrentSearchResult):
        self.store.add(torrent_file.hash, torrent_file)
        return TorrentResult(
            torrent_hash=torrent_file.hash,
            name=torrent_file.name,
            size=torrent_file.size,
            seeders=torrent_file.seeders,
        ).to_dict()
