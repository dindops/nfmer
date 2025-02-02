from bs4 import BeautifulSoup, Tag
from datetime import datetime
from typing import Dict
from dataclasses import dataclass, field
from datetime import date


PLACEHOLDER_DATE = date(9999, 12, 31)


@dataclass
class NFM_Event:
    url: str = ""
    event_programme: Dict = field(default_factory=Dict)
    location: str = ""
    date: date = PLACEHOLDER_DATE
    hour: str = "00:00:00"


class Parser:
    ''' Processes HTML soup of a given event, and returns filtered data '''

    def __init__(self):
        self.soup = None

    def _cleanup_programme(self, programme_dict: dict) -> Dict:
        for artist in programme_dict:
            piece = programme_dict[artist]
            piece = piece.replace(u'\xa0', u' ')
            programme_dict[artist] = piece.strip()
        return programme_dict

    def _format_programme_section(self, programme_section) -> Dict:
        all_p_tags = programme_section.find_next_siblings('p')
        tag_list = programme_section.contents
        for p_tag in all_p_tags:
            tag_list += p_tag.contents
        programme_dict = {}
        current_key = None
        current_value = []
        ignored_strings = ["<img ",
                           "Mecenas Edukacji NFM"]
        # shenanigans to distinguish composer from their work included within
        # few <p> tags
        for item in tag_list:
            # is this a new <strong>artists</strong>?
            if isinstance(item, Tag) and item.name == 'strong':
                if "<img " in item.text:
                    continue
                if "Mecenas Edukacji NFM" in item.text:
                    continue
                # TODO: - all ^^^ those weird entries in <p> tags should be handled
                # in a separate function
                if current_key is not None:
                    if '***' in current_value:  # *** is not a valid artist
                        current_value.remove('***')
                    programme_dict[current_key] = ''.join(current_value)
                current_key = item.text
                if current_key in programme_dict:
                    current_value = [programme_dict[current_key], "; "]
                else:
                    current_value = []
            else:
                current_value.append(item.text)
            if current_key is not None and current_key != '':
                programme_dict[current_key] = ''.join(current_value)
        programme_dict = self._cleanup_programme(programme_dict)
        return programme_dict

    def _retrieve_event_date(self) -> date:
        event_date_raw = self.soup.find('div', class_="nfmEDDate nfmComEvDate")
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
        event_hour_raw = self.soup.find('div', class_="nfmEDTime nfmComEvTime")
        try:
            event_hour = event_hour_raw.text.strip()
            event_hour = f"{event_hour}:00"
        except AttributeError:
            event_hour = "00:00:00"
        return event_hour

    def _retrieve_section_data(self, section: str) -> Dict | str:
        string = f"{section.title()}:"
        section_tag = self.soup.find('div', class_="nfmArtAITitle", string=string)
        try:
            if section == "program":
                section_raw = section_tag.find_next()
                programme = self._format_programme_section(section_raw)
                return programme
            else:
                section_raw = section_tag.find_next().text
        except AttributeError:
            # AttributeError means that event's section is not yet established
            section_raw = ""
        return section_raw

    def parse(self, url: str, soup: BeautifulSoup) -> NFM_Event | None:
        self.soup = soup
        programme = self._retrieve_section_data("program")
        location = self._retrieve_section_data("lokalizacja")
        event_date = self._retrieve_event_date()
        hour = self._retrieve_event_hour()
        parsed_event = NFM_Event(
            url=url,
            event_programme=programme,
            location=location,
            date=event_date,
            hour=hour
        )
        return parsed_event
