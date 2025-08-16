from pathlib import Path
from typing import List

from agox.analysis import SearchCollection


def test_search_collection(search_collection: SearchCollection) -> None:
    search_collection


def test_search_collection_get_searches(search_collection: SearchCollection, database_directories: List[Path]) -> None:
    searches = search_collection.get_searches()
    assert len(searches) == len(database_directories)


def test_search_collection_iter(search_collection: SearchCollection, database_directories: List[Path]) -> None:
    i = 0
    for search in search_collection:
        i += 1
    assert i == len(database_directories)


def test_search_collection_index(search_collection: SearchCollection, database_directories: List[Path]) -> None:
    for i in range(len(database_directories)):
        search = search_collection[i]
        assert search.directory == database_directories[i]
