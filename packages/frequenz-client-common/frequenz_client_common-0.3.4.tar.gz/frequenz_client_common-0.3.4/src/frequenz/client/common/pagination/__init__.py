# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Module to define the pagination used with the common client."""

from __future__ import annotations  # required for constructor type hinting

from dataclasses import dataclass
from typing import Self

# pylint: disable=no-name-in-module
from frequenz.api.common.v1.pagination.pagination_info_pb2 import PaginationInfo
from frequenz.api.common.v1.pagination.pagination_params_pb2 import PaginationParams

# pylint: enable=no-name-in-module


@dataclass(frozen=True, kw_only=True)
class Params:
    """Parameters for paginating list requests."""

    page_size: int
    """The maximum number of results to be returned per request."""

    page_token: str
    """The token identifying a specific page of the list results."""

    @classmethod
    def from_proto(cls, pagination_params: PaginationParams) -> Self:
        """Convert a protobuf Params to PaginationParams object.

        Args:
            pagination_params: Params to convert.
        Returns:
            Params object corresponding to the protobuf message.
        """
        return cls(
            page_size=pagination_params.page_size,
            page_token=pagination_params.page_token,
        )

    def to_proto(self) -> PaginationParams:
        """Convert a Params object to protobuf PaginationParams.

        Returns:
            Protobuf message corresponding to the Params object.
        """
        return PaginationParams(
            page_size=self.page_size,
            page_token=self.page_token,
        )


@dataclass(frozen=True, kw_only=True)
class Info:
    """Information about the pagination of a list request."""

    total_items: int
    """The total number of items that match the request."""

    next_page_token: str | None = None
    """The token identifying the next page of results."""

    @classmethod
    def from_proto(cls, pagination_info: PaginationInfo) -> Self:
        """Convert a protobuf PBPaginationInfo to Info object.

        Args:
            pagination_info: Info to convert.
        Returns:
            Info object corresponding to the protobuf message.
        """
        return cls(
            total_items=pagination_info.total_items,
            next_page_token=pagination_info.next_page_token,
        )

    def to_proto(self) -> PaginationInfo:
        """Convert a Info object to protobuf PBPaginationInfo.

        Returns:
            Protobuf message corresponding to the Info object.
        """
        return PaginationInfo(
            total_items=self.total_items,
            next_page_token=self.next_page_token,
        )
