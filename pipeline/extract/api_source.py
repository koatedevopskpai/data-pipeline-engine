# ApiSource uses httpx over the more common requests library. Decision rationale:
#
# 1. httpx supports async natively. While this pipeline is synchronous, choosing
#    httpx now means the pathway to an async pipeline (e.g., httpx.AsyncClient
#    with asyncio) doesn't require replacing the HTTP library.
# 2. httpx has a cleaner connection management model — the Client context manager
#    properly handles connection pooling and teardown.
# 3. httpx supports HTTP/2, which matters for high-throughput API sources.
#
# The timeout parameter defaults to 30 seconds. This is intentionally not hidden
# in a config file: timeout is a runtime decision based on the specific API's
# SLA, not a global pipeline setting. Different APIs have different response
# time characteristics.
#
# Like JsonSource, this normalises both list and single-object responses.
# Real REST APIs are inconsistent — some return {"data": [...]}, some return
# [...] directly. This handles both.
from collections.abc import Iterator

import httpx

from .base import SourceReader


class ApiSource(SourceReader):
    source_type = "api"

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def read(self, source: str) -> Iterator[dict]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(source)
            response.raise_for_status()
            data = response.json()
        if isinstance(data, list):
            yield from data
        else:
            yield data
