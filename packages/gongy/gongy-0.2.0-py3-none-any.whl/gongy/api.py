"""Gong API."""

from __future__ import annotations

__all__: tuple[str, ...] = ("Gongy",)

from typing import TYPE_CHECKING

from aiohttp import ClientSession
from pydantic import BaseModel, ConfigDict, Field
from yarl import URL

from gongy.models import CallsResponse
from gongy.utils.web import (
    AuthMiddleware,
    ErrorMiddleware,
    RateLimitMiddleware,
)

if TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime
    from types import TracebackType
    from typing import Self

    from gongy.models import Cursor, WorkspaceID


class Gongy(BaseModel):
    """Gong API client."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    api_key: str
    secret: str

    retries: int = Field(default=3, gt=0)
    delay: float = Field(default=1.0, gt=0)

    base_url: URL = URL("https://api.gong.io")

    raw_session: ClientSession | None = Field(default=None, init=False)

    @property
    def session(self) -> ClientSession:
        """Get the aiohttp session."""
        if self.raw_session is None:
            msg = (
                f"Session not initialized. "
                f"Use 'async with {self.__class__.__name__}(...) as gong:'"
            )
            raise RuntimeError(msg)
        return self.raw_session

    async def __aenter__(self) -> Self:
        """Enter the async context."""
        self.raw_session = ClientSession(
            middlewares=(
                AuthMiddleware(api_key=self.api_key, secret=self.secret),
                ErrorMiddleware(),
                RateLimitMiddleware(retries=self.retries, default_delay=self.delay),
            )
        )
        await self.session.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context."""
        await self.session.__aexit__(exc_type, exc_val, exc_tb)
        self.raw_session = None

    @property
    def v2(self) -> URL:
        """Get the v2 API URL."""
        return self.base_url / "v2"

    async def get_calls(
        self,
        start: datetime,
        end: datetime,
        workspace: WorkspaceID | None = None,
        cursor: Cursor | None = None,
    ) -> CallsResponse:
        """Get calls from the Gong API."""
        url = self.v2 / "calls"
        params = {
            "fromDateTime": start.isoformat(),
            "toDateTime": end.isoformat(),
        }
        if workspace is not None:
            params["workspaceId"] = workspace
        if cursor is not None:
            params["cursor"] = cursor
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return CallsResponse.model_validate(data)
