#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup

NFM_URL = "https://www.nfm.wroclaw.pl/component/nfmcalendar"


def retrieve_links_to_all_events(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    events = {}
    for section in soup.find_all("a", class_="nfmEDTitle"):
        title = section.contents[0].strip()
        href = section["href"]
        event_id = href.split("/")[-1]
        event_url = f"{url}/event/{event_id}"
        events[event_id] = {
                "title": title,
                "url": event_url
                }
    return events


def retrieve_event_data(soup, section: str):
    string = f"{section.title()}:"
    section_tag = soup.find('div', class_="nfmArtAITitle", string=string)
    try:
        section_raw = section_tag.find_next().text.replace("***", "")
        #  TODO: try to figure out how to distinguish authors from their work
    except AttributeError:
        # AttributeError means that event's section is not yet established
        section_raw = ""
    return section_raw


def retrieve_data_about_all_events(events: dict) -> dict:
    for event in events.keys():
        event_url = nfm_events[event]["url"]
        response = requests.get(event_url)
        soup = BeautifulSoup(response.content, "html.parser")
        program = retrieve_event_data(soup, "program")
        location = retrieve_event_data(soup, "lokalizacja")
        performers = retrieve_event_data(soup, "wykonawcy")
        events[event]["program"] = program
        events[event]["performers"] = performers
        events[event]["location"] = location
    return events




nfm_events = retrieve_links_to_all_events(NFM_URL)
parsed_events = retrieve_data_about_all_events(nfm_events)


"""
TODO:
* parse over each link, and get data about Program, date, location - DONE
* confirm if this really retrieves all events
* figure out data classes for each entry/event
"""
