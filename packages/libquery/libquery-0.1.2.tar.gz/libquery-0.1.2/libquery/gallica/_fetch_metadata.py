import json
import logging
import math
import os
import re
from datetime import datetime, timezone
from uuid import uuid5, UUID

import backoff
import requests
import xmltodict
from requests.exceptions import ProxyError, SSLError
from tqdm import tqdm
from xml.parsers.expat import ExpatError

from ..utils.jsonl import load_jl
from ..utils.metadata import filter_queries
from ._typing import Page, MetadataEntry, Record, SourceData


logger = logging.getLogger(__name__)

searched_url: list[str] = []


@backoff.on_exception(backoff.constant, ExpatError)
def _try_fetch_xml(url: str) -> dict | None:
    response = requests.get(url)

    # If the server raises error,
    # the returned XML will not be parsable.
    # Raise error to retry to query.
    if response.status_code != 200:
        raise ExpatError("Request failed with status code:", response.status_code)

    # An example query with status code 200 and empty response.text:
    # https://gallica.bnf.fr/services/Pagination?ark=cb326850921
    try:
        return xmltodict.parse(response.text)
    except ExpatError:
        return None


@backoff.on_exception(backoff.constant, KeyError)
def _fetch_num_records(base_url: str) -> int:
    """Get the number of entries found by the search url."""

    payload = _try_fetch_xml(base_url)
    n_records = payload["srw:searchRetrieveResponse"]["srw:numberOfRecords"]
    return int(n_records)


def _get_query_param(base_url: str) -> str:
    """
    Split the query parameter from the url.
    """

    query_param = base_url.split("query=")[1]
    return f"query={query_param}"


def _get_ark_identifier(identifier: str) -> str | None:
    """
    Extract the ark identifier from the url identifier.
    If the ark identifier cannot be parsed, return None.

    Examples:
    1. given 'https://gallica.bnf.fr/ark:/12148/bpt6k5619759j',
    return 'ark:/12148/bpt6k5619759j'.
    2. given 'https://gallica.bnf.fr/ark:/12148/cb32798952c/date',
    return 'ark:/12148/cb32798952c,
    """

    m = re.findall(r"ark:/12148/[a-zA-Z0-9]+", identifier)
    if len(m) != 1:
        return None
    return f"ark:/{m[0]}"


def _build_queries(template_url: str, query_return_path: str) -> list[str]:
    """
    Build a list of urls to query.
    """

    # Number of entries per page (i.e., per query).
    records_per_page = 10

    n_records = _fetch_num_records(
        template_url.format(
            startRecord=1,
            maximumRecords=records_per_page,
        )
    )
    n_pages = math.ceil(n_records / records_per_page)

    # The first entry is indexed 1 in the database.
    queries = [
        template_url.format(
            startRecord=i * records_per_page + 1,
            maximumRecords=records_per_page,
        )
        for i in range(n_pages)
    ]
    queries = [d for d in queries if d not in searched_url]
    return filter_queries(queries, query_return_path)


def _fetch_oai_record(ark: str) -> Record:
    """
    Get OAI record information given the ARK identifier.
    Example ARK identifier: 'ark:/12148/cb32798952c'.
    """

    # The service of the detailed content for a collection.
    query_term = ark.split("/")[-1]
    oai_record_url = f"https://gallica.bnf.fr/services/OAIRecord?ark={query_term}"

    # Note: the server sometimes raises internal error with response.status_code = 500.
    # We ignore such errors and let the error handler outside
    # to identify such cases and retry the query.
    payload = _try_fetch_xml(oai_record_url)
    return payload["results"]["notice"]["record"]["metadata"]["oai_dc:dc"]


def _fetch_pagination(ark: str) -> list[Page]:
    """
    Get pagination information given the ARK identifier.
    For the identifier of an image collection,
    the pagination information can be used to fetch the images.
    Example ARK identifier: 'ark:/12148/cb32798952c'.

    Parameters
    ----------
    ark : string
        The ARK identifier of a collection.

    Notes
    -----
    Using the ARK identifier to obtain image information using the BNF service may fail in the following cases:
    - The ARK identifier corresponds to a record outside Gallica, e.g., <https://bibliotheques-specialisees.paris.fr/ark:/73873/pf0000855747>.
    - In rare cases, image information of records in Gallica can not be retrieved using the API, e.g., <https://gallica.bnf.fr/ark:/12148/bc6p06xk9kk>.
    """

    # Get image page information (i.e., image list) for a collection
    query_term = ark.split("/")[-1]
    pagination_url = f"https://gallica.bnf.fr/services/Pagination?ark={query_term}"

    pagination = _try_fetch_xml(pagination_url)
    if pagination is None:
        return []

    # Note: 'livre' is the French translation of 'book'
    pages = (
        []
        if "pages" not in pagination["livre"]
        else pagination["livre"]["pages"]["page"]
    )
    if not isinstance(pages, list):
        pages = [pages]
    return pages


