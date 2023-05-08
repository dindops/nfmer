# NFMer - a better way to search through a NFM repertoire

## Initial architecture design idea

1. Scraper - running as a cron job that would scrape data from the NFM site + update Postgres
2. Database - PostreSQL or something lighter
3. Optionally - kafka as a data pipeline - possibly an overkill
4. API server - to expose the data in the database to the frontend; FastAPI
5. Frontend - most likely Django/Flask, but Go options might be nice


Each part will run as a separate pod in a kubernetes cluster.
