"""
Fetch files from Internet Archive.
"""

import logging
import os
from os.path import isfile
from typing import TypedDict

from internetarchive import download
from requests.exceptions import ConnectTimeout, HTTPError
from tqdm import tqdm

from ..utils.jsonl import load_jl
from ._typing import MetadataEntry, SourceData


logger = logging.getLogger(__name__)


class FileQuery(TypedDict):
    filename: str
    identifier: str


def _get_filename(source_data: SourceData) -> str | None:
    files = source_data["files"]

    # 'JPEG' and 'PNG' correspond to collections of single images.
    # 'Single Page Processed JP2 ZIP' and 'Single Page Processed JPEG ZIP'
    # correspond to collections of multiple images.
    # Example of 'Single Page Processed JP2 ZIP':
    # <https://ia800500.us.archive.org/view_archive.php?archive=/25/items/essaisurlastatis00gueruoft/essaisurlastatis00gueruoft_jp2.zip>
    # Example of 'Single Page Processed JPEG ZIP':
    # <https://ia801402.us.archive.org/view_archive.php?archive=/10/items/1926981926m1931eng/1926981926m1931eng_jpg.zip>
    image_formats = [
        "JPEG",
        "PNG",
        "Single Page Processed JP2 ZIP",
        "Single Page Processed JPEG ZIP",
    ]
    image_files = [d for d in files if d["format"] in image_formats]
    if len(image_files) == 0:
        return None

    # Download the first image.
    return image_files[0]["name"]


def _build_queries(metadata: list[MetadataEntry]) -> list[FileQuery]:
    """
    Build a list of image urls to query.
    Note that internetarchive's download API already
    avoids downloading files already stored.
    """

    img_queries = []
    for d in metadata:
        source_data = d["sourceData"]
        identifier = source_data["metadata"]["identifier"]
        filename = _get_filename(source_data)
        if filename is None:
            continue
        img_queries.append(
            {
                "filename": filename,
                "identifier": identifier,
            }
        )

    return img_queries


def _filter_queries(img_queries: list[FileQuery], download_dir: str) -> list[FileQuery]:
    """
    Filter urls queried before according to the stored files.
    """

    return [
        d
        for d in img_queries
        if not isfile(f"{download_dir}/{d['identifier']}/{d['filename']}")
    ]


def fetch_file(metadata_path: str, download_dir: str) -> None:
    """
    Given base urls, generate file queries, and store the query results.

    Parameters
    ----------
    metadata_path : str
        The path to the metadata file where file urls are stored.
    download_dir : str
        The path to the folder for storing the files.
    """

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    metadata = load_jl(metadata_path)
    img_queries = _filter_queries(_build_queries(metadata), download_dir)

    for query in tqdm(img_queries, desc="Fetch File Progress"):
        try:
            download(query["identifier"], files=query["filename"], destdir=download_dir)
        except (ConnectTimeout, HTTPError) as e:
            # Internet Archive raises 403 Forbidden when item is not available.
            logger.error("Error: %s", e)
