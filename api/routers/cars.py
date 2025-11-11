from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
import logging

from api.models import (
    CarSearchRequest, CarSearchResponse, CarListing, VehicleAttributes,
    CarDetailResponse, Condition, SortOption, DeliveryOption
)
from api.services.car_service import CarService
from api.services.location_service import LocationService
from api.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_car_service() -> CarService:
    """Dependency injection for car service"""
    return CarService()


def get_location_service() -> LocationService:
    """Dependency injection for location service"""
    return LocationService()


@router.post("/cars/search", response_model=CarSearchResponse)
async def search_cars(
    request: CarSearchRequest,
    car_service: CarService = Depends(get_car_service)
):
    """
    Search for used cars with advanced filtering options.
    
    All parameters are optional - omit them to get broader results.
    
    - **query**: Search query (optional - omit for broader results, e.g., "Honda Civic", "Mercedes CLS63")
    - **state**: State name (optional - omit for broader geographic results)
    - **city**: City name (optional - requires state if provided)
    - **lat/lon**: Coordinates (optional, alternative to state/city)
    - **limit**: Maximum number of results (1-100, default: 50)
    - **price_min/price_max**: Price range filter (optional)
    - **year**: Filter by vehicle year (optional)
    - **make**: Filter by vehicle make (optional)
    - **model**: Filter by vehicle model (optional)
    - **max_miles/min_miles**: Mileage filters (optional)
    - **sort**: Sort option (newest_first, closest_first, price_low_to_high, price_high_to_low)
    """
    try:
        logger.info(f"Car search request: {request.model_dump()}")
        
        results = await car_service.search_cars(request)
        
        # Use actual query (may be default "car" if not provided)
        actual_query = request.query if request.query else "car"
        
        return CarSearchResponse(
            total_results=len(results),
            listings=results,
            query=actual_query,
            filters_applied=request.model_dump(exclude_none=True)
        )
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching cars: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/cars/search", response_model=CarSearchResponse)
async def search_cars_get(
    query: Optional[str] = Query(None, description="Search query (optional - omit for broader results)"),
    state: Optional[str] = Query(None, description="State name"),
    city: Optional[str] = Query(None, description="City name"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    price_min: Optional[int] = Query(None, ge=0, description="Minimum price"),
    price_max: Optional[int] = Query(None, ge=0, description="Maximum price"),
    year: Optional[int] = Query(None, ge=1900, le=2030, description="Vehicle year"),
    make: Optional[str] = Query(None, description="Vehicle make"),
    model: Optional[str] = Query(None, description="Vehicle model"),
    max_miles: Optional[int] = Query(None, ge=0, description="Maximum mileage"),
    min_miles: Optional[int] = Query(None, ge=0, description="Minimum mileage"),
    sort: SortOption = Query(SortOption.NEWEST_FIRST, description="Sort option"),
    car_service: CarService = Depends(get_car_service)
):
    """
    Search for used cars (GET endpoint for convenience).
    Same functionality as POST /cars/search but using query parameters.
    
    All parameters are optional - omit them to get broader results.
    """
    request = CarSearchRequest(
        query=query,
        state=state,
        city=city,
        lat=lat,
        lon=lon,
        limit=limit,
        price_min=price_min,
        price_max=price_max,
        year=year,
        make=make,
        model=model,
        max_miles=max_miles,
        min_miles=min_miles,
        sort=sort
    )
    
    return await search_cars(request, car_service)


@router.get("/cars/test", response_model=dict)
async def test_search(
    car_service: CarService = Depends(get_car_service)
):
    """Test endpoint to debug search issues"""
    from api.models import CarSearchRequest
    
    request = CarSearchRequest(
        query="car",
        state="California",
        city="Los Angeles",
        limit=3
    )
    
    try:
        results = await car_service.search_cars(request)
        return {
            "status": "success",
            "results_count": len(results),
            "sample_titles": [r.title for r in results[:3]]
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

