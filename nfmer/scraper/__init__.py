from bs4 import BeautifulSoup
import httpx
import asyncio
from nfmer.scraper import Scraper

NFM_URL = "https://www.nfm.wroclaw.pl/component/nfmcalendar"


def retrieve_events_urls(url: str) -> list[str]:
    response = httpx.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    events_urls = []
    for section in soup.find_all("a", class_="nfmEDTitle"):
        href = section["href"]
        event_id = href.split("/")[-1]
        event_url = f"{url}/event/{event_id}"
        events_urls.append(event_url)
    return events_urls


async def main():
    nfm_events_urls = retrieve_events_urls(NFM_URL)
    scraper = Scraper(*nfm_events_urls)
    await scraper.scrape()
    nfm_events = scraper.event_soup
    print(nfm_events)

if __name__ == "__main__":
    asyncio.run(main())


"""
TODO:
* confirm if this really retrieves all events
* figure out data classes for each entry/event
* perhaps the output should be in a json format?
"""
