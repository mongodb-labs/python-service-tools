"""Utilities to support writing simple and concise unit tests."""

from typing import Callable, Any
from unittest.mock import patch


def relative_patch_maker(namespace: str) -> Callable[[str], Any]:
    """
    Create a namespace relative patcher.

    :param namespace: The namespace relative to which we wish to create patches.
    :return: The patch function.
    """

    def relative_patch(relative: str) -> Any:
        """
        Create a namespace relative patch.

        :param relative: The relative path to patch.
        :return: The patch.
        """
        return patch(namespace + "." + relative)

    return relative_patch
