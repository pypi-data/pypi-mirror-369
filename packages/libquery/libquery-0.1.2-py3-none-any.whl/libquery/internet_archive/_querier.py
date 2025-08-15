"""
The entrance to querier class.
"""

from ..base import BaseQuerierWithQueryReturn
from ..utils.jsonl import save_jl
from ._extract_images import extract_images
from ._fetch_metadata import (
    fetch_metadata,
    merge_deduplicate_metadata,
)
from ._fetch_file import fetch_file


class InternetArchive(BaseQuerierWithQueryReturn):
    """
    The querier for the `Internet Archive` data source.
    """

    def __init__(self, metadata_dir: str, download_dir: str, img_dir: str):
        """
        Parameters
        ----------
        metadata_path : str
            The file storing the metadata from each query.
        download_dir : str
            The directory storing the downloads from each query.
        img_dir : str
            The directory storing the images extract from downloads.
        """

        self.metadata_dir = metadata_dir
        self.download_dir = download_dir
        self.img_dir = img_dir

    def fetch_metadata(self, queries: list[str]) -> None:
        fetch_metadata(queries, self.query_return_dir, deduplicate=True)
        entries = merge_deduplicate_metadata(queries, self.query_return_dir)
        save_jl(entries, self.metadata_path)

    def fetch_image(self) -> None:
        fetch_file(self.metadata_path, self.download_dir)
        extract_images(self.download_dir, self.img_dir)
