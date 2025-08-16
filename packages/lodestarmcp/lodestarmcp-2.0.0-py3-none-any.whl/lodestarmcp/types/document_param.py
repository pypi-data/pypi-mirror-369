# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DocumentParam"]


class DocumentParam(TypedDict, total=False):
    num_count: Required[float]
    """Number of copies of documents that will need to be submitted.

    Only used for Release, ASsignment, and Subordination.
    """

    page_count: Required[float]
    """Number of pages needed to record the document."""

    num_grantees: float
    """Number of people recieving the grant.

    Will mostly be used for Mortgage and Release Document.
    """

    num_grantors: float
    """Number of institutions make the grant.

    Will mostly be used for Mortgage and Release Document.
    """

    num_names: float
    """Number of Names on the document. Will usually match num_grantees value."""

    num_sigs: float
    """Number of signatures on the doucment. Will usually match num_names."""
