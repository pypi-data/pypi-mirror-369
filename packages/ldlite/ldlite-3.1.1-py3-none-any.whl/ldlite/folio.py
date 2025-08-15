"""Utilities for connecting to FOLIO."""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import count
from typing import TYPE_CHECKING

import httpx
import orjson
from httpx_retries import Retry, RetryTransport

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator


@dataclass(frozen=True)
class FolioParams:
    """Connection parameters for FOLIO.

    base_url and tenant can be found in Settings > Software versions.
    """

    """The service url for FOLIO."""
    base_url: str
    """The FOLIO tenant. ECS setups are not currently supported."""
    tenant: str
    """The user to query FOLIO. LDlite will have the same permissions as this user."""
    username: str
    """The user's FOLIO password."""
    password: str


class _RefreshTokenAuth(httpx.Auth):
    def __init__(self, params: FolioParams):
        self._params = params
        self._hdr = _RefreshTokenAuth._do_auth(self._params)

    def auth_flow(
        self,
        request: httpx.Request,
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers.update(self._hdr)
        response = yield request

        if response.status_code == 401:
            self._hdr = _RefreshTokenAuth._do_auth(self._params)
            request.headers.update(self._hdr)
            yield request

    @staticmethod
    def _do_auth(params: FolioParams) -> dict[str, str]:
        hdr = {"x-okapi-tenant": params.tenant}
        res = httpx.post(
            params.base_url.rstrip("/") + "/authn/login-with-expiry",
            headers=hdr,
            json={
                "username": params.username,
                "password": params.password,
            },
        )
        res.raise_for_status()

        hdr["x-okapi-token"] = res.cookies["folioAccessToken"]
        return hdr


class _QueryParams:
    _default_re = re.compile(
        r"^cql\.allrecords(?:=1)?(?:\s+sortby\s+id(?:(?:\/|\s)+(?:sort\.)?(asc|desc))?)?$",
        re.IGNORECASE,
    )
    _without_sort_re = re.compile(
        r"^(.*?)(?:\s+sortby.*)?$",
        re.IGNORECASE,
    )

    def __init__(
        self,
        query: str | dict[str, str] | None,
        page_size: int,
    ):
        if isinstance(query, dict):
            q = None
            if "query" in query:
                q = query["query"]
                del query["query"]
            self.additional_params = query
            query = q
        else:
            self.additional_params = {}

        if query is None or self._default_re.match(query) is not None:
            # See below for papering over sort desc notes
            self.query_str = None
        else:
            self.query_str = query

        if (
            self.query_str is not None
            and (without_sort := self._without_sort_re.match(self.query_str))
            is not None
            and len(without_sort.groups()) > 0
        ):
            # We're dumping any sort the user did supply
            # This might get weird if the user is relying on
            # both a desc query and a limit on the result set
            # I'm gambling that this isn't happening
            self.query_str = without_sort.groups()[0]

        self._page_size = page_size

    def for_stats(self) -> httpx.QueryParams:
        q = self.query_str if self.query_str is not None else "cql.allRecords=1"
        return httpx.QueryParams(
            {
                **self.additional_params,
                "query": q,
                "limit": 1,
                # ERM endpoints use perPage and stats
                # Additional filtering for ERM endpoints is ignored
                # (for now because stats doesn't actually impact behavior)
                "perPage": 1,
                "stats": True,
            },
        )

    def for_values(self, last_id: str | None = None) -> httpx.QueryParams:
        if last_id is None:
            last_id = "00000000-0000-0000-0000-000000000000"
        iter_query = f"id>{last_id}"
        q = iter_query + (
            f" and ({self.query_str})" if self.query_str is not None else ""
        )
        # Additional filtering beyond ids for ERM endpoints is ignored
        return httpx.QueryParams(
            {
                **self.additional_params,
                "sort": "id;asc",
                "filters": iter_query,
                "query": q + " sortBy id",
                "limit": str(self._page_size),
                "perPage": str(self._page_size),
                "stats": True,
            },
        )

    def for_values_offset(self, sort_key: str, page: int) -> httpx.QueryParams:
        # ERM endpoints all have ids
        return httpx.QueryParams(
            {
                **self.additional_params,
                "query": (self.query_str or "cql.allRecords=1")
                + f' sortBy "{sort_key}"',
                "offset": str(page * self._page_size),
                "limit": str(self._page_size),
            },
        )


class FolioClient:
    """Client for reliably and performantly fetching FOLIO records."""

    def __init__(self, params: FolioParams):
        """Initializes and tests the Folio connection."""
        self._base_url = params.base_url.rstrip("/")
        self._auth = _RefreshTokenAuth(params)

    def iterate_records(
        self,
        path: str,
        timeout: float,
        retries: int,
        page_size: int,
        query: str | dict[str, str] | None = None,
    ) -> Iterator[tuple[int, str | bytes]]:
        """Iterates all records for a given path.

        Returns:
            A tuple of the autoincrementing key + the json for each record.
            The first result will be the total record count.
        """
        is_srs = path.startswith("/source-storage")
        # this is Java's max size of int because we want all the source records
        params = _QueryParams(query, 2_147_483_647 - 1 if is_srs else page_size)

        with httpx.Client(
            base_url=self._base_url,
            auth=self._auth,
            transport=RetryTransport(retry=Retry(total=retries, backoff_factor=0.5)),
            timeout=timeout,
        ) as client:
            res = client.get(
                # Hardcode the source storage endpoint that returns stats
                # even if the user passes in the stream endpoint
                path if not is_srs else "/source-storage/source-records",
                params=params.for_stats(),
            )
            res.raise_for_status()
            j = orjson.loads(res.text)
            r = int(j["totalRecords"])
            yield (r, b"")

            if r == 0:
                return

            pkey = count(start=1)
            if is_srs:
                # this is a more stable endpoint for srs
                # we want it to be transparent so if the user wants srs we just use it
                with client.stream(
                    "GET",
                    "/source-storage/stream/source-records",
                    params=params.for_values(),
                ) as res:
                    res.raise_for_status()
                    record = ""
                    for f in res.iter_lines():
                        # FOLIO can return partial json fragments
                        # if they contain "newline-ish" characters like U+2028
                        record += f
                        if f[-1] == "}":
                            yield (next(pkey), record)
                            record = ""
                            continue
                    return

            key = next(iter(j.keys()))
            sort_key = (
                None
                # If there's an id or we'll use id paging
                if "id" in j[key][0]
                # Otherwise we have to fall back to offet paging sorted by the first key
                else next(iter(j[key][0].keys()))
            )

            last_id: str | None = None
            page = count(start=0)
            while True:
                res = client.get(
                    path,
                    params=params.for_values(last_id)
                    if sort_key is None
                    else params.for_values_offset(sort_key, next(page)),
                )
                res.raise_for_status()

                last = None
                for r in (o for o in orjson.loads(res.text)[key] if o is not None):
                    last = r
                    yield (next(pkey), orjson.dumps(r))

                if last is None:
                    return

                last_id = last.get(
                    "id",
                    "this value is unused because we're offset paging",
                )
