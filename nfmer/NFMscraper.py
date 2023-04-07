#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup

url = 'https://www.nfm.wroclaw.pl/component/nfmcalendar'
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')

events = {}

for section in soup.find_all('a', class_='nfmEDTitle'):
    title = section.contents[0].strip()
    href = section['href']
    event_id = href.split('/')[-1]
    event_url = f"{url}/event/{event_id}"
    events[event_id] = {
            'title': title,
            'url': event_url
            }

'''
TODO:
* parse over each link, and get data about Program, date, location
* confirm if this really retrieves all events
* figure out data classes for each entry/event
'''

