"""
The entrance to querier class.
"""

from ..base import BaseQuerierWithQueryReturn
from ..typing import ImageQuery
from ..utils.image import (
    fetch as base_fetch_image,
    IncompleteFileHandler,
)
from ..utils.jsonl import save_jl
from ..utils.metadata import deduplicate
from ._fetch_metadata import fetch_metadata, merge_metadata
from ._typing import MetadataEntry
from ._utils import get_image_url, get_image_uuid


def _build_image_queries(metadata: list[MetadataEntry]) -> list[ImageQuery]:
    """Build a list of image urls to query."""

    img_queries = []
    for d in metadata:
        if "pages" not in d["sourceData"]:
            continue
        pages = d["sourceData"]["pages"]
        img_queries += [
            {
                "url": get_image_url(page, d),
                "uuid": get_image_uuid(page, d),
                # The file extension in Gallica are jpeg, and cannot be inferred
                # with mimetypes.guess_extension.
                "extension": ".jpeg",
            }
            for page in pages
        ]
    return img_queries


class Gallica(BaseQuerierWithQueryReturn):
    """
    The querier for the `Gallica` data source.
    """

    def fetch_metadata(self, queries: list[str]) -> None:
        """
        Parameters
        ----------
        queries : list[str]
            The base urls for which query results are to be stored.
        """

        fetch_metadata(queries, self.query_return_dir)
        entries = merge_metadata(queries, self.query_return_dir)
        save_jl(entries, self.metadata_path)
        deduplicate(self.metadata_path)

    def fetch_image(self) -> None:
        base_fetch_image(
            self.metadata_path,
            self.img_dir,
            _build_image_queries,
            IncompleteFileHandler.SAVE,
        )
