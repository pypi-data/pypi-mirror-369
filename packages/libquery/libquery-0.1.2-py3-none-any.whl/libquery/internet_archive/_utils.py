from uuid import uuid5, UUID


def get_image_uuid(filename: str, source_name: str) -> str:
    """Get the uuid of the image."""

    identifier = filename.split(".")[0]
    return str(uuid5(UUID(int=0), f"{source_name}/{identifier}"))