@backoff.on_exception(backoff.constant, KeyError)
def _fetch_identifiers(query: str) -> list[str]:
    """
    Get the identifiers of search results, given a search query.

    Example identifiers:
    https://gallica.bnf.fr/ark:/12148/btv1b530093905
    """

    payload: dict = _try_fetch_xml(query)
    records = payload["srw:searchRetrieveResponse"]["srw:records"]["srw:record"]

    if not isinstance(records, list):
        records = [records]

    identifiers = [d["srw:recordData"]["oai_dc:dc"]["dc:identifier"] for d in records]
    return [d for d in identifiers if d is not None]


def _fetch_source_data(identifier: str) -> SourceData:
    source_data = {"identifier": identifier}

    # If the identifier does not contain 'ark:/',
    # the ark identifier cannot be parsed, and the OAI record cannot be found.
    if "ark:/" not in identifier:
        return source_data

    # ARK identifier of the form 'ark:/12148/cb32798952c'.
    ark = _get_ark_identifier(identifier)
    if ark is None:
        return source_data

    source_data["record"] = _fetch_oai_record(ark)

    # If the entry is not in Gallica, its images cannot be obtained.
    if "gallica.bnf.fr/ark:/" in identifier:
        source_data["pages"] = _fetch_pagination(ark)

    return source_data


def _parse(query: str, identifier: str) -> MetadataEntry:
    """
    Parse each record, which may have more than one images.

    Example identifier:
    https://gallica.bnf.fr/ark:/12148/btv1b530093905
    """

    source_name = "Gallica"
    id_in_source = identifier
    source_data = _fetch_source_data(identifier)

    return {
        "uuid": str(uuid5(UUID(int=0), f"{source_name}/{id_in_source}")),
        "url": query,
        "source": source_name,
        "idInSource": id_in_source,
        "accessDate": datetime.now(timezone.utc).isoformat(),
        "sourceData": source_data,
    }


@backoff.on_exception(backoff.constant, (ProxyError, SSLError))
def fetch_metadata(base_urls: list[str], query_return_dir: str) -> None:
    """
    Given base url and title keywords, generate metadata queries, and store the query results.

    Parameters
    ----------
    base_urls:
        The base URLs for generating queries.
    query_return_dir:
        The path to the folder for storing the metadata files.
    """

    if not os.path.exists(query_return_dir):
        os.makedirs(query_return_dir)

    visited_id_in_source = []

    for template_url in base_urls:
        logger.info("Fetch Metadata from %s", template_url)

        query_return_path = os.path.join(
            query_return_dir,
            f"{_get_query_param(template_url)}.jsonl",
        )
        queries = _build_queries(template_url, query_return_path)

        entries = (
            [] if not os.path.exists(query_return_path) else load_jl(query_return_path)
        )
        visited_id_in_source += [d["idInSource"] for d in entries]

        with open(query_return_path, "a", encoding="utf8") as f:
            for query in tqdm(queries, desc="Progress"):
                identifiers = _fetch_identifiers(query)
                for identifier in identifiers:
                    if isinstance(identifier, list):
                        identifier = identifier[0]

                    id_in_source = identifier
                    if id_in_source in visited_id_in_source:
                        continue
                    visited_id_in_source.append(id_in_source)

                    metadata_entry = _parse(query, identifier)
                    if metadata_entry is not None:
                        f.write(f"{json.dumps(metadata_entry, ensure_ascii=False)}\n")
                searched_url.append(query)


def merge_metadata(base_urls: list[str], query_return_dir: str) -> list[MetadataEntry]:
    """
    Combine metadata files into one.
    """

    entries = []
    for base_url in base_urls:
        path = os.path.join(
            query_return_dir,
            f"{_get_query_param(base_url)}.jsonl",
        )
        if os.path.exists(path):
            entries += load_jl(path)
    return entries
