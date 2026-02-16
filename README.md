# NFMer - a better way to search through a NFM repertoire

## Why?
This is first and foremost a non-profit learning project!

This is a learning project built to solve a real problem: NFM's website couldn't search events by composition, only by performer/conductor. I wanted to find specific pieces being performed without manually checking every event.

I also wanted to build something with FastAPI and try out SQLModel.


## Requirements:
This project consists of a `scraper` and `api`. The following list of requirements is valid for the whole project:
* Makefile
* Docker
* Python 3.11+
* poetry
* sqlite3

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
This starts the uvicorn webserver running a HTMX webpage at `http://0.0.0.0:8080`. This requires a simultaneously running API server to work. API can be running in the Docker container, but if you run the frontend from the container, it won't have access to your local API! Docker compose mitigates this issue.


## ~Initial~ Established architecture design:

1. Scraper - script, possibly running as a cron job, that scrapes data from the NFM site, parses it and feeds it to a local sqlite database
2. Database - ~PostreSQL or something lighter~ local sqlite
3. ~Optionally - kafka as a data pipeline - possibly an overkill~
4. API server - to expose the data in the database to the frontend; FastAPI
5. Frontend - a webapp HTMX


## TODO:
* [x] Dockerfiles!
* [ ] POST/PUT endpoints in the API that would be used by the Scraper - this allows the Scraper to be used locally/in the CI/CD pipeline, and doesn't require to set up Internet egress in the VPS (cost-saving)
* [x] All in English
* [ ] api and webapp running as separate pods on a kubernetes cluster!
