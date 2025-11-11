# pyOfferUp - OfferUp Scraper & Used Cars API

A Python package for scraping OfferUp listings and a production-grade FastAPI application for searching used cars.

## Table of Contents

- [Installation](#installation)
- [Package Usage](#package-usage)
- [API Usage](#api-usage)
- [Project Structure](#project-structure)
- [Development](#development)

## Installation

### Install the Package

```bash
pip install pyOfferUp
```

Or install from source:

```bash
pip install -r requirements.txt
```

### Install API Dependencies

For the FastAPI application:

```bash
pip install -r requirements.txt
```

## Package Usage

### Cities and States

`places.py` contains all supported cities and states with their respective coordinates (case sensitive).

```python
from pyOfferUp import places

print(places.available_states())
print(places.available_cities("Texas"))
print(places.available_cities("Alabama"))
```

### Search Listings by City/State

```python
from pyOfferUp import fetch

# Search for listings in a specific city
posts = fetch.get_listings(
    query="luigis mansion", 
    state="Texas", 
    city="Mcallen", 
    limit=100
)

# NOTE: When looking in a city you must also provide the state the city resides in.
```

### Search Listings by Coordinates

```python
from pyOfferUp import fetch

# Search around specific coordinates
posts = fetch.get_listings_by_lat_lon(
    query="luigis mansion", 
    lat=26.2043691, 
    lon=-98.230082, 
    limit=100
)
```

### Get Listing Details

```python
from pyOfferUp import fetch

details = fetch.get_listing_details(listing_id)
```

## API Usage

### Quick Start

1. **Run the API server:**
```bash
python main.py
```

Or using uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Access the API:**
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health

### API Endpoints

#### Car Search
- `POST /api/v1/cars/search` - Search for cars (with request body)
- `GET /api/v1/cars/search` - Search for cars (with query parameters)
- `GET /api/v1/cars/{listing_id}` - Get detailed car information

#### Locations
- `GET /api/v1/locations/states` - Get all available states
- `GET /api/v1/locations/cities?state={state}` - Get cities for a state
- `GET /api/v1/locations/coordinates?state={state}&city={city}` - Get coordinates

#### Health
- `GET /api/v1/health` - Health check endpoint

### Example API Calls

#### Search for 2014 CLS63 Mercedes with < 100,000 miles

```bash
curl -X POST "http://localhost:8000/api/v1/cars/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "CLS63 Mercedes",
    "state": "California",
    "city": "Los Angeles",
    "year": 2014,
    "max_miles": 100000,
    "limit": 10
  }'
```

#### Search using GET endpoint

```bash
curl "http://localhost:8000/api/v1/cars/search?query=Honda+Civic&state=Texas&city=Austin&limit=10"
```

#### Get car details

```bash
curl "http://localhost:8000/api/v1/cars/{listing_id}"
```

### API Configuration

Set environment variables (optional):
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: false)
- `CORS_ORIGINS`: CORS allowed origins (default: *)

## Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── pyOfferUp/              # Core package
│   ├── __init__.py
│   ├── fetch.py            # Scraping functions
│   ├── places.py           # Location data
│   └── constants.py        # Constants and enums
├── api/                    # FastAPI application
│   ├── config.py          # Configuration settings
│   ├── models.py          # Pydantic models
│   ├── middleware.py       # Custom middleware
│   ├── routers/           # API route handlers
│   │   ├── cars.py
│   │   ├── locations.py
│   │   └── health.py
│   └── services/          # Business logic
│       ├── car_service.py
│       └── location_service.py
├── tests/                 # Test files
│   ├── test_package.py
│   ├── test_used_cars.py
│   └── test_cls63_search.py
├── requirements.txt       # Python dependencies
├── setup.py              # Package setup
└── README.md             # This file
```

## Development

### Running Tests

```bash
# Run package tests
python -m pytest tests/

# Or run individual test files
python tests/test_package.py
python tests/test_used_cars.py
python tests/test_cls63_search.py
```

### Building the Package

```bash
python setup.py sdist bdist_wheel
```

## License

See LICENSE.txt for details.
