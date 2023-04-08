#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup

NFM_URL = "https://www.nfm.wroclaw.pl/component/nfmcalendar"


def retrieve_all_events_links(url):
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


def retrieve_event_program(soup):
    program_tag = soup.find('div', class_="nfmArtAITitle", string="Program:")
    try:
        program_raw = program_tag.find_next().text.replace("***", "")
        #  TODO: try to figure out how to distinguish authors from their work
    except AttributeError:
        # AttributeError means that event's program is not yet established
        program_raw = ""
    return program_raw



nfm_events = retrieve_all_events_links(NFM_URL)

for event in nfm_events.keys():
    event_url = nfm_events[event]["url"]
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    program = retrieve_event_program(soup)
    nfm_events[event]["program"] = program

TODO:
* parse over each link, and get data about Program, date, location
* confirm if this really retrieves all events
* figure out data classes for each entry/event
'''

