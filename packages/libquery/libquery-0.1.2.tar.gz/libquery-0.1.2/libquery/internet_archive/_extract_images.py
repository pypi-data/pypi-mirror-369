"""
Extract images from Internet Archive.
"""

import io
import logging
import os
import shutil

from PIL import Image
from tqdm import tqdm
from zipfile import ZipFile, BadZipFile

from ._utils import get_image_uuid

logger = logging.getLogger(__name__)


def _revise_filename(filename: str) -> str:
    """
    Revised the filename from using Internet Archive identifier to using UUID.
    """

    source_name = "Internet Archive"

    extension = filename.split(".")[-1]
    uuid = get_image_uuid(filename, source_name)
    return f"{uuid}.{extension}"


def _extract_images_from_zip(file: str, img_dir: str) -> None:
    """
    Extract images from a zip file.
    The zip file is expected to contain only .jp2 or .jpg files.
    """

    try:
        with ZipFile(file, "r") as zip_ref:
            zip_paths = zip_ref.namelist()
            for zip_path in zip_paths:
                extension = os.path.splitext(zip_path)[-1]
                if extension not in {".jp2", ".jpg"}:
                    continue
                _, filename = os.path.split(zip_path)
                filename_revised = ".".join(filename.split(".")[:-1]) + ".jpg"
                filename_revised = _revise_filename(filename_revised)

                # Skip, if the file is already unzipped
                store_path = f"{img_dir}/{filename_revised}"
                if os.path.exists(store_path):
                    continue

                image_bytes = zip_ref.read(zip_path)
                img = Image.open(io.BytesIO(image_bytes))
                img.save(store_path)
    except BadZipFile:
        logger.warning("Zip file corrupted: %s", file)


def extract_images(download_dir: str, img_dir: str) -> None:
    """
    Extract the images from download directory into image directory.
    """

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    dir_names = os.listdir(download_dir)

    # Note: the directory name is the same as `idInSource`
    for dir_name in tqdm(dir_names, desc="Extract Image Progress"):
        filenames = os.listdir(f"{download_dir}/{dir_name}")

        # No file is downloaded, which may happen when the file resource is not accessible.
        if len(filenames) == 0:
            continue

        # Note: all the non-empty directory are expected to contain one file
        # that is either a zip file or an image file.
        assert len(filenames) == 1, f"Directory contains multiple files: {dir_name}"

        filename = filenames[0]
        file_path = f"{download_dir}/{dir_name}/{filename}"
        if filename.endswith(".zip"):
            _extract_images_from_zip(file_path, img_dir)
        else:
            filename_revised = _revise_filename(filename)
            shutil.copy(file_path, f"{img_dir}/{filename_revised}")
