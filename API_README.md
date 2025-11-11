# Used Cars API - FastAPI Application

Production-grade FastAPI application for searching used cars from OfferUp.

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python main.py
```

Or using uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

3. **Access the API:**
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health

## API Endpoints

### Car Search
- `POST /api/v1/cars/search` - Search for cars (with request body)
- `GET /api/v1/cars/search` - Search for cars (with query parameters)
- `GET /api/v1/cars/{listing_id}` - Get detailed car information

### Locations
- `GET /api/v1/locations/states` - Get all available states
- `GET /api/v1/locations/cities?state={state}` - Get cities for a state
- `GET /api/v1/locations/coordinates?state={state}&city={city}` - Get coordinates

### Health
- `GET /api/v1/health` - Health check endpoint

## Example Usage

### Search for 2014 CLS63 Mercedes with < 100,000 miles

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

### Search using GET endpoint

```bash
curl "http://localhost:8000/api/v1/cars/search?query=Honda+Civic&state=Texas&city=Austin&limit=10"
```

### Get car details

```bash
curl "http://localhost:8000/api/v1/cars/b415e8ab-d2b0-3c48-8c56-08f2c8471f75"
```

## Configuration

Set environment variables (optional):
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: false)
- `CORS_ORIGINS`: CORS allowed origins (default: *)

## Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── api/
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
└── requirements.txt       # Python dependencies
```

