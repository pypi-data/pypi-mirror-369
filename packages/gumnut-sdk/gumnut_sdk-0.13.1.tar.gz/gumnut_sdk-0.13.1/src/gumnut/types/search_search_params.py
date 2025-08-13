# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SearchSearchParams"]


class SearchSearchParams(TypedDict, total=False):
    captured_after: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter to only include assets captured after this date (ISO format)."""

    captured_before: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter to only include assets captured before this date (ISO format)."""

    limit: int
    """Number of results per page"""

    page: int
    """Page number"""

    person_ids: List[str]
    """Filter to only include assets containing ALL of these person IDs.

    Can be comma-delimited string (e.g., 'person_123,person_abc') or multiple query
    parameters.
    """

    query: Optional[str]
    """The text query to search for"""

    threshold: float
    """Similarity threshold (lower means more similar)"""
