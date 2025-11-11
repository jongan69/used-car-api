from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Literal
from enum import Enum


class Condition(str, Enum):
    """Car condition enum"""
    NEW = "NEW"
    OPEN_BOX = "OPEN_BOX"
    REFURBISHED = "REFURBISHED"
    USED = "USED"
    BROKEN = "BROKEN"
    OTHER = "OTHER"


class SortOption(str, Enum):
    """Sort options"""
    NEWEST_FIRST = "-posted"
    CLOSEST_FIRST = "distance"
    PRICE_LOW_TO_HIGH = "price"
    PRICE_HIGH_TO_LOW = "-price"


class DeliveryOption(str, Enum):
    """Delivery options"""
    PICKUP = "p"
    SHIPPING = "s"
    PICKUP_AND_SHIPPING = "p_s"


class CarSearchRequest(BaseModel):
    """Request model for car search"""
    query: Optional[str] = Field(None, max_length=200, description="Search query (e.g., 'Honda Civic', 'Mercedes CLS63'). If omitted, returns broader results.")
    state: Optional[str] = Field(None, description="State name (e.g., 'California', 'Texas')")
    city: Optional[str] = Field(None, description="City name (e.g., 'Los Angeles', 'Dallas')")
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    lon: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    limit: int = Field(50, ge=1, le=100, description="Maximum number of results")
    pickup_distance: int = Field(50, ge=1, le=500, description="Pickup distance in miles")
    price_min: Optional[int] = Field(None, ge=0, description="Minimum price in dollars")
    price_max: Optional[int] = Field(None, ge=0, description="Maximum price in dollars")
    sort: SortOption = Field(SortOption.NEWEST_FIRST, description="Sort option")
    delivery: DeliveryOption = Field(DeliveryOption.PICKUP, description="Delivery option")
    conditions: List[Condition] = Field(default_factory=list, description="Car conditions to filter by")
    
    # Vehicle-specific filters
    year: Optional[int] = Field(None, ge=1900, le=2030, description="Vehicle year")
    make: Optional[str] = Field(None, max_length=100, description="Vehicle make (e.g., 'Mercedes-Benz', 'Honda')")
    model: Optional[str] = Field(None, max_length=100, description="Vehicle model (e.g., 'CLS63', 'Civic')")
    max_miles: Optional[int] = Field(None, ge=0, description="Maximum mileage")
    min_miles: Optional[int] = Field(None, ge=0, description="Minimum mileage")
    
    @model_validator(mode='after')
    def validate_coordinates_and_location(self):
        """Validate that both lat and lon are provided together, and city requires state"""
        if self.lat is not None and self.lon is None:
            raise ValueError("Both lat and lon must be provided together")
        if self.lon is not None and self.lat is None:
            raise ValueError("Both lat and lon must be provided together")
        if self.city is not None and self.state is None:
            raise ValueError("State must be provided when city is specified")
        return self


class VehicleAttributes(BaseModel):
    """Vehicle attributes model"""
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    miles: Optional[int] = None
    color: Optional[str] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    body: Optional[str] = None
    drive_train: Optional[str] = None
    vin: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create VehicleAttributes from dict, handling year as string or int"""
        if not data:
            return None
        
        year = data.get('vehicleYear')
        if year:
            try:
                year = int(year) if isinstance(year, str) else year
            except (ValueError, TypeError):
                year = None
        
        miles = data.get('vehicleMiles')
        if miles:
            try:
                miles = int(miles) if isinstance(miles, str) else miles
            except (ValueError, TypeError):
                miles = None
        
        return cls(
            year=year,
            make=data.get('vehicleMake'),
            model=data.get('vehicleModel'),
            miles=miles,
            color=data.get('vehicleColor'),
            transmission=data.get('vehicleTransmissionClean'),
            fuel_type=data.get('vehicleFuelType'),
            body=data.get('vehicleBody'),
            drive_train=data.get('vehicleDriveTrain'),
            vin=data.get('vehicleVin')
        )


class CarListing(BaseModel):
    """Car listing response model"""
    listing_id: str
    title: str
    price: Optional[str] = None
    location_name: Optional[str] = None
    listing_url: str
    condition_text: Optional[str] = None
    image_url: Optional[str] = None
    vehicle_attributes: Optional[VehicleAttributes] = None


class CarSearchResponse(BaseModel):
    """Response model for car search"""
    total_results: int
    listings: List[CarListing]
    query: str
    filters_applied: dict


class CarDetailResponse(BaseModel):
    """Response model for car details"""
    listing_id: str
    title: str
    price: Optional[str] = None
    description: Optional[str] = None
    location_name: Optional[str] = None
    listing_url: str
    condition: Optional[str] = None
    vehicle_attributes: Optional[VehicleAttributes] = None
    photos: List[str] = []


class LocationResponse(BaseModel):
    """Response model for location"""
    state: str
    city: Optional[str] = None
    lat: float
    lon: float


class StatesResponse(BaseModel):
    """Response model for available states"""
    states: List[str]
    total: int


class CitiesResponse(BaseModel):
    """Response model for available cities"""
    cities: List[str]
    total: int
    state: str

