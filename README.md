# pyOfferUp - OfferUp Scraper & Used Cars API

A Python package for scraping OfferUp listings and a production-grade FastAPI application for searching used cars.

## Table of Contents

- [Installation](#installation)
- [Package Usage](#package-usage)
- [API Usage](#api-usage)
- [Deployment](#deployment)
- [Development](#development)
- [Project Structure](#project-structure)
- [License](#license)

## Installation

### Install the Package

```bash
pip install pyOfferUp
```

Or install from source:

```bash
pip install -r requirements.txt
```

This will install both the `pyOfferUp` package and all API dependencies.

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

1. **Run the API server locally:**
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

#### Search using GET endpoint with filters

```bash
curl "http://localhost:8000/api/v1/cars/search?query=Honda+Civic&state=Texas&city=Austin&limit=10"
```

#### Broader search - minimal parameters (all optional)

```bash
# Get cars without specifying query or location (uses defaults)
curl "http://localhost:8000/api/v1/cars/search?limit=20"

# Get cars by make only
curl "http://localhost:8000/api/v1/cars/search?make=Mercedes&limit=20"

# Get cars by year and price range only
curl "http://localhost:8000/api/v1/cars/search?year=2020&price_min=10000&price_max=50000&limit=20"
```

#### Get car details

```bash
curl "http://localhost:8000/api/v1/cars/{listing_id}"
```

**Note:** All query parameters are optional. Omit parameters to get broader results:
- No `query` → Uses default "car" search term
- No `state`/`city`/`lat`/`lon` → Uses default location (California)
- No filters → Returns all matching listings

### API Configuration

Set environment variables (optional):
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000, automatically set by Render in production)
- `DEBUG`: Enable debug mode (default: false)
- `CORS_ORIGINS`: CORS allowed origins (default: *)

## Deployment

### Render Deployment

This application is configured for deployment on [Render](https://render.com).

#### Quick Setup

1. **Connect your repository** to Render
2. **Create a new Web Service** in Render dashboard
3. **Configure the service:**
   - **Build Command:** `pip install -r requirements.txt && pip install -e .`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3
   - **Python Version:** 3.12.0 (or use `runtime.txt`)

   **Note:** The build command installs dependencies first, then installs the local `pyOfferUp` package.

#### Important Notes

**PORT Environment Variable:**
- Render automatically sets the `PORT` environment variable
- The app is configured to read `PORT` from the environment
- **Do NOT set PORT manually** in Render's environment variables - Render sets it automatically

**Environment Variables (Optional):**
You can set these in Render's dashboard:
- `HOST`: Server host (default: 0.0.0.0)
- `DEBUG`: Enable debug mode (default: false)
- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: *)

#### Configuration Files

- `render.yaml` - Render service configuration (optional, can configure via dashboard)
- `runtime.txt` - Specifies Python version (3.12.0)

#### Testing Deployment

After deployment, test the endpoints:
- Health check: `https://your-app.onrender.com/api/v1/health`
- API docs: `https://your-app.onrender.com/docs`
- Search: `https://your-app.onrender.com/api/v1/cars/search?query=car&state=California&city=Los+Angeles&limit=5`

#### Troubleshooting

**Issue: App not starting**
- Check that `requirements.txt` includes `-e .` to install the local package
- Verify Python version matches runtime.txt (3.12.0)
- Check build logs for import errors

**Issue: Port binding errors**
- Ensure start command uses `$PORT` (Render's environment variable)
- Don't hardcode port numbers

**Issue: Import errors**
- Make sure build command includes `pip install -e .` to install the local package
- Verify all dependencies are in requirements.txt
- Check that `setup.py` or `pyproject.toml` exists in the root directory

**Issue: "ModuleNotFoundError: No module named 'pyOfferUp'"**
- Ensure build command includes `pip install -e .` after installing requirements
- Verify `setup.py` or `pyproject.toml` exists in the root directory
- Check build logs to confirm package installation succeeded

**Issue: "does not appear to be a Python project: neither 'setup.py' nor 'pyproject.toml' found"**
- Ensure `setup.py` or `pyproject.toml` is in the repository root
- Verify the build command runs from the correct directory
- Try using the build command: `pip install -r requirements.txt && pip install -e .`

**Issue: Different results than local**
- Check environment variables match local setup
- Verify the same Python version is used (3.12.0)
- Check Render logs for any errors or warnings

**Issue: App crashes on startup**
- Check build logs for import errors
- Verify `pyOfferUp` package installed correctly
- Check that all imports in `api/` modules work
- Review Render logs for specific error messages

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

### Project Structure

```
pyOfferUp/
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
├── pyOfferUp/             # Core package
│   ├── __init__.py
│   ├── fetch.py            # Scraping functions
│   ├── places.py           # Location data
│   └── constants.py        # Constants and enums
├── tests/                 # Test files
│   ├── test_package.py
│   ├── test_used_cars.py
│   └── test_cls63_search.py
├── main.py               # API entry point
├── requirements.txt      # Python dependencies
├── setup.py             # Package setup
├── render.yaml          # Render deployment config (optional)
├── runtime.txt          # Python version specification
└── README.md            # This file
```

### Key Features

- **Package**: Direct scraping of OfferUp listings with location-based search
- **API**: RESTful API with advanced filtering (year, make, model, mileage)
- **Smart Filtering**: Extracts make/model from query strings, filters parts listings
- **Vehicle Attributes**: Fetches detailed vehicle information when available
- **Production Ready**: Configured for Render deployment with proper environment handling

## License

See LICENSE.txt for details.
