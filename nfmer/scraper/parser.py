from datetime import date, datetime

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

from nfmer.models import NFM_Event

PLACEHOLDER_DATE = date(9999, 12, 31)


class Parser:
    """Processes HTML soup of a given event, and returns filtered data"""

    def __init__(self) -> None:
        self.soup: BeautifulSoup | None = None

    def _cleanup_programme(self, programme_dict: dict[str, str]) -> dict[str, str]:
        cleaned_programme = {}
        for artist in programme_dict:
            piece = programme_dict[artist]
            piece = piece.replace("\xa0", " ")
            cleaned_programme[artist.strip()] = piece.strip()
        return cleaned_programme

    def _format_programme_section(self, programme_section: Tag) -> dict[str, str]:
        all_p_tags = programme_section.find_next_siblings("p")
        tag_list = programme_section.contents
        for p_tag in all_p_tags:
            if hasattr(p_tag, "contents"):
                tag_list += p_tag.contents
        programme_dict: dict[str, str] = {}
        current_key: str | None = None
        current_value: list[str] = []
        # TODO: implement filtering of unwanted data + extend the list
        # ignored_strings = ["<img ", "Mecenas Edukacji NFM"]

        # shenanigans to distinguish composer from their work included within
        # few <p> tags
        for item in tag_list:
            # is this a new <strong>artists</strong>?
            if isinstance(item, Tag) and item.name == "strong":
                if "<img " in item.text:
                    continue
                if "Mecenas Edukacji NFM" in item.text:
                    continue
                # TODO: - all ^^^ those weird entries in <p> tags should be handled
                # in a separate function
                if current_key is not None:
                    if "***" in current_value:  # *** is not a valid artist
                        current_value.remove("***")
                    programme_dict[current_key] = "".join(current_value)
                current_key = item.text
                if current_key in programme_dict:
                    current_value = [programme_dict[current_key], "; "]
                else:
                    current_value = []
            else:
                if hasattr(item, "text"):
                    current_value.append(item.text)
                elif isinstance(item, NavigableString):
                    current_value.append(str(item))
            if current_key is not None and current_key != "":
                programme_dict[current_key] = "".join(current_value)
        programme_dict = self._cleanup_programme(programme_dict)
        return programme_dict

    def _retrieve_event_date(self) -> date:
        if not self.soup:
            return PLACEHOLDER_DATE
        event_date_raw = self.soup.find("div", class_="nfmEDDate nfmComEvDate")
        if not event_date_raw:
            return PLACEHOLDER_DATE
        try:
            event_date_list = event_date_raw.text.strip().split(".")
            day = int(event_date_list[0])
            month = int(event_date_list[1])
            current_date = datetime.now().date()
            tentative_date = date(current_date.year, month, day)
            # NFM repertoire doesn't contain past events and each event contain
            # data only about day and month, but not the year of the event
            # If a given month already passed this year, then the event most likely
            # takes place next year
            if tentative_date < current_date:
                tentative_date = date(current_date.year + 1, month, day)
            return tentative_date
        except (AttributeError, ValueError, IndexError):
            return PLACEHOLDER_DATE

    def _retrieve_event_hour(self) -> str:
        if not self.soup:
            return "00:00:00"
        event_hour_raw = self.soup.find("div", class_="nfmEDTime nfmComEvTime")
        if not event_hour_raw:
            return "00:00:00"
        try:
            event_hour = str(event_hour_raw.text.strip())
            event_hour = f"{event_hour}:00"
        except AttributeError:
            event_hour = "00:00:00"
        return event_hour

    def _retrieve_event_location(self) -> str:
        if not self.soup:
            return ""
        event_location_raw = self.soup.find("div", class_="nfmEDLoc")
        if not event_location_raw or not hasattr(event_location_raw, "text"):
            return ""
        event_location = str(event_location_raw.text).strip()
        return event_location

    def _retrieve_event_programme(self) -> dict[str, str]:
        if not self.soup:
            return {}
        programme_container = self.soup.find("div", class_="nfmArtAddInfo")
        if not isinstance(programme_container, Tag):
            return {}
        while programme_container and hasattr(programme_container, "find"):
            title_div = programme_container.find("div", class_="nfmArtAITitle")
            if title_div and hasattr(title_div, "text") and title_div.text == "Program:":
                break
            next_container = programme_container.find_next_sibling("div", class_="nfmArtAddInfo")
            if not isinstance(next_container, Tag):
                break
            programme_container = next_container
        programme_p = programme_container.find("p")
        if not isinstance(programme_p, Tag):
            return {}
        programme = self._format_programme_section(programme_p)
        return programme

    def parse(self, url: str, soup: BeautifulSoup) -> NFM_Event | None:
        self.soup = soup
        programme = self._retrieve_event_programme()
        location = self._retrieve_event_location()
        event_date = self._retrieve_event_date()
        hour = self._retrieve_event_hour()
        parsed_event = NFM_Event(
            url=url,
            event_programme=programme,
            location=location,
            date=event_date,
            hour=hour,
        )
        return parsed_event
