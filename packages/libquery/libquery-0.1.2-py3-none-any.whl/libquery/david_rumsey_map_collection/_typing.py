"""
The type declarations specific to the `David Rumsey Map Collection` data source.
"""

from typing import Literal, TypedDict

from typing_extensions import NotRequired

from ..typing import MetadataEntry as _MetadataEntry

Fields = Literal[
    "Author",
    "Date",
    "Short Title",
    "Publisher",
    "Publisher Location",
    "Type",
    "Obj Height cm",
    "Obj Width cm",
    "Scale 1",
    "World Area",
    "Subject",
    "Full Title",
    "List No",
    "Page No",
    "Series No",
    "Publication Author",
    "Pub Date",
    "Pub Title",
    "Pub Reference",
    "Pub Note",
    "Pub List No",
    "Pub Type",
    "Pub Maps",
    "Pub Height cm",
    "Pub Width cm",
    "Image No",
    "Download 1",
    "Download 2",
    "Authors",
    "Note",
    "Reference",
    "World Area",
    "Collection",
    "Scale 1",
    "Country",
    "Engraver or Printer",
    "Region",
    "State/Province",
    "City",
    "Event",
    "County",
    "Attributed Author",
    "Attributed Publication Author",
]


class SourceData(TypedDict):
    displayName: str
    description: str
    mediaType: str
    fieldValues: list[dict[Fields, list[str]]]
    relatedFieldValues: list
    relayButtonUrl: str
    relayButtonTitle: str
    id: str
    iiifManifest: str
    urlSize0: NotRequired[str]
    urlSize1: NotRequired[str]
    urlSize2: str
    urlSize3: NotRequired[str]
    urlSize4: NotRequired[str]
    refUrlSize0: NotRequired[str]
    refUrlSize1: NotRequired[str]
    refUrlSize2: NotRequired[str]
    refUrlSize3: NotRequired[str]
    refUrlSize4: NotRequired[str]


class MetadataEntry(_MetadataEntry):
    """The data structure of an entry in the metadata."""

    sourceData: SourceData
