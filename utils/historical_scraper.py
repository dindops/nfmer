import asyncio
from asyncio import Semaphore

from loguru import logger

from nfmer.db_handler import DatabaseHandler
from nfmer.models import NFM_Event
from nfmer.scraper.fetcher import Fetcher, FetcherException
from nfmer.scraper.parser import Parser

NFM_URL = "https://www.nfm.wroclaw.pl/en/component/nfmcalendar"


class HistoricalScraper:
    def __init__(self, fetcher: Fetcher, parser: Parser, main_url: str, max_concurrent: int = 10):
        self.fetcher = fetcher
        self.parser = parser
        self.main_url = main_url
        self.semaphore = Semaphore(max_concurrent)

    async def get_starting_event_id(self) -> int:
        soup = await self.fetcher.fetch_soup(self.main_url)
        min_id = float('inf')
        for section in soup.find_all("a", class_="nfmEDTitle"):
            if not section.has_attr("href"):
                continue
            href_value = section["href"]
            if not isinstance(href_value, str):
                continue
            event_id = href_value.split("/")[-1]
            try:
                event_id_int = int(event_id)
                if event_id_int < min_id:
                    min_id = event_id_int
            except ValueError:
                continue
        return int(min_id)

    async def scrape_single_event(self, event_id: int) -> tuple[str, NFM_Event | None]:
        async with self.semaphore:
            event_url = f"{self.main_url}/event/{event_id}"
            try:
                event_soup = await self.fetcher.fetch_soup(event_url)
                return str(event_id), self.parser.parse(event_url, event_soup)
            except FetcherException:
                return str(event_id), None
            except Exception:
                return str(event_id), None

    async def scrape_chunk(self, event_ids: list[int]) -> dict[str, NFM_Event]:
        tasks = [self.scrape_single_event(event_id) for event_id in event_ids]
        results = {}
        for event_id, data in await asyncio.gather(*tasks):
            if data is not None:
                results[event_id] = data
        return results


async def run_historical_scraper(
    db_path: str = "sqlite:///historical_events.db",
    chunk_size: int = 100
) -> None:
    fetcher = Fetcher()
    parser = Parser()
    scraper = HistoricalScraper(fetcher, parser, NFM_URL)
    db_handler = DatabaseHandler(db_path)

    logger.info("Detecting starting event ID from main page...")
    start_id = await scraper.get_starting_event_id()
    logger.info(f"Starting from event ID: {start_id}")
    logger.info(f"Scraping events from {start_id} down to 1 in chunks of {chunk_size}...")

    total_events = start_id
    total_saved = 0
    events_processed = 0

    for chunk_start in range(start_id, 0, -chunk_size):
        chunk_end = max(chunk_start - chunk_size + 1, 1)
        event_ids = list(range(chunk_start, chunk_end - 1, -1))

        logger.info(f"Scraping chunk: events {chunk_start} to {chunk_end} ({len(event_ids)} events)")
        scraped_events = await scraper.scrape_chunk(event_ids)

        if scraped_events:
            logger.info(f"Scraped {len(scraped_events)} valid events, saving to database...")
            db_handler.save_event_data(scraped_events)
            total_saved += len(scraped_events)
        else:
            logger.debug("No valid events in this chunk")

        events_processed += len(event_ids)
        logger.info(f"Progress: {events_processed}/{total_events} events processed, {total_saved} saved to DB")

    logger.success(f"Historical scraping completed! Total events saved: {total_saved}")


def main() -> None:
    asyncio.run(run_historical_scraper())


if __name__ == "__main__":
    main()
