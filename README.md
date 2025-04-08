# NFMer - a better way to search through a NFM repertoire

## Why?
This is first and foremost a non-profit learning project!

I'm a fan of live music and I love my local philharmonic venue, the NFM
(National Forum of Music in Wrocław, Poland). I've always struggled when I
searched through their repertoire, as, until very recently, it was impossible
to search for events based on the compositions that are being played, rather
than the performer or the conductor. While I appreciate our local
philharmonic's programming strategy emphasizing contemporary performers and
conductors rather than focusing solely on original composers, I find myself
drawn more to the compositions themselves. As a novice listener, I'm still
developing the ability to discern the subtle nuances that different performers
and conductors bring to these centuries-old works. Their artistic
interpretation certainly adds value, but at my current stage of appreciation,
I'm primarily seeking to hear the compositions in their foundational form.
Live. Preferably as soon as possible, without the need to go over each event
and manually checking what exactly is going to be played.


I also wanted to build something with FastAPI, try out SQLModel and finally learn basics of Django.


## How to:
### Requirements:
This project consists of a `scraper`, `api` and a `webapp`. The following list of requirements is valid for the whole project:
* Makefile
* Python 3.11+
* poetry
* sqlite3

### Run scraper:
```bash
make scrape
```
This will create a local sqlite3 database named `events.db` and feed it with all the scraped data. If `events.db` exists, it will attempt to update it.

### Run API locally:
``` bash
make api-run
```
This starts the uvicorn webserver running FastAPI at `http://127.0.0.1:8000`


### Run Django webapp locally:
``` bash
make frontend-run
```
This starts the uvicorn webserver running Django webappa at `http://127.0.0.1:8080`. This requires a simultaneously running API server to work!

Don't worry, Docker containers are coming soon!


## ~Initial~ Established architecture design:

1. Scraper - script, possibly running as a cron job, that scrapes data from the NFM site, parses it and feeds it to a local sqlite database
2. Database - ~PostreSQL or something lighter~ local sqlite
3. ~Optionally - kafka as a data pipeline - possibly an overkill~
4. API server - to expose the data in the database to the frontend; FastAPI
5. Frontend - a webapp written in Django and HTMX


## TODO:
* Dockerfiles!
* POST/PUT endpoints in the API that would be used by the Scraper - this allows the Scraper to be used locally/in the CI/CD pipeline, and doesn't require to set up Internet egress in the VPS (cost-saving)
* Separation of English and Polish names
* api and webapp running as separate pods on a kubernetes cluster!
