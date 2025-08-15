"""
Utility functions for getting metadata from David Rumsey Map Collection.
"""

import json
import logging
import os
from datetime import datetime, timezone
from uuid import uuid5, UUID

import backoff
import requests
from requests import Response
from requests.exceptions import ProxyError
from tqdm import tqdm

from ..utils.jsonl import load_jl
from ..utils.metadata import deduplicate, filter_queries
from ._typing import MetadataEntry


logger = logging.getLogger(__name__)


def _fetch_num_records(base_url: str) -> int:
    """
    Get the number of entries matching the url.
    Use the 'totalResults' attribute returned by David Rumsey Map Collection.
    """

    response = requests.get(base_url)
    data = response.json()
    return int(data["totalResults"])


def _get_query_param(base_url: str) -> str:
    """
    Split the query parameter from the url.
    """

    return base_url.split("?")[1]


def _build_queries(base_url: str, query_return_path: str) -> list[str]:
    """
    Build a list of urls to query.
    The urls already queried according to
    the stored metadata will be excluded.

    Note
    ----
    The query f'{base_url}&os={offset}&bs={n_samples}' can result in
    different return values when David Rumsey Map Collection updates,
    the deduplication may cause new images to be ignored.
    Thus, the deduplication only apply to the queried in the recent 7 days.
    """

    n_records = _fetch_num_records(base_url)
    n_samples = 1
    queries = [f"{base_url}&os={offset}&bs={n_samples}" for offset in range(n_records)]
    return filter_queries(queries, query_return_path)


def _parse(response: Response) -> MetadataEntry:
    """
    Parse metadata of entries in David Rumsey Map Collection.
    """

    data = response.json()

    assert len(data["results"]) == 1, f"length = {len(data['results'])}"

    result = data["results"][0]

    # relayButtonUrl and relayButtonTitle are useless but take much storage
    del result["relayButtonUrl"]
    del result["relayButtonTitle"]

    source = "David Rumsey Map Collection"
    id_in_source = result["id"]

    return {
        "uuid": str(uuid5(UUID(int=0), f"{source}/{id_in_source}")),
        "url": response.url,
        "source": source,
        "idInSource": id_in_source,
        "accessDate": datetime.now(timezone.utc).isoformat(),
        "sourceData": result,
    }


@backoff.on_exception(backoff.constant, ProxyError)
def fetch_metadata(base_urls: list[str], query_return_dir: str) -> None:
    """
    Given base urls, generate metadata queries, and store the query results.

    Avoid duplication with the entries
    already stored in existing metadata files.
    The duplication is checked by idInSource.

    Parameters
    ----------
    base_urls : list[str]
        The base urls for generating queries.
        Each base url corresponds to a search keyword.
    query_return_dir : str
        The path to the folder for storing the metadata files.
    """

    if not os.path.exists(query_return_dir):
        os.makedirs(query_return_dir)

    for base_url in base_urls:
        logger.info("Fetch Metadata from %s", base_url)

        query_return_path = os.path.join(
            query_return_dir,
            f"{_get_query_param(base_url)}.jsonl",
        )
        queries = _build_queries(base_url, query_return_path)

        with open(query_return_path, "a", encoding="utf-8") as f:
            for query in tqdm(queries, desc="Progress"):
                response = requests.get(query)
                metadata_entry = _parse(response)
                f.write(f"{json.dumps(metadata_entry, ensure_ascii=False)}\n")

        # For duplicate entries, only keep the latest one.
        deduplicate(query_return_path)


def merge_metadata(base_urls: list[str], query_return_dir: str) -> list[MetadataEntry]:
    """
    Merge metadata of different queries.
    Return the merge result.
    """

    entries: list[MetadataEntry] = []
    for base_url in base_urls:
        path = os.path.join(
            query_return_dir,
            f"{_get_query_param(base_url)}.jsonl",
        )
        if os.path.exists(path):
            entries += load_jl(path)
    return entries
