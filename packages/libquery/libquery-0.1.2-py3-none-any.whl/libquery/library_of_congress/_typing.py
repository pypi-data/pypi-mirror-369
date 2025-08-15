"""
The type declarations specific to the `Internet Archive` data source.

See reference on the response data structure at
<https://www.loc.gov/apis/json-and-yaml/responses/item-and-resource/>
"""

from typing import Any, TypedDict

from typing_extensions import NotRequired

from ..typing import MetadataEntry as _MetadataEntry


class RelatedItem(TypedDict):
    title: str
    url: str


class Creator(TypedDict):
    link: str
    role: str
    title: str


class Format(TypedDict):
    link: str
    title: str


class Item(TypedDict):
    created_published: NotRequired[str | list[str]]
    digital_id: NotRequired[list[str]]
    format: NotRequired[str | list[str]]
    language: NotRequired[str | list[str]]
    notes: NotRequired[list[str]]
    repository: NotRequired[str | list[str]]
    title: NotRequired[str]
    date: NotRequired[str]
    location: NotRequired[list[str]]
    medium: NotRequired[list[str]]
    other_title: NotRequired[list[str]]
    source_collection: NotRequired[str | list[str]]
    subjects: NotRequired[list[str]]
    translated_title: NotRequired[list[str]]
    call_number: NotRequired[str | list[str]]
    contributors: NotRequired[list[str]]
    number_former_id: NotRequired[list[str]]
    contents: NotRequired[str | list[str]]
    creator: NotRequired[str]
    genre: NotRequired[list[str]]
    summary: NotRequired[str | list[str]]
    rights: NotRequired[str]
    reproduction_number: NotRequired[str | list[str]]
    access_advisory: NotRequired[str | list[str]]
    related_items: NotRequired[list[RelatedItem]]
    rights_advisory: NotRequired[str | list[str]]
    control_number: NotRequired[str]
    created: NotRequired[str]
    created_published_date: NotRequired[str]
    creators: NotRequired[list[Creator]]
    display_offsite: NotRequired[bool]
    formats: NotRequired[list[Format]]
    id: NotRequired[str]
    link: NotRequired[str]
    marc: NotRequired[str]
    medium_brief: NotRequired[str]
    mediums: NotRequired[list[str]]
    modified: NotRequired[str]
    resource_links: NotRequired[list[str]]
    rights_information: NotRequired[str]
    service_low: NotRequired[str]
    service_medium: NotRequired[str]
    sort_date: NotRequired[str]
    source_created: NotRequired[str]
    source_modified: NotRequired[str]
    stmt_of_responsibility: NotRequired[str]
    subject_headings: NotRequired[list[str]]
    thumb_gallery: NotRequired[str]


class Resource(TypedDict):
    # The number of files.
    files: NotRequired[int]
    # The image URL.
    image: NotRequired[str]
    # The metadata query URL.
    search: NotRequired[str]
    segments: NotRequired[int]
    # The collection entry URL on loc.gov.
    url: NotRequired[str]
    caption: NotRequired[str]
    captions: NotRequired[str | int]
    zip: NotRequired[str]
    pdf: NotRequired[str]
    representative_index: NotRequired[int]
    djvu_text_file: NotRequired[str]
    fulltext_derivative: NotRequired[str]
    fulltext_file: NotRequired[str]
    paprika_resource_path: NotRequired[str]
    version: NotRequired[int]


class Segment(TypedDict):
    count: int
    link: str
    url: str


class Related(TypedDict):
    neighbors: str
    group_record: NotRequired[str]


class SourceData(TypedDict):
    access_restricted: bool
    # Alternative identifiers for documents (e.g., shortcut urls).
    aka: list[str]
    campaigns: list[Any]
    digitized: bool
    # Timestamp of most recent ETL (extract-transform-load)
    # process that produced this item. In ISO 8601 format, UTC.
    extract_timestamp: str
    # The ETL processes that produced this item.
    # For many items, different attributes are contributed by different ETL processes.
    group: list[str]
    # Whether this item has segmented data
    # (pages, bounding boxes of images, audio segmentation, etc.) in the index.
    hassegments: bool
    # HTTP version of the URL for the item, including its identifier. Always appears.
    id: str
    # URLs for images in various sizes, if available.
    # If the item is not something that has an image
    # (e.g. it's a book that's not digitized or an exhibit),
    # the URL for the image might be for an icon image file.
    image_url: list[str]
    index: int
    # The item attribute of the item response object provides
    # subfields with information for display of the item on the loc.gov website.
    item: Item
    # Formats available for download.
    mime_type: list[str]
    # Format available via the website.
    online_format: list[str]
    # The kind of object being described (not the digitized version).
    original_format: list[str]
    # Alternative language titles and other alternative titles.
    other_title: list[str]
    # Collections, divisions, units in the Library of Congress,
    # or any of a number of less formal groupings and subgroupings used for organizing content.
    partof: list[str]
    resources: list[Resource]
    # The primary sorting field of the item record.
    # This field really only has meaning within loc.gov, and is not a canonical identifier.
    shelf_id: str
    timestamp: str
    title: str
    # URL on the loc.gov website.
    # If the items is something in the library catalog,
    # the URL will start with lccn.loc.gov.
    url: str
    date: NotRequired[str]
    dates: NotRequired[list[str]]
    description: NotRequired[list[str]]
    language: NotRequired[list[str]]
    location: NotRequired[list[str]]
    number: NotRequired[list[str]]
    number_source_modified: NotRequired[list[str]]
    number_related_items: NotRequired[list[str]]
    segments: NotRequired[list[Segment]]
    site: NotRequired[list[str]]
    number_lccn: NotRequired[list[str]]
    subject: NotRequired[list[str]]
    contributor: NotRequired[list[str]]
    location_country: NotRequired[list[str]]
    location_county: NotRequired[list[str]]
    location_state: NotRequired[list[str]]
    location_city: NotRequired[list[str]]
    number_former_id: NotRequired[list[str]]
    number_carrier_type: NotRequired[list[str]]
    number_oclc: NotRequired[list[str]]
    type: NotRequired[list[str]]
    related: NotRequired[Related]
    reproductions: NotRequired[str]
    unrestricted: NotRequired[bool]
    publication_frequency: NotRequired[list[str]]


class MetadataEntry(_MetadataEntry):
    """The data structure of an entry in the metadata."""

    sourceData: SourceData
