# Instructions
## Prerequisites
To run this application you need to have installed:
- Docker
- Docker Compose

To start the application run in the terminal in the  root folder:

`docker-compose up --build web`

The above command will set up the web and database volumes and make the project available in:

http://localhost:8000/


## Endpoints
- http://localhost:8000/latest for today's currency rate.
It returns a JSON with the rate value for the current date and the corresponding date. If it is before 16:00 CET the date and value will be of the previous day.
- http://localhost:8000/YYYY-MM-DD..YYYY-MM-DD/ for the currency rates between 2 dates. For example: http://localhost:8000/2004-01-01..2014-01-01/. It returns a JSON for the average rate value and the corresponding start and end date that are returned from the Frankfurter API. Sometimes the Frankfurter API will respond with dates near the requested ones so the requested dates will not match the dates in the JSON.

## Tests
To run the application tests run the command: 

`docker-compose up --build tests`