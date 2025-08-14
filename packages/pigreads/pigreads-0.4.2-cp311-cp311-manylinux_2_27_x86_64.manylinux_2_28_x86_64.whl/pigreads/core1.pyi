"""
Type annotations for single-precision implementation
----------------------------------------------------
"""

from __future__ import annotations

from pigreads.core import Models

# pylint: disable=abstract-method

class Models1(Models):
    """
    Single-precision implementation of the ``Models`` class.

    :see: :py:class:`pigreads.Models` for the main interface to the models.
    """

__all__ = ["Models1"]
