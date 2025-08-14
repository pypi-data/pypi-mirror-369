from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

from maggma import __version__

if TYPE_CHECKING:
    from pydantic import ValidationInfo

""" Describes the Materials API Response """


DataT = TypeVar("DataT")


class Meta(BaseModel):
    """
    Meta information for the MAPI Response.
    """

    api_version: str = Field(
        __version__,
        description="a string containing the version of the Materials API implementation, e.g. v0.9.5",
    )

    time_stamp: datetime = Field(
        description="a string containing the date and time at which the query was executed",
        default_factory=datetime.utcnow,
    )

    total_doc: int | None = Field(None, description="the total number of documents available for this query", ge=0)

    facet: dict | None = Field(
        None,
        description="a dictionary containing the facets available for this query",
    )

    class Config:
        extra = "allow"


class Error(BaseModel):
    """
    Base Error model for General API.
    """

    code: int = Field(..., description="The error code")
    message: str = Field(..., description="The description of the error")

    @classmethod
    def from_traceback(cls, traceback):
        pass


class Response(BaseModel, Generic[DataT]):
    """
    A Generic API Response.
    """

    data: list[DataT] | None = Field(None, description="List of returned data")
    errors: list[Error] | None = Field(None, description="Any errors on processing this query")
    meta: Meta | None = Field(None, description="Extra information for the query")

    @field_validator("errors", mode="before")
    def check_consistency(cls, v, values: ValidationInfo):
        if v is not None and getattr(values, "data", None) is not None:
            raise ValueError("must not provide both data and error")
        if v is None and getattr(values, "data", None) is None:
            raise ValueError("must provide data or error")
        return v

    @field_validator("meta", mode="before")
    def default_meta(cls, v, values: ValidationInfo):
        if v is None:
            v = Meta().model_dump()
        if v.get("total_doc", None) is None:
            if getattr(values, "data", None) is not None:
                v["total_doc"] = len(values.data)
            else:
                v["total_doc"] = 0
        return v


class S3URLDoc(BaseModel):
    """
    S3 pre-signed URL data returned by the S3 URL resource.
    """

    url: str = Field(
        ...,
        description="Pre-signed download URL",
    )

    requested_datetime: datetime = Field(..., description="Datetime for when URL was requested")

    expiry_datetime: datetime = Field(..., description="Expiry datetime of the URL")
