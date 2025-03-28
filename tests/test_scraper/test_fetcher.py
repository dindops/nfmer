import httpx
import pytest
from bs4 import BeautifulSoup
from pytest_httpx import HTTPXMock

from nfmer.scraper.fetcher import Fetcher, FetcherException


@pytest.fixture
def mock_html_response() -> str:
    return """
    <html>
        <body>
            <div class="test">Hi Mum!</div>
        </body>
    </html>
    """


@pytest.fixture
def mock_url() -> str:
    return "https://mock-url.com"


@pytest.mark.asyncio
async def test_fetch_soup_success(mock_html_response: str, mock_url: str, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        status_code=200,
        html=mock_html_response,
    )
    fetcher = Fetcher()
    soup = await fetcher.fetch_soup(mock_url)
    assert isinstance(soup, BeautifulSoup)
    element = soup.find("div", class_="test")
    assert element is not None
    assert element.text == "Hi Mum!"


@pytest.mark.asyncio
async def test_fetch_soup_http_error(mock_url: str, httpx_mock: HTTPXMock) -> None:
    dummy_request = httpx.Request(method="PUT", url="https://fake-confbuster-hostname")
    dummy_response = httpx.Response(status_code=418, request=dummy_request, text="I'm a teapot")
    httpx_mock.add_exception(
        httpx.HTTPStatusError("Dummy HTTPStatusError", request=dummy_request, response=dummy_response)
    )
    fetcher = Fetcher()
    with pytest.raises(FetcherException):
        await fetcher.fetch_soup(mock_url)
