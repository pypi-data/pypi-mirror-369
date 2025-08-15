"""
Type declarations for collected data.
"""

from typing import Any, TypedDict

from typing_extensions import NotRequired


class MetadataEntry(TypedDict):
    """
    The data structure of an entry of metadata.

    Attributes
    ----------
    uuid : str
        The UUID of the metadata entry.
        Generate with `str(uuid5(UUID(int=0), f'{source}/{idInSource}'))`
        to make the UUID reproducible.
    url : str
        The url from which the metadata is collected.
        Either an API query or a webpage url.
    source : str
        The name of the database or data source containing the metadata.
    idInSource : str
        The unique identifier that can be used to differentiate items within the same database.
    accessDate : str
        The time (UTC+0) the entry is saved (in ISO 8601 format).
        Generate with datetime.now(timezone.utc).isoformat().
    sourceData : dict[str, Any]
        The source data directly extracted from the url.
        If the url is an API query, store the returned JSON.
        If the url is a webpage url, store the useful information extracted from the webpage.
    """

    uuid: str
    url: str
    source: str
    idInSource: str
    accessDate: str
    sourceData: dict[str, Any]


class ImageQuery(TypedDict):
    """
    The data structure of an image query.

    Attributes
    ----------
    url : str
        The url for fetching the image
    uuid : str
        The UUID of the image.
    extension: NotRequired[str]
        The file extension.
        If not given, the file extension will be
        inferred with mimetypes.guess_extension.
    """

    url: str
    uuid: str
    extension: NotRequired[str]
