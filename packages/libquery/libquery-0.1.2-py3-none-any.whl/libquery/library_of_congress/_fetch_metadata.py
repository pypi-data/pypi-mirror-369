"""
Fetch metadata from Library of Congress.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid5, UUID

import backoff
import requests
from requests import Response
from requests.exceptions import ProxyError, SSLError
from tqdm import tqdm

from ..utils.jsonl import load_jl
from ..utils.metadata import filter_queries
from ._typing import MetadataEntry


logger = logging.getLogger(__name__)


def _fetch_num_pages(
    base_url: str, records_per_page: Literal[25, 50, 100, 150]
) -> int | None:
    """
    Get the number of found pages, given the search base url.

    Note
    ----
    Library of congress only allow records_per_page in [25, 50, 100, 150].
    """

    pagination_url = f"{base_url}&at=pagination&c={records_per_page}"
    response = requests.get(pagination_url)
    if response.status_code == 403:
        logger.warning("403 Forbidden at %s", pagination_url)
        return None
    return response.json()["pagination"]["total"]


def _build_queries(base_urls: list[str], metadata_path: str) -> list[str]:
    """
    Build a list of urls to query.
    """

    # Number of entries per page (i.e., per query).
    records_per_page = 25

    queries = []
    for base_url in base_urls:
        n_pages = _fetch_num_pages(base_url, records_per_page)
        if n_pages is None:
            continue
        # The first page is indexed 1 in the database.
        queries += [
            f"{base_url}&sp={i + 1}&c={records_per_page}" for i in range(n_pages)
        ]
    return filter_queries(queries, metadata_path)


def _parse(response: Response) -> list[MetadataEntry]:
    """
    Parse metadata of entries in Library of Congress.
    """

    data = response.json()
    if "results" not in data:
        return []

    entries: list[MetadataEntry] = []
    for result in data["results"]:
        is_image = "image_url" in result and len(result["image_url"]) >= 1
        if (not is_image) or ("item" not in result):
            continue
        source = "Library of Congress"
        id_in_source = result["id"].split("/")[-2]
        entries.append(
            {
                "uuid": str(uuid5(UUID(int=0), f"{source}/{id_in_source}")),
                "url": response.url,
                "source": source,
                "idInSource": id_in_source,
                "accessDate": datetime.now(timezone.utc).isoformat(),
                "sourceData": result,
            }
        )
    return entries


@backoff.on_exception(backoff.constant, (ProxyError, SSLError))
def fetch_metadata(base_urls: list[str], metadata_path: str) -> None:
    """
    Given base urls, generate metadata queries, and store the query results.

    Parameters
    ----------
    base_urls : list[str]
        The base urls for generating queries.
        Each base url corresponds to a search keyword.
    metadata_path : str
        The path to the folder for storing the metadata.
    """

    output_dir = os.path.dirname(metadata_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    metadata = [] if not os.path.exists(metadata_path) else load_jl(metadata_path)

    queried_view_urls = [d["sourceData"]["url"] for d in metadata]

    # TODO: store the query result of each query in an individual jsonl to:
    # 1. reduce file size
    # 2. allow deduplication in the merged jsonl without removing
    # the original queried record, which cause query progress to be lost

    # TODO: make the progress logging scheme consistent with other data sources

    # Each query queries a page with multiple entries.
    queries = _build_queries(base_urls, metadata_path)
    with open(metadata_path, "a", encoding="utf-8") as f:
        for query in tqdm(queries, desc="Fetch Metadata Progress"):
            response = requests.get(query)
            entries = _parse(response)
            for d in entries:
                if d["sourceData"]["url"] not in queried_view_urls:
                    f.write(f"{json.dumps(d, ensure_ascii=False)}\n")

    # For duplicate entries (returned by different search queries),
    # only keep the latest one.
    # from ..utils.metadata import deduplicate
    # deduplicate(metadata_path)
