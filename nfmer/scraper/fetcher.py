from bs4 import BeautifulSoup
import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed


class Fetcher:
    ''' Takes a list of URLs and returns a dictionary with event id as a key,
    and BeautifulSoup as a value '''

    def __init__(self, concurrency: int = 10) -> None:
        self.soup_dict = {}
        self.semaphore = asyncio.Semaphore(concurrency)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry_error_callback=lambda retry_state: None
    )
    async def _fetch_soup(self, url: str) -> None:
        async with self.semaphore:
            async with httpx.AsyncClient() as client:
                await asyncio.sleep(10)  # pseudo rate-limiting
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                event_id = url.rsplit("/", 1)[-1]
                self.soup_dict[event_id] = soup

    async def fetch(self, urls: list[str]) -> None:
        tasks = [self._fetch_soup(url) for url in urls]
        await asyncio.gather(*tasks)
