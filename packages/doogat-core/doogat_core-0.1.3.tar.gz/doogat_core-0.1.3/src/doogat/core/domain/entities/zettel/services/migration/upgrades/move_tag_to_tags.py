"""
This module provides functionality to manipulate metadata in :class:`ZettelData`.

Imports:
    - :class:`ZettelData` from `doogat.core.domain.value_objects.zettel_data`: Represents the data structure for Zettel metadata.
"""

from doogat.core.domain.value_objects.zettel_data import ZettelData


def move_tag_to_tags(zettel_data: ZettelData) -> None:
    """
    Move the 'tag' field from metadata to 'tags' field in :class:`ZettelData`.

    If the 'tag' field exists in the metadata, it is converted to a list (if it is a string),
    and then appended to the 'tags' field. The 'tag' field is removed afterward.

    :param zettel_data: The ZettelData object whose metadata is being modified.
    :type zettel_data: :class:`ZettelData`
    :return: None. The function modifies the `zettel_data.metadata` in place.
    :rtype: None
    """
    tag = zettel_data.metadata.get("tag")
    if tag is None:
        return

    tags = zettel_data.metadata.setdefault("tags", [])

    if isinstance(tag, str):
        tag = [tag]

    tags.extend(tag)
    del zettel_data.metadata["tag"]
