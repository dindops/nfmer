from datetime import date
from typing import Optional, Type
from unittest.mock import AsyncMock

import pytest
from bs4 import BeautifulSoup
from pytest_httpx import HTTPXMock
from pytest_mock import MockerFixture

from nfmer.db_handler import DatabaseHandler
from nfmer.models import NFM_Event
from nfmer.scraper import (
    Scraper,
    ScraperException,
    run_scraper,
)
from nfmer.scraper.fetcher import Fetcher, FetcherException
from nfmer.scraper.parser import Parser


@pytest.fixture
def mock_url() -> str:
    return "https://fake-url.com/events"


@pytest.fixture
def mock_html_response() -> str:
    return """
    <html>
        <body>
            <div class="nfmEventHeader">
                <a class="nfmEDTitle" href="/event/1">Event 1</a>
                <a class="nfmEDTitle" href="/event/2">Event 2</a>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def mock_event_data() -> NFM_Event:
    return NFM_Event(
        url="https://fake-url.com/events/event/1",
        event_programme={"Fake artist": "baby shark"},
        location="fake place",
        date=date(2011, 11, 11),
        hour="21:37:00",
    )


async def test_scraper_initialise_success(
    mock_url: str,
    mock_html_response: str,
    mocker: MockerFixture,
) -> None:
    mock_parser = mocker.Mock()
    mock_fetcher = AsyncMock()
    mock_fetcher.fetch_soup = AsyncMock(return_value=BeautifulSoup(mock_html_response, "html.parser"))
    scraper = await Scraper.initialise(mock_fetcher, mock_parser, mock_url)
    expected_events_dict = {
        "1": "https://fake-url.com/events/event/1",
        "2": "https://fake-url.com/events/event/2",
    }
    assert scraper.events_dict == expected_events_dict
    scraped_events = await scraper.scrape()
    assert len(scraped_events) == 2


async def test_scraper_initialise_fetcher_error(mock_url: str, httpx_mock: HTTPXMock, mocker: MockerFixture) -> None:
    mock_fetcher = mocker.AsyncMock()
    mock_fetcher.fetch_soup = AsyncMock(side_effect=FetcherException("I'm a fake error"))
    mock_parser = mocker.Mock()
    with pytest.raises(ScraperException):
        await Scraper.initialise(mock_fetcher, mock_parser, mock_url)


@pytest.mark.parametrize(
    "parsed_event,exception",
    [
        (
            NFM_Event(
                url="https://fake-url.com/events/event/1",
                event_programme={"Fake artist": "baby shark"},
                location="fake place",
                date=date(2011, 11, 11),
                hour="21:37:00",
            ),
            None,
        ),
        (None, FetcherException),
        (None, Exception),
    ],
)
async def test_scraper_scrape(
    mock_url: str, mocker: MockerFixture, parsed_event: Optional[NFM_Event], exception: Optional[Type[Exception]]
) -> None:
    mock_parser = mocker.Mock()
    mock_parser.parse.return_value = parsed_event
    mocked_html_response = """
    <html>
        <body>
            <div class="nfmEventHeader">
                <a class="nfmEDTitle" href="/event/1">Event 1</a>
            </div>
        </body>
    </html>
    """
    mock_fetcher = AsyncMock()
    mock_fetcher.fetch_soup = AsyncMock(return_value=BeautifulSoup(mocked_html_response, "html.parser"))
    scraper = await Scraper.initialise(mock_fetcher, mock_parser, mock_url)
    if exception:
        mock_fetcher.fetch_soup = AsyncMock(side_effect=exception("I'm a fake error"))
    scraped_events = await scraper.scrape()
    first_event = scraped_events.get("1")
    if not exception:
        assert isinstance(first_event, NFM_Event)
        assert first_event.event_programme == {"Fake artist": "baby shark"}
        assert first_event.location == "fake place"
    else:
        assert first_event is None


async def test_run_scraper(mocker: MockerFixture) -> None:
    mock_parser = mocker.Mock(spec=Parser)
    mock_fetcher = AsyncMock(spec=Fetcher)
    mock_db_handler = mocker.Mock(spec=DatabaseHandler)
    mocker.patch("nfmer.scraper.Parser", return_value=mock_parser)
    mocker.patch("nfmer.scraper.Fetcher", return_value=mock_fetcher)
    mocker.patch("nfmer.scraper.DatabaseHandler", return_value=mock_db_handler)
    mock_scraped_events = {"1": mock_event_data}
    mock_scraper = AsyncMock(spec=Scraper)
    mock_scraper.scrape = AsyncMock(return_value=mock_scraped_events)
    mock_initialise = mocker.patch(
        "nfmer.scraper.Scraper.initialise",
        new_callable=mocker.AsyncMock,
        return_value=mock_scraper,
    )
    await run_scraper()
    mock_initialise.assert_called_once_with(mock_fetcher, mock_parser)
    mock_scraper.scrape.assert_called_once()
    mock_db_handler.save_event_data.assert_called_once_with(mock_scraped_events)
