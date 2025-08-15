"""
The base querier class.
"""

from abc import ABC, abstractmethod


class BaseQuerier(ABC):
    """The base to be inherited by all the querier classes."""

    @abstractmethod
    def fetch_metadata(self) -> None:
        """Fetch and store metadata."""

    @abstractmethod
    def fetch_image(self) -> None:
        """Fetch and store image."""


class BaseQuerierWithQueryReturn(BaseQuerier):
    """
    The base of queriers whose
    query returns are to be stored as individual JSON lines files.
    """

    def __init__(self, metadata_dir: str, img_dir: str):
        """
        Parameters
        ----------
        metadata_dir : str
            The directory storing the metadata from each query.
        img_dir : str
            The directory storing the images from each query.
        """

        self.metadata_dir = metadata_dir
        self.img_dir = img_dir

    @property
    def query_return_dir(self) -> str:
        """The directory storing the metadata from each query."""
        dirname = "query-return"
        return f"{self.metadata_dir}/{dirname}"

    @property
    def metadata_path(self) -> str:
        """The file storing the metadata from each query."""
        filename = "metadata.jsonl"
        return f"{self.metadata_dir}/{filename}"
