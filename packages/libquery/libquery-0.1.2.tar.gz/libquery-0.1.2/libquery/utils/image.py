"""
Fetch images from the urls stored in metadata.
"""

import logging
import mimetypes
import os
from enum import Enum
from os import listdir, remove
from os.path import isfile, join
from time import sleep
from typing import Callable

import backoff
import requests
from backoff.types import Details
from requests.exceptions import ChunkedEncodingError, ProxyError, SSLError
from tqdm import tqdm

from ..typing import ImageQuery, MetadataEntry
from .jsonl import load_jl


logger = logging.getLogger(__name__)


def _filename2uuid(filename: str) -> str:
    return filename.split(".")[0]


def _try_remove_image(img_dir: str, uuid: str) -> bool:
    """Try removing an image given uuid."""

    filenames = os.listdir(img_dir)
    filename = next((d for d in filenames if _filename2uuid(d) == uuid), None)
    if filename is None:
        return False

    file_path = os.path.join(img_dir, filename)
    if not os.path.isfile(file_path):
        return False

    remove(file_path)
    return True


def filter_queries(img_queries: list[ImageQuery], img_dir: str) -> list[ImageQuery]:
    """
    Filter urls queried before according to the stored images.
    """

    filenames = [d for d in listdir(img_dir) if isfile(join(img_dir, d))]
    img_uuids = {_filename2uuid(d) for d in filenames}
    return [d for d in img_queries if d["uuid"] not in img_uuids]


class IncompleteFileHandler(Enum):
    """The type of handlers when incomplete file is received."""

    # Raise error when incomplete file is received.
    RAISE_ERROR = 1
    # Do not save the incomplete file and do not raise error.
    IGNORE = 2
    # Save the incomplete file and do not raise error.
    SAVE = 3


last_uuid = None


def _backoff_handler(details: Details) -> None:
    logger.warning("Error occurred. Retry fetching the images: %s", details)

    if last_uuid is None:
        return

    img_dir = (
        details["args"][1]
        if "img_dir" not in details["kwargs"]
        else details["kwargs"]["img_dir"]
    )
    is_removed = _try_remove_image(img_dir, last_uuid)
    if is_removed:
        logger.info("Removed incomplete image: %s", last_uuid)


@backoff.on_exception(
    backoff.constant,
    (ChunkedEncodingError, ProxyError, SSLError),
    on_backoff=_backoff_handler,
)
def fetch(
    metadata_path: str,
    img_dir: str,
    _build_queries: Callable[[list[MetadataEntry]], list[ImageQuery]],
    incomplete_file_handler: IncompleteFileHandler = IncompleteFileHandler.RAISE_ERROR,
) -> None:
    """
    Given base urls, generate image queries, and store the query results.

    Parameters
    ----------
    metadata_path : str
        The path to the metadata file where image urls are stored.
    img_dir : str
        The path to the folder for storing the image files.
    """

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    s = requests.Session()

    metadata = load_jl(metadata_path)
    img_queries = filter_queries(_build_queries(metadata), img_dir)

    for query in tqdm(img_queries, desc="Fetch Image Progress"):
        uuid = query["uuid"]
        global last_uuid
        last_uuid = uuid

        # Note: some database may continuously raise error for a certain resource.
        # It is necessary to ignore such resources instead of keep fetching repeatedly.
        response = None
        try:
            response = s.get(query["url"])
        except SSLError as e:
            logger.error("SSL Error: %s", e)

        if response is None:
            continue

        # 403 Forbidden
        if response.status_code == 403:
            continue

        # 429 Too Many Requests
        if response.status_code == 429:
            sleep(300)
            continue

        # 500 Internal Server Error
        if response.status_code == 500:
            continue

        # 503 Service Unavailable
        if response.status_code == 503:
            continue

        extension = (
            query["extension"]
            if "extension" in query
            else mimetypes.guess_extension(response.headers["content-type"])
        )

        # In some cases, the extension may not be set.
        # For example, when the response is a plain text string.
        if extension is None:
            continue

        # If the file is not fully returned, which may frequently happen for large images.
        # Note: there is no guarantee that the server will set the correct content-length.
        # For example, Gallica often returns incorrect 'content-length' even if the image is correctly returned.
        if "content-length" in response.headers and len(response.content) != int(
            response.headers["content-length"]
        ):
            logger.warning(
                "Status code %d - File not fully returned for url = %s: %d != %s",
                response.status_code,
                query["url"],
                len(response.content),
                response.headers["content-length"],
            )
            if incomplete_file_handler == IncompleteFileHandler.RAISE_ERROR:
                raise ProxyError()
            elif incomplete_file_handler == IncompleteFileHandler.IGNORE:
                continue
            elif incomplete_file_handler == IncompleteFileHandler.SAVE:
                pass

        with open(f"{img_dir}/{uuid}{extension}", "wb") as f:
            f.write(response.content)
