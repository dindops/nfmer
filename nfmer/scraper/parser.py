from bs4 import BeautifulSoup, Tag
from datetime import datetime
from typing import Dict
from dataclasses import dataclass, field


@dataclass
class NFM_Event:
    url: str = ""
    event_id: int = 69696969
    event_programme: Dict = field(default_factory=Dict)
    location: str = ""
    date: str = ""


class Parser:
    ''' Processes HTML soup of a given event, and returns filtered data '''

    def __init__(self):
        self.soup = None

    def _clean_up_programme(self, programme_dict: dict) -> Dict:
        for artist in programme_dict:
            piece = programme_dict[artist]
            piece = piece.replace(u'\xa0', u' ')
            programme_dict[artist] = piece
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
        programme_dict = self._clean_up_programme(programme_dict)
        return programme_dict

    def _retrieve_event_date(self) -> str:
        # NOTE: Event date provided on event's main page currently doesn't
        # include year of the event - this is provided on a ticketing site.
        # As crawling through additional set of urls is too much of a hassle, I'm
        # eyeballing the event's year ;)
        event_date_raw = self.soup.find('div', class_="nfmEDDate nfmComEvDate")
        try:
            event_date_list = event_date_raw.text.strip().split(".")
            day = event_date_list[0]
            month = event_date_list[1]
            current_year = int(datetime.now().year)
            event_date = f"{day}-{month}-{current_year}"
            event_date = datetime.strptime(event_date, '%d-%m-%Y').date()
            current_date = datetime.now().date()
            # no past events in repertoire -> event happens in the future
            if event_date < current_date:
                event_date = f"{day}-{month}-{current_year+1}"
            else:
                event_date = str(event_date)
        except AttributeError:
            event_date = "TBD"
        return event_date

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
        date = self._retrieve_event_date()
        hour = self._retrieve_event_hour()
        date_8601 = f"{date} {hour}"
        event_id = int(self.url.rsplit("/", 1)[-1])
        parsed_event = NFM_Event(
            url=url,
            event_programme=programme,
            location=location,
            date=date_8601
        )
        return parsed_event
