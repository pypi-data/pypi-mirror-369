"""
This module contains a function to set the default publish status for a ZettelData object.

Imports:
    - :class:`ZettelData` from doogat.core.domain.value_objects.zettel_data which is used to manipulate zettel metadata.
"""

from doogat.core.domain.value_objects.zettel_data import ZettelData


def set_default_publish(zettel_data: ZettelData) -> None:
    """
    Set the default publish status of the zettel data to False.

    :param zettel_data: The ZettelData object whose publish status is to be set.
    :type zettel_data: :class:`ZettelData`
    :return: None. The function modifies the `zettel_data` in place.
    """
    zettel_data.metadata["publish"] = False
