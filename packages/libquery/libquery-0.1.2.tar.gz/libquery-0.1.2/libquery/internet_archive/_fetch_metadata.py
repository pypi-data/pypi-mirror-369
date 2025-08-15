"""
Utility functions for getting metadata from David Rumsey Map Collection.
"""

import logging
import os
import json
from datetime import datetime, timezone
from uuid import uuid5, UUID

import backoff
import internetarchive
from requests.exceptions import ProxyError
from slugify import slugify
from tqdm import tqdm

from ..utils.jsonl import load_jl
from ._typing import MetadataEntry

logger = logging.getLogger(__name__)

fields = [
    "avg_rating",
    "backup_location",
    "btih",
    "call_number",
    "collection",
    "contributor",
    "coverage",
    "creator",
    "date",
    "description",
    "downloads",
    "external-identifier",
    "foldoutcount",
    "format",
    "genre",
    "identifier",
    "imagecount",
    "indexflag",
    "item_size",
    "language",
    "licenseurl",
    "mediatype",
    "members",
    "month",
    "name",
    "noindex",
    "num_reviews",
    "oai_updatedate",
    "publicdate",
    "publisher",
    "related-external-id",
    "reviewdate",
    "rights",
    "scanningcentre",
    "source",
    "stripped_tags",
    "subject",
    "title",
    "type",
    "volume",
    "week",
    "year",
]


def _parse(search_result: dict, query: str) -> MetadataEntry:
    """
    Parse metadata of entries in Internet Archive.
    """

    source_data = search_result.item_metadata
    source = "Internet Archive"
    id_in_source = source_data["metadata"]["identifier"]

    return {
        "uuid": str(uuid5(UUID(int=0), f"{source}/{id_in_source}")),
        "url": f"https://archive.org/search?query={query}",
        "source": source,
        "idInSource": id_in_source,
        "accessDate": datetime.now(timezone.utc).isoformat(),
        "sourceData": source_data,
    }


@backoff.on_exception(backoff.constant, ProxyError)
def fetch_metadata(
    queries: list[str], query_return_dir: str, deduplicate: bool = True
) -> None:
    """
    Given the search queries, and store the query results.

    Parameters
    ----------
    queries : list[str]
        The search queries.
    query_return_dir : str
        The path to the folder for storing the metadata files.
    deduplicate : boolean, default = True
        Whether to avoid duplication with the entries
        already stored in existing metadata files.
        The duplication is checked by idInSource.
    """

    if not os.path.exists(query_return_dir):
        os.makedirs(query_return_dir)

    for query in queries:
        logger.info("Fetch Metadata from %s", query)

        query_return_path = f"{query_return_dir}/{slugify(query)}.jsonl"
        search_results = internetarchive.search_items(query, fields=fields)

        if deduplicate:
            entries = (
                []
                if not os.path.exists(query_return_path)
                else load_jl(query_return_path)
            )
            visited_id_in_source = {d["idInSource"] for d in entries}

        with open(query_return_path, "a", encoding="utf-8") as f:
            for d in tqdm(search_results.iter_as_items(), desc="Progress"):
                entry = _parse(d, query)
                if not deduplicate or entry["idInSource"] not in visited_id_in_source:
                    f.write(f"{json.dumps(entry)}\n")


def merge_deduplicate_metadata(
    queries: list[str], query_return_dir: str
) -> tuple[list, int]:
    """
    Merge metadata of different queries
    and deduplicate the metadata entries by idInSource.
    For duplicate entries, one is kept and the others are removed.
    Return the merge result and number of duplicates.

    TODO: check whether this function should be kept,
    or it should be replaced with _utils.metadata.deduplicate.
    """

    entries: list[MetadataEntry] = []

    for query in queries:
        query_return_path = f"{query_return_dir}/{slugify(query)}.jsonl"
        if os.path.exists(query_return_path):
            entries += load_jl(query_return_path)

    # Build the mapping from idInSource to index.
    id2index = {}
    for i, entry in enumerate(entries):
        if entry["idInSource"] not in id2index:
            id2index[entry["idInSource"]] = i

    selected_indices = list(id2index.values())
    entries_filtered = [entries[i] for i in selected_indices]
    return entries_filtered
