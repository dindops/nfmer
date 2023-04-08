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



nfm_events = retrieve_all_events_links(NFM_URL)

TODO:
* parse over each link, and get data about Program, date, location
* confirm if this really retrieves all events
* figure out data classes for each entry/event
'''

