"""
The type declarations specific to the `David Rumsey Map Collection` data source.
"""

from typing import TypedDict

from typing_extensions import NotRequired

from ..typing import MetadataEntry as _MetadataEntry

TextWithLang = TypedDict(
    "TextWithLang",
    {
        "@xml:lang": str,
        "#text": str,
    },
)

Record = TypedDict(
    "Record",
    {
        "@xmlns:dc": str,
        "@xmlns:oai_dc": str,
        "@xmlns:xsi": str,
        "@xsi:schemaLocation": str,
        "dc:identifier": str | list[str],
        "dc:relation": str | list[str],
        "dc:source": str,
        "dc:title": str | list[str | TextWithLang],
        # The author(s).
        "dc:creator": NotRequired[str | list[str]],
        "dc:date": NotRequired[str | list[str]],
        "dc:subject": NotRequired[str | TextWithLang | list[str | TextWithLang] | None],
        "dc:coverage": NotRequired[str | list[str] | None],
        "dc:format": NotRequired[str | TextWithLang | list[str | TextWithLang]],
        # For collections within the BnF, the language code has 3 characters.
        # For collections from outside, the language code can be arbitrary.
        "dc:language": NotRequired[str | list[str]],
        # Type of the document, e.g., monograph, map, image,
        # fascicle, manuscript, score, sound, object and video.
        "dc:type": NotRequired[list[str | TextWithLang]],
        "dc:rights": NotRequired[list[TextWithLang]],
        "dc:publisher": NotRequired[str | list[str]],
        "dc:description": NotRequired[str | list[str]],
        "dc:contributor": NotRequired[str | list[str]],
        "#text": NotRequired[str],
    },
)


class Page(TypedDict):
    numero: str | None
    ordre: str
    pagination_type: str | None
    image_width: str
    image_height: str
    legend: NotRequired[str]


class SourceData(TypedDict):
    identifier: str
    record: NotRequired[Record]
    pages: NotRequired[list[Page]]


class MetadataEntry(_MetadataEntry):
    """The data structure of an entry in the metadata."""

    sourceData: SourceData
