from bs4 import BeautifulSoup
import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed


class Fetcher:
    ''' Takes an URL and returns a BeautifulSoup for further parsing '''

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry_error_callback=lambda retry_state: None
    )
    async def fetch_soup(self, url: str) -> BeautifulSoup:
        async with httpx.AsyncClient() as client:
            await asyncio.sleep(10)  # pseudo rate-limiting
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
