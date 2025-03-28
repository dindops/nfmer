from datetime import date

import pytest
from bs4 import BeautifulSoup

from nfmer.scraper.parser import PLACEHOLDER_DATE, Parser


@pytest.fixture
def mock_event_url() -> str:
    return "https://example.com/event/123"


@pytest.fixture
def mock_soup() -> BeautifulSoup:
    sample_event_html = """
    <div class="nfmEDLoc">dummy location</div>
    <div class="nfmEDDate nfmComEvDate">06.12</div>
    <div class="nfmEDTime nfmComEvTime">19:00</div>
    <div class="nfmArtAddInfo"><div class="nfmArtAITitle">Program:</div>
    <p><strong>dummy artist1 </strong> dummy song1 <br/>
    <strong> dummy artist2</strong><em>dummy song2 </em></p>
"""
    return BeautifulSoup(sample_event_html, "html.parser")


@pytest.fixture
def parser() -> Parser:
    return Parser()


def test_parse_event_basic_info(mock_event_url: str, parser: Parser, mock_soup: BeautifulSoup) -> None:
    event = parser.parse(mock_event_url, mock_soup)
    assert event is not None
    assert event.location == "dummy location"
    assert event.date == date(2025, 12, 6)  # TODO: add dynamically adjusted year in the test
    assert event.hour == "19:00:00"


def test_parse_event_programme(mock_event_url: str, parser: Parser, mock_soup: BeautifulSoup) -> None:
    event = parser.parse(mock_event_url, mock_soup)
    assert event is not None
    assert event.event_programme["dummy artist1"] == "dummy song1"
    assert event.event_programme["dummy artist2"] == "dummy song2"


def test_parse_event_with_attribute_errors(mock_event_url: str, parser: Parser) -> None:
    mock_html = """
    <html> I'm a dummy html page </html>
    """
    event = parser.parse(mock_event_url, BeautifulSoup(mock_html, "html.parser"))
    assert event is not None
    assert len(event.event_programme) == 0
    assert event.date == PLACEHOLDER_DATE
    assert event.hour == "00:00:00"
