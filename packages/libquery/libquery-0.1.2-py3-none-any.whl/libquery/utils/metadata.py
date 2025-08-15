"""
Private utility functions for metadata.
"""

import os
from datetime import datetime, timezone

from dateutil import parser

from ..typing import MetadataEntry
from .jsonl import load_jl, save_jl


def deduplicate(metadata_path: str) -> None:
    """
    Deduplicate metadata.
    Load the metadata and deduplicate by `idInSource`.
    For the entries with the same `idInSource`, only keep the latest one.

    Parameters
    ----------
    metadata_path : str
        The path to the metadata to be read and edited.
    """

    entries = load_jl(metadata_path)
    id_in_source_to_entry = {}
    for d in entries:
        id_in_source = d["idInSource"]
        if id_in_source not in id_in_source_to_entry:
            id_in_source_to_entry[id_in_source] = d
            continue
        prev_access_date = parser.parse(
            id_in_source_to_entry[id_in_source]["accessDate"]
        )
        new_access_date = parser.parse(d["accessDate"])
        if new_access_date > prev_access_date:
            id_in_source_to_entry[id_in_source] = d
    save_jl(id_in_source_to_entry.values(), metadata_path)


def is_stale(entry: MetadataEntry, days_before_stale: int = 30) -> bool:
    """
    Return whether the entry is stale.

    Parameters
    ----------
    entry : MetadataEntry
        The metadata entry.
    days_before_stale : int
        The number of days to regard the data queried as stale.
    """

    now = datetime.now(timezone.utc)
    access_date = parser.parse(entry["accessDate"])
    delta = now - access_date
    return delta.days >= days_before_stale


def filter_queries(
    queries: list[str], metadata_path: str, keep_stale: bool = False
) -> list[str]:
    """
    Discard the queries that have been executed.

    Parameters
    ----------
    queries : list[str]
        The queries to be executed.
    metadata_path : str
        The path to the metadata to be read and edited.
    keep_stale : bool
        Whether to keep stale queries.
        If keep_stale = False, discard the metadata queries that have been executed
        in the recent 30 days.

    Returns
    -------
    list[str]
        The queries that have not been executed.
    """

    metadata: list[MetadataEntry] = []
    if os.path.exists(metadata_path):
        metadata = load_jl(metadata_path)

    # Regard the data queried 30 days ago as stale.
    # Stale queries will be executed again.
    queried_urls = {
        d["url"]
        for d in metadata
        if keep_stale or not is_stale(d, days_before_stale=30)
    }
    return [d for d in queries if d not in queried_urls]
