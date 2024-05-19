# Trading platform

## Overview

This project is designed to test and simulate a trading system where orders can be created via REST API or WebSockets
and updates are broadcast via WebSockets. The project includes a server and tests that are set up into
docker containers.

## Used libraries:

### Backend server

* FastAPI
* uvicorn
* pydantic

### Testing

* pytest
* pytest-asyncio
* httpx
* websockets

## Prerequisites

Ensure you have the following installed on your system:

* Python 3.11
* Docker
* Docker Compose

## Setup

1. Clone the repository:

```bash
git clone git@github.com:agilezs/trading-platform.git
cd trading-platform
```

2. Build and start the application and tests using Docker Compose:

```bash
docker-compose up --build 
```

3. The container with the application should be running at `http://localhost:8000` and interactive documentation (
   Swagger)
   should be available at http://localhost:8000/docs or http://localhost:8000/redoc
4. Also, the first test run should be performed with test report available as a html file
   at `trading-platform/reports/report.html`

## Running tests

1. Running tests can be performed using

```bash
docker-compose run tests
```

2. This also updates the test report html file at `trading-platform/reports/report.html`

## Running performance tests

1. Ensure the application is running.
2. Run the performance test script available in `performance` module:

```bash
python performance_test.py
```

3. The results and metrics should be printed to the console.
4. This test is only available to be run locally

## Running the application and tests locally:

1. If you need to run the application locally, you should create a virtual environment and activate it:

```bash
python -m venv venv 
```

2. Install required libraries from both `./backend/requirements.txt` and `./tests/requirements.txt`

```bash
pip install -r ./backend/requirements.txt
pip install -r ./tests/requirements.txt
```

3. Run the `server.py` and then tests


