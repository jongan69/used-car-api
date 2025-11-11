import asyncio
import logging
from typing import List, Optional
from functools import lru_cache

from pyOfferUp import fetch, places
from pyOfferUp.constants import CONDITION, SORT, DELIVERY

from api.models import (
    CarSearchRequest, CarListing, VehicleAttributes, CarDetailResponse
)
from api.config import settings

logger = logging.getLogger(__name__)


class CarService:
    """Service for car-related operations"""
    
    def __init__(self):
        self.cache = {} if settings.ENABLE_CACHE else None
    
    async def search_cars(self, request: CarSearchRequest) -> List[CarListing]:
        """
        Search for cars based on the request parameters.
        """
        # Run the blocking operation in a thread pool
        loop = asyncio.get_event_loop()
        listings = await loop.run_in_executor(
            None,
            self._search_cars_sync,
            request
        )
        
        # Convert to response models
        car_listings = []
        for listing in listings:
            car_listing = self._convert_listing_to_model(listing)
            
            # Apply post-filtering for vehicle-specific attributes
            if self._matches_filters(car_listing, request):
                car_listings.append(car_listing)
        
        return car_listings
    
    def _search_cars_sync(self, request: CarSearchRequest) -> List[dict]:
        """Synchronous car search (runs in thread pool)"""
        try:
            # Convert request conditions to pyOfferUp constants
            conditions = []
            for cond in request.conditions:
                conditions.append(CONDITION[cond.value])
            
            # Convert sort option
            sort_option = SORT[request.sort.value.replace("-", "_").upper()]
            
            # Convert delivery option
            delivery_option = DELIVERY[request.delivery.value.replace("_", "_").upper()]
            
            # Determine search method
            if request.lat is not None and request.lon is not None:
                # Search by coordinates
                listings = fetch.get_listings_by_lat_lon(
                    query=request.query,
                    lat=request.lat,
                    lon=request.lon,
                    limit=request.limit,
                    pickup_distance=request.pickup_distance,
                    price_min=request.price_min,
                    price_max=request.price_max,
                    sort=sort_option,
                    delivery=delivery_option,
                    conditions=conditions
                )
            elif request.state:
                # Search by state/city
                listings = fetch.get_listings(
                    query=request.query,
                    state=request.state,
                    city=request.city,
                    limit=request.limit,
                    pickup_distance=request.pickup_distance,
                    price_min=request.price_min,
                    price_max=request.price_max,
                    sort=sort_option,
                    delivery=delivery_option,
                    conditions=conditions
                )
            else:
                raise ValueError("Either state/city or lat/lon must be provided")
            
            return listings
        except Exception as e:
            logger.error(f"Error in car search: {e}", exc_info=True)
            raise
    
    def _convert_listing_to_model(self, listing: dict) -> CarListing:
        """Convert raw listing dict to CarListing model"""
        # Get vehicle attributes if available
        vehicle_attrs = None
        image_url = None
        
        if listing.get('image'):
            image_url = listing['image'].get('url')
        
        return CarListing(
            listing_id=listing.get('listingId', ''),
            title=listing.get('title', ''),
            price=listing.get('price'),
            location_name=listing.get('locationName'),
            listing_url=listing.get('listingUrl', ''),
            condition_text=listing.get('conditionText'),
            image_url=image_url,
            vehicle_attributes=None  # Will be populated if details are fetched
        )
    
    def _matches_filters(self, listing: CarListing, request: CarSearchRequest) -> bool:
        """
        Check if listing matches vehicle-specific filters.
        Note: This requires fetching details, which is expensive.
        For now, we'll do basic title matching and fetch details only if needed.
        """
        # Basic title matching for make/model/year
        title_upper = listing.title.upper()
        
        if request.make and request.make.upper() not in title_upper:
            return False
        
        if request.model and request.model.upper() not in title_upper:
            return False
        
        if request.year and str(request.year) not in listing.title:
            return False
        
        # For mileage and detailed matching, we'd need to fetch details
        # This is expensive, so we'll do it selectively
        if request.max_miles is not None or request.min_miles is not None:
            # Fetch details to check mileage
            try:
                details = fetch.get_listing_details(listing.listing_id)
                if details and 'data' in details and 'listing' in details['data']:
                    vehicle_attrs = details['data']['listing'].get('vehicleAttributes')
                    if vehicle_attrs:
                        miles = vehicle_attrs.get('vehicleMiles')
                        if miles:
                            miles_int = int(miles)
                            if request.max_miles is not None and miles_int > request.max_miles:
                                return False
                            if request.min_miles is not None and miles_int < request.min_miles:
                                return False
                        
                        # Update vehicle attributes in listing
                        listing.vehicle_attributes = VehicleAttributes(
                            year=vehicle_attrs.get('vehicleYear'),
                            make=vehicle_attrs.get('vehicleMake'),
                            model=vehicle_attrs.get('vehicleModel'),
                            miles=int(vehicle_attrs.get('vehicleMiles')) if vehicle_attrs.get('vehicleMiles') else None,
                            color=vehicle_attrs.get('vehicleColor'),
                            transmission=vehicle_attrs.get('vehicleTransmissionClean'),
                            fuel_type=vehicle_attrs.get('vehicleFuelType'),
                            body=vehicle_attrs.get('vehicleBody'),
                            drive_train=vehicle_attrs.get('vehicleDriveTrain'),
                            vin=vehicle_attrs.get('vehicleVin')
                        )
            except Exception as e:
                logger.warning(f"Could not fetch details for listing {listing.listing_id}: {e}")
        
        return True
    
    async def get_car_details(self, listing_id: str) -> Optional[CarDetailResponse]:
        """
        Get detailed information about a specific car listing.
        """
        loop = asyncio.get_event_loop()
        details = await loop.run_in_executor(
            None,
            fetch.get_listing_details,
            listing_id
        )
        
        if not details or 'data' not in details or 'listing' not in details['data']:
            return None
        
        listing_data = details['data']['listing']
        
        # Extract vehicle attributes
        vehicle_attrs_data = listing_data.get('vehicleAttributes')
        vehicle_attrs = None
        
        if vehicle_attrs_data:
            vehicle_attrs = VehicleAttributes(
                year=vehicle_attrs_data.get('vehicleYear'),
                make=vehicle_attrs_data.get('vehicleMake'),
                model=vehicle_attrs_data.get('vehicleModel'),
                miles=int(vehicle_attrs_data.get('vehicleMiles')) if vehicle_attrs_data.get('vehicleMiles') else None,
                color=vehicle_attrs_data.get('vehicleColor'),
                transmission=vehicle_attrs_data.get('vehicleTransmissionClean'),
                fuel_type=vehicle_attrs_data.get('vehicleFuelType'),
                body=vehicle_attrs_data.get('vehicleBody'),
                drive_train=vehicle_attrs_data.get('vehicleDriveTrain'),
                vin=vehicle_attrs_data.get('vehicleVin')
            )
        
        # Extract photos
        photos = []
        photos_data = listing_data.get('photos', [])
        for photo in photos_data:
            if photo.get('detail') and photo['detail'].get('url'):
                photos.append(photo['detail']['url'])
        
        return CarDetailResponse(
            listing_id=listing_id,
            title=listing_data.get('title', ''),
            price=listing_data.get('price'),
            description=listing_data.get('description'),
            location_name=listing_data.get('locationDetails', {}).get('locationName') if listing_data.get('locationDetails') else None,
            listing_url=f"https://offerup.com/item/detail/{listing_id}",
            condition=listing_data.get('condition'),
            vehicle_attributes=vehicle_attrs,
            photos=photos
        )

