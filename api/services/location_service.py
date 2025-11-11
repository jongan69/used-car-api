import asyncio
import logging
from typing import List, Tuple, Optional

from pyOfferUp import places

logger = logging.getLogger(__name__)


class LocationService:
    """Service for location-related operations"""
    
    async def get_available_states(self) -> List[str]:
        """Get list of available states"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, places.available_states)
    
    async def get_available_cities(self, state: str) -> List[str]:
        """Get list of available cities for a state"""
        loop = asyncio.get_event_loop()
        try:
            cities = await loop.run_in_executor(None, places.available_cities, state)
            return cities
        except Exception as e:
            raise ValueError(f"Invalid state: {state}")
    
    async def get_coordinates(self, state: str, city: Optional[str] = None) -> Tuple[float, float]:
        """Get coordinates for a state or city"""
        loop = asyncio.get_event_loop()
        try:
            lat, lon = await loop.run_in_executor(None, places.get_lat_lon, state, city)
            return lat, lon
        except Exception as e:
            raise ValueError(f"Invalid location: {state}" + (f", {city}" if city else ""))
