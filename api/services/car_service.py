import asyncio
import logging
from typing import List, Optional

from pyOfferUp import fetch
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
        try:
            # Run the blocking operation in a thread pool
            loop = asyncio.get_event_loop()
            listings = await loop.run_in_executor(
                None,
                self._search_cars_sync,
                request
            )
            
            logger.info(f"Found {len(listings)} raw listings from pyOfferUp")
            
            if not listings:
                logger.warning("No listings returned from pyOfferUp")
                return []
            
            # Convert to response models
            car_listings = []
            filtered_count = 0
            for listing in listings:
                try:
                    car_listing = self._convert_listing_to_model(listing)
                    
                    # Apply post-filtering for vehicle-specific attributes
                    if self._matches_filters(car_listing, request):
                        car_listings.append(car_listing)
                    else:
                        filtered_count += 1
                        logger.debug(f"Filtered out listing: {car_listing.title}")
                except Exception as e:
                    logger.warning(f"Error converting listing: {e}")
                    continue
            
            logger.info(f"After filtering: {len(car_listings)} listings match criteria (filtered out {filtered_count})")
            
            # If no results after filtering, return similar results (relax filters)
            if len(car_listings) == 0 and len(listings) > 0:
                logger.info("No exact matches found, returning similar results with relaxed filters")
                # Create a relaxed request (remove strict filters)
                relaxed_request = CarSearchRequest(
                    query=request.query,
                    state=request.state,
                    city=request.city,
                    lat=request.lat,
                    lon=request.lon,
                    limit=request.limit,
                    pickup_distance=request.pickup_distance,
                    price_min=request.price_min,
                    price_max=request.price_max,
                    sort=request.sort,
                    delivery=request.delivery,
                    conditions=request.conditions,
                    # Keep make/model but remove year and mileage filters
                    make=request.make,
                    model=request.model,
                    year=None,  # Remove year filter
                    max_miles=None,  # Remove mileage filter
                    min_miles=None
                )
                
                # Re-filter with relaxed criteria
                for listing in listings:
                    try:
                        car_listing = self._convert_listing_to_model(listing)
                        if self._matches_filters(car_listing, relaxed_request):
                            car_listings.append(car_listing)
                    except Exception as e:
                        logger.warning(f"Error converting listing: {e}")
                        continue
                
                logger.info(f"After relaxed filtering: {len(car_listings)} similar listings returned")
            
            return car_listings
        except Exception as e:
            logger.error(f"Error in search_cars: {e}", exc_info=True)
            raise
    
    def _search_cars_sync(self, request: CarSearchRequest) -> List[dict]:
        """Synchronous car search (runs in thread pool)"""
        try:
            # Use default query if not provided (empty string to maximize results)
            query = request.get_query()
            logger.info(f"Searching with query: {query}, state: {request.state}, city: {request.city}")
            
            # Convert request conditions to pyOfferUp constants
            conditions = []
            if request.conditions:
                condition_mapping = {
                    "NEW": CONDITION.NEW,
                    "OPEN_BOX": CONDITION.OPEN_BOX,
                    "REFURBISHED": CONDITION.REFURBISHED,
                    "USED": CONDITION.USED,
                    "BROKEN": CONDITION.BROKEN,
                    "OTHER": CONDITION.OTHER
                }
                for cond in request.conditions:
                    if cond.name in condition_mapping:
                        conditions.append(condition_mapping[cond.name])
            
            # Convert sort option
            sort_mapping = {
                "NEWEST_FIRST": SORT.NEWEST_FIRST,
                "CLOSEST_FIRST": SORT.CLOSEST_FIRST,
                "PRICE_LOW_TO_HIGH": SORT.PRICE_LOW_TO_HIGH,
                "PRICE_HIGH_TO_LOW": SORT.PRICE_HIGH_TO_LOW
            }
            sort_option = sort_mapping.get(request.sort.name if request.sort else "NEWEST_FIRST", SORT.NEWEST_FIRST)
            
            # Convert delivery option
            delivery_mapping = {
                "PICKUP": DELIVERY.PICKUP,
                "SHIPPING": DELIVERY.SHIPPING,
                "PICKUP_AND_SHIPPING": DELIVERY.PICKUP_AND_SHIPPING
            }
            delivery_option = delivery_mapping.get(request.delivery.name if request.delivery else "PICKUP", DELIVERY.PICKUP)
            
            # Use defaults for limit and pickup_distance if not provided
            limit = request.limit or 50
            pickup_distance = request.pickup_distance or 50
            
            # Determine search method
            if request.lat is not None and request.lon is not None:
                # Search by coordinates
                logger.info(f"Searching by coordinates: lat={request.lat}, lon={request.lon}")
                listings = fetch.get_listings_by_lat_lon(
                    query=query,
                    lat=request.lat,
                    lon=request.lon,
                    limit=limit,
                    pickup_distance=pickup_distance,
                    price_min=request.price_min,
                    price_max=request.price_max,
                    sort=sort_option,
                    delivery=delivery_option,
                    conditions=conditions
                )
            elif request.state:
                # Search by state/city
                logger.info(f"Searching by location: state={request.state}, city={request.city}")
                listings = fetch.get_listings(
                    query=query,
                    state=request.state,
                    city=request.city,
                    limit=limit,
                    pickup_distance=pickup_distance,
                    price_min=request.price_min,
                    price_max=request.price_max,
                    sort=sort_option,
                    delivery=delivery_option,
                    conditions=conditions
                )
            else:
                # No location provided - use geographic center of US with max pickup distance for nationwide search
                # Geographic center of the contiguous United States (Lebanon, Kansas)
                nationwide_lat = 39.8283
                nationwide_lon = -98.5795
                # Use maximum pickup distance (500 miles) to cover as much area as possible
                nationwide_pickup_distance = 500
                logger.info(f"No location provided, using nationwide search from center of US (lat={nationwide_lat}, lon={nationwide_lon}) with {nationwide_pickup_distance} mile radius")
                listings = fetch.get_listings_by_lat_lon(
                    query=query,
                    lat=nationwide_lat,
                    lon=nationwide_lon,
                    limit=limit,
                    pickup_distance=nationwide_pickup_distance,
                    price_min=request.price_min,
                    price_max=request.price_max,
                    sort=sort_option,
                    delivery=delivery_option,
                    conditions=conditions
                )
            
            logger.info(f"Search returned {len(listings)} listings")
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
    
    def _extract_keywords_from_query(self, query: str) -> tuple:
        """Extract potential make and model from query string"""
        query_upper = query.upper()
        make = None
        model = None
        
        # Common car makes to look for
        common_makes = ['MERCEDES', 'BENZ', 'MERCEDES-BENZ', 'HONDA', 'TOYOTA', 'FORD', 
                       'BMW', 'AUDI', 'LEXUS', 'ACURA', 'INFINITI', 'NISSAN', 'CHEVROLET',
                       'CHEVY', 'DODGE', 'JEEP', 'CHRYSLER', 'GMC', 'CADILLAC', 'LINCOLN']
        
        # Check for make in query
        for car_make in common_makes:
            if car_make in query_upper:
                make = car_make
                break
        
        # Extract model - look for common patterns like "CLS63", "Civic", "Camry", etc.
        # Remove make from query to find model
        query_without_make = query_upper
        if make:
            query_without_make = query_without_make.replace(make, '').replace('-', '').strip()
        
        # Model is usually what's left after removing make and year
        # Look for alphanumeric patterns
        import re
        model_patterns = re.findall(r'[A-Z0-9]+', query_without_make)
        if model_patterns:
            # Take the longest pattern as model (excluding years)
            model_candidates = [p for p in model_patterns if not p.isdigit() or len(p) != 4]
            if model_candidates:
                model = max(model_candidates, key=len)
        
        return make, model
    
    def _matches_filters(self, listing: CarListing, request: CarSearchRequest) -> bool:
        """
        Check if listing matches vehicle-specific filters.
        Matches the logic from test_cls63_search.py:
        - Extract make/model from query if not explicitly provided
        - Do title-based matching first
        - Fetch details for mileage/year verification when needed
        - Use vehicle attributes if available, fall back to title matching
        """
        title_upper = listing.title.upper()
        
        # Exclude parts listings (like test script does)
        parts_keywords = ['PART', 'SHELL', 'PANEL', 'DOOR', 'BUMPER', 'FENDER', 'HOOD', 'TRUNK', 
                         'SEAT', 'WHEEL', 'RIM', 'HEADLIGHT', 'TAILLIGHT', 'OEM', 'DRIVER REAR']
        is_part = any(keyword in title_upper for keyword in parts_keywords)
        if is_part:
            logger.debug(f"Filtered out parts listing: {listing.title}")
            return False
        
        # Extract make/model from query if not explicitly provided
        make_to_check = request.make
        model_to_check = request.model
        
        if not make_to_check or not model_to_check:
            query_str = request.get_query()
            if query_str:
                query_make, query_model = self._extract_keywords_from_query(query_str)
                if not make_to_check and query_make:
                    make_to_check = query_make
                if not model_to_check and query_model:
                    model_to_check = query_model
        
        logger.debug(f"Checking listing '{listing.title}' - make_to_check: {make_to_check}, model_to_check: {model_to_check}, year_filter: {request.year}")
        
        # Title-based matching (like test script)
        has_make = False
        has_model = False
        has_year = False
        
        if make_to_check:
            make_upper = make_to_check.upper()
            # Check for Mercedes variations
            if make_upper in ['MERCEDES', 'MERCEDES-BENZ', 'BENZ']:
                has_make = 'MERCEDES' in title_upper or 'BENZ' in title_upper
            else:
                has_make = make_upper in title_upper
        
        if model_to_check:
            model_upper = model_to_check.upper()
            # Check for model variations (CLS63, CLS 63, CLS-63)
            model_variations = [
                model_upper,
                model_upper.replace(" ", ""),
                model_upper.replace("-", ""),
                model_upper.replace(" ", "-"),
                model_upper.replace("-", " ")
            ]
            has_model = any(variation in title_upper for variation in model_variations)
        
        if request.year:
            year_str = str(request.year)
            has_year = year_str in listing.title
        
        # If no vehicle-specific filters, include all results
        has_explicit_filters = any([
            request.make,
            request.model,
            request.year,
            request.max_miles is not None,
            request.min_miles is not None
        ])
        
        # If we extracted make/model from query, we should filter by them
        if make_to_check or model_to_check:
            has_explicit_filters = True
        
        if not has_explicit_filters:
            return True
        
        # Fetch details to check vehicle attributes (like test script does)
        # But only if we need to verify mileage or if title doesn't match
        vehicle_attrs = None
        vehicle_year = None
        vehicle_make = None
        vehicle_model = None
        vehicle_miles = None
        
        # Only fetch details if we really need to verify something that's not in the title
        # Optimize: Don't fetch if title already matches make/model and we don't need mileage/year check
        needs_details = False
        
        # Need details if:
        # 1. We need to check mileage (always need vehicle attributes for this)
        # 2. Title doesn't match make/model and we want to check vehicle attributes
        # 3. Year filter is set and not in title
        if request.max_miles is not None or request.min_miles is not None:
            needs_details = True  # Always need to fetch for mileage check
        elif (make_to_check and not has_make) or (model_to_check and not has_model):
            needs_details = True  # Title doesn't match, check vehicle attributes
        elif request.year and not has_year:
            needs_details = True  # Year filter set but not in title
        
        if needs_details:
            try:
                details = fetch.get_listing_details(listing.listing_id)
                if details and 'data' in details and 'listing' in details['data']:
                    vehicle_attrs = details['data']['listing'].get('vehicleAttributes')
                    if vehicle_attrs:
                        vehicle_year = vehicle_attrs.get('vehicleYear')
                        make_raw = vehicle_attrs.get('vehicleMake')
                        model_raw = vehicle_attrs.get('vehicleModel')
                        vehicle_make = make_raw.upper() if make_raw else None
                        vehicle_model = model_raw.upper() if model_raw else None
                        vehicle_miles = vehicle_attrs.get('vehicleMiles')
            except Exception as e:
                logger.debug(f"Could not fetch details for listing {listing.listing_id}: {e}")
                # If we can't fetch details, be lenient - only exclude if title clearly doesn't match
                # Don't exclude just because we can't verify filters
                pass
        
        # Check if it matches our criteria (like test script)
        # Year can be string or int
        year_match = False
        if request.year:
            # Check if year is in title first
            if has_year:
                year_match = True
            # Then check vehicle attributes if available
            elif vehicle_year:
                # Try multiple formats for year matching
                try:
                    vehicle_year_int = int(vehicle_year) if isinstance(vehicle_year, str) else vehicle_year
                    year_match = (vehicle_year_int == request.year)
                except (ValueError, TypeError):
                    # If we can't parse, try string comparison
                    year_match = (str(vehicle_year) == str(request.year))
            # If no year in title and no vehicle year, be lenient (don't exclude)
            else:
                year_match = False  # Will be handled leniently in matching logic
        else:
            year_match = True  # No year filter
        
        # Check make - check both title and vehicle attributes (either can match)
        make_match = False
        if make_to_check:
            # Check title first
            if has_make:
                make_match = True
            # Also check vehicle attributes if available
            if not make_match and vehicle_make:
                make_upper = make_to_check.upper()
                if make_upper in ['MERCEDES', 'MERCEDES-BENZ', 'BENZ']:
                    make_match = 'MERCEDES' in vehicle_make or 'BENZ' in vehicle_make
                else:
                    make_match = make_upper in vehicle_make
        else:
            make_match = True  # No make filter
        
        # Check model - check both title and vehicle attributes (either can match)
        model_match = False
        if model_to_check:
            # Check title first
            if has_model:
                model_match = True
            # Also check vehicle attributes if available
            if not model_match and vehicle_model:
                model_upper = model_to_check.upper()
                # Special handling for CLS models
                if 'CLS' in model_upper:
                    model_match = ('CLS63' in vehicle_model or 'CLS 63' in vehicle_model or 
                                 'CLS-63' in vehicle_model)
                else:
                    model_match = model_upper in vehicle_model
        else:
            model_match = True  # No model filter
        
        # Check mileage
        miles_match = True
        if vehicle_miles is not None:
            try:
                miles = int(vehicle_miles) if isinstance(vehicle_miles, str) else vehicle_miles
                if request.max_miles is not None and miles > request.max_miles:
                    miles_match = False
                if request.min_miles is not None and miles < request.min_miles:
                    miles_match = False
            except (ValueError, TypeError):
                miles_match = True  # If we can't parse miles, include it
        
        # Match logic - be lenient: only exclude if we can definitively say it doesn't match
        # Check mileage - only exclude if we have definitive mileage data that doesn't match
        # If we can't verify mileage, be lenient and include it
        if request.max_miles is not None or request.min_miles is not None:
            if vehicle_miles is not None:
                # Only exclude if mileage definitively doesn't match
                if not miles_match:
                    logger.debug(f"Filtered out '{listing.title}' - mileage mismatch: {vehicle_miles} vs max={request.max_miles}, min={request.min_miles}")
                    return False
            # If we need to check mileage but don't have vehicle_miles data, be lenient and include it
            # This ensures we don't exclude listings just because we can't verify mileage
        
        # If we have complete vehicle attributes AND they match, use them
        if vehicle_year and vehicle_make and vehicle_model:
            if year_match and make_match and model_match:
                listing.vehicle_attributes = VehicleAttributes.from_dict(vehicle_attrs)
                logger.debug(f"Including '{listing.title}' - vehicle attributes match")
                return True
            # If vehicle attributes don't match, fall through to title-based matching
        
        # Title-based matching - include if title matches make/model
        # For year, be lenient: if not in title and we don't have vehicle attributes, still include
        if make_match and model_match:
            # Year matching: if we have vehicle year, use it; otherwise be lenient if not in title
            if request.year:
                # Only exclude if we can definitively say year doesn't match
                if vehicle_year is not None:
                    # We have vehicle year data, so check it strictly
                    if not year_match:
                        logger.debug(f"Filtered out '{listing.title}' - year mismatch: vehicle_year={vehicle_year}, requested={request.year}")
                        return False
                # If no vehicle year and not in title, be lenient and include
                logger.debug(f"Including '{listing.title}' - make/model match, year lenient (no vehicle year data)")
            else:
                # No year filter
                logger.debug(f"Including '{listing.title}' - make/model match, no year filter")
            
            # Update vehicle attributes if we have them
            if vehicle_attrs:
                listing.vehicle_attributes = VehicleAttributes.from_dict(vehicle_attrs)
            return True
        
        logger.debug(f"Filtered out '{listing.title}' - make_match={make_match}, model_match={model_match}")
        return False
    
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
        vehicle_attrs = VehicleAttributes.from_dict(vehicle_attrs_data) if vehicle_attrs_data else None
        
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
