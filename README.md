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


## Requirements:
This project consists of a `scraper`, `api` and a `webapp`. The following list of requirements is valid for the whole project:
* Makefile
* Docker
* Python 3.11+
* poetry
* sqlite3

Env variables:
* `DJANGO_SECRET_KEY` - your super secret string

## Quickstart:
### 1. Run scraper:
```bash
make scrape
```
This will create a local sqlite3 database named `events.db` and feed it with all the scraped data. If `events.db` exists, it will attempt to update it.

### 2. Run API and frontend app:
```bash
docker compose-up
```

Or you can run API and Frontend locally:
``` bash
make api-run
```
This starts the uvicorn webserver running FastAPI at `http://0.0.0.0:8000`

``` bash
make frontend-run
```
This starts the uvicorn webserver running Django webappa at `http://0.0.0.0:8080`. This requires a simultaneously running API server to work. API can be running in the Docker container, but if you run the frontend from the container, it won't have access to your local API! Docker compose mitigates this issue.


## ~Initial~ Established architecture design:

1. Scraper - script, possibly running as a cron job, that scrapes data from the NFM site, parses it and feeds it to a local sqlite database
2. Database - ~PostreSQL or something lighter~ local sqlite
3. ~Optionally - kafka as a data pipeline - possibly an overkill~
4. API server - to expose the data in the database to the frontend; FastAPI
5. Frontend - a webapp written in Django and HTMX


## TODO:
* [x] Dockerfiles!
* [ ] POST/PUT endpoints in the API that would be used by the Scraper - this allows the Scraper to be used locally/in the CI/CD pipeline, and doesn't require to set up Internet egress in the VPS (cost-saving)
* [x] All in English
* [ ] api and webapp running as separate pods on a kubernetes cluster!
