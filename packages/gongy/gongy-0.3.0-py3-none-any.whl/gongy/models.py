"""Models."""

from __future__ import annotations

__all__: tuple[str, ...] = (
    "CallDirection",
    "CallID",
    "CallItem",
    "CallResponse",
    "CallScope",
    "CallsResponse",
    "Cursor",
    "EventID",
    "MediaType",
    "RecordsInfo",
    "RequestID",
    "StrID",
    "UserID",
    "WorkspaceID",
)


from datetime import datetime, timedelta  # noqa: TC003
from enum import Enum

from pydantic import BaseModel, ConfigDict, HttpUrl

type StrID = str

type WorkspaceID = StrID
type RequestID = StrID
type CallID = StrID
type UserID = StrID
type EventID = StrID
type Cursor = str


def to_camel(s: str) -> str:
    """snake_case -> camelCase."""
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class CallDirection(str, Enum):
    """Call direction."""

    INBOUND = "Inbound"
    OUTBOUND = "Outbound"
    CONFERENCE = "Conference"
    UNKNOWN = "Unknown"


class CallScope(str, Enum):
    """Scope of the call."""

    INTERNAL = "Internal"
    EXTERNAL = "External"
    UNKNOWN = "Unknown"


class MediaType(str, Enum):
    """Media type of the call recording."""

    VIDEO = "Video"
    AUDIO = "Audio"


class RecordsInfo(BaseModel):
    """Information about the number of records that match the requested filter."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    total_records: int
    """Total number of records."""

    current_page_size: int
    """Number of records in the current page."""

    current_page_number: int
    """Current page number."""

    cursor: Cursor | None = None
    """Pagination cursor. Returned only when there are more records to be retrieved.
    Pass this value in the next request to fetch the next page."""


class CallItem(BaseModel):
    """One call entry."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    id: CallID
    """Gong's unique numeric identifier for the call (up to 20 digits)."""

    url: HttpUrl
    """URL to the call page in the Gong web application."""

    title: str
    """The title of the call."""

    scheduled: datetime
    """Scheduled date and time of the call (ISO-8601)."""

    started: datetime
    """Date and time when the call was recorded (ISO-8601)."""

    duration: timedelta
    """Duration of the call in seconds."""

    primary_user_id: UserID
    """Primary user ID of the team member who hosted the call."""

    direction: CallDirection
    """Call direction. Allowed values: Inbound, Outbound, Conference, Unknown."""

    system: str
    """System with which the call was carried out (e.g., WebEx, ShoreTel)."""

    scope: CallScope
    """Scope of the call: 'internal', 'external', or 'unknown'."""

    media: MediaType
    """Media type. Allowed values: Video, Audio."""

    language: str
    """Language code (ISO-639-2B), e.g., 'eng', 'fre', 'spa', 'ger', 'ita'.
    Also: 'und', 'zxx'."""

    workspace_id: WorkspaceID
    """Gong's unique numeric identifier for the call's workspace (up to 20 digits)."""

    sdr_disposition: str | None = None
    """SDR disposition of the call—automatically provided or manually entered."""

    client_unique_id: StrID | None = None
    """Call's unique ID in the origin recording system."""

    custom_data: str | None = None
    """Custom metadata provided during call creation."""

    purpose: str | None = None
    """Purpose of the call."""

    meeting_url: HttpUrl | None = None
    """Meeting provider URL where the web conference was recorded."""

    is_private: bool
    """Whether the call is private."""

    calendar_event_id: EventID | None = None
    """ID of the associated Google or Outlook Calendar event."""


class CallsResponse(BaseModel):
    """Calls."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    request_id: RequestID
    """A Gong request reference ID generated for this request.
    Use for troubleshooting."""

    records: RecordsInfo
    """Information about the number of records that match the requested filter."""

    calls: list[CallItem]
    """A list in which each item specifies one call."""


class CallResponse(BaseModel):
    """Call."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    request_id: RequestID
    """A Gong request reference ID generated for this request.
    Use for troubleshooting."""

    call: CallItem
    """Call."""
