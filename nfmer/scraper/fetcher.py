import asyncio

import httpx
from bs4 import BeautifulSoup
from tenacity import (retry, retry_if_not_exception_type, stop_after_attempt,
                      wait_fixed)


class FetcherException(Exception):
    def __init__(
        self, message: str, method: str | None = None, error_code: int | None = None
    ):
        self.message = message
        self.method = method
        self.error_code = error_code
        super().__init__(message)


class Fetcher:
    """Takes an URL and returns a BeautifulSoup for further parsing"""

    @retry(
        retry=retry_if_not_exception_type(FetcherException),
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
    )
    async def fetch_soup(self, url: str) -> BeautifulSoup:
        async with httpx.AsyncClient() as client:
            try:
                await asyncio.sleep(1)  # pseudo rate-limiting
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.content, "html.parser")
            except httpx.HTTPStatusError as e:
                msg = (
                    f"Error response. "
                    f"URL: {e.request.url}, method: {e.request.method}, "
                    f"status: {e.response.status_code}, message: {e.response.text}"
                )
                raise FetcherException(msg, e.request.method, e.response.status_code)
