#!/usr/bin/env python

from bs4 import BeautifulSoup, Tag
from datetime import datetime
from typing import Dict
from dataclasses import dataclass, field

@dataclass
class NFM_Event:
    url: str = ""
    event_programme: Dict = field(default_factory=Dict)
    performers: str = ""
    location: str = ""
    date: str = ""


class Parser:
    ''' Processes HTML soup of a given event, and returns filtered data '''
    def __init__(self, url: str, soup: BeautifulSoup):
        self.url = url
        self.soup = soup
        self.parsed_event = ""

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
                current_value.append(item.text)
            if current_key is not None and current_key != '':
                programme_dict[current_key] = ''.join(current_value)
        programme_dict = self._clean_up_programme(programme_dict)
        return programme_dict

    def _format_artists_section(self, artists_section) -> str:
        # not gonna work on this too much, as might have to remove it in the end
        artists = ''
        for item in artists_section.contents:
            if type(item) is not Tag:
                artists += item + ', '
        artists = artists[:-2]
        return artists

    def _retrieve_event_date(self) -> str:
        # TODO currently dates don't come with a year - how to figure out from
        # which year an event is exactly? From tickets info, but this require
        # further crawling
        event_date_raw = self.soup.find('div', class_="nfmEDDate nfmComEvDate")
        try:
            event_date_list = event_date_raw.text.strip().split(".")
            event_date = f"{datetime.now().year}-{event_date_list[1]}-" \
                f"{event_date_list[0]}"
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
            elif section == "wykonawcy":
                section_raw = section_tag.find_next()
                artists = self._format_artists_section(section_raw)
                return artists
            else:
                section_raw = section_tag.find_next().text
        except AttributeError:
            # AttributeError means that event's section is not yet established
            section_raw = ""
        return section_raw

    def parse(self) -> None:
        programme = self._retrieve_section_data("program")
        location = self._retrieve_section_data("lokalizacja")
        performers = self._retrieve_section_data("wykonawcy")
        date = self._retrieve_event_date()
        hour = self._retrieve_event_hour()
        date_8601 = f"{date} {hour}"
        parsed_event = NFM_Event(
            url=self.url,
            event_programme=programme,
            performers=performers,
            location = location,
            date = date_8601
            )
        self.parsed_event = parsed_event

    @property
    def get_parsed_event(self) -> str | NFM_Event:
        return self.parsed_event
