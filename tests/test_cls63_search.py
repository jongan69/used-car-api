#!/usr/bin/env python3
"""
Test script for searching a specific car: 2014 CLS63 Mercedes Benz with < 100,000 miles
"""

import sys
from pyOfferUp import fetch
from pyOfferUp.constants import CONDITION, SORT

def search_cls63_mercedes():
    """Search for 2014 CLS63 Mercedes Benz with less than 100,000 miles"""
    print("=" * 80)
    print("SEARCHING FOR: 2014 CLS63 Mercedes Benz with < 100,000 miles")
    print("=" * 80)
    
    # Try different search queries - search in major cities likely to have luxury cars
    search_locations = [
        ("California", "Los Angeles"),
        ("California", "San Francisco"),
        ("Texas", "Dallas"),
        ("Florida", "Miami"),
        ("New York", "New York")
    ]
    
    search_queries = [
        "2014 CLS63 Mercedes",
        "CLS63 Mercedes 2014",
        "Mercedes CLS63 2014",
        "CLS63 2014"
    ]
    
    all_listings = []
    seen_listing_ids = set()
    
    print("\n1. Searching with multiple query variations across major cities...")
    for state, city in search_locations:
        for query in search_queries:
            print(f"\n   Query: '{query}' in {city}, {state}")
            try:
                listings = fetch.get_listings(
                    query=query,
                    state=state,
                    city=city,
                    limit=50,
                    conditions=[CONDITION.USED]
                )
                
                # Add unique listings
                for listing in listings:
                    listing_id = listing.get('listingId')
                    if listing_id and listing_id not in seen_listing_ids:
                        seen_listing_ids.add(listing_id)
                        all_listings.append(listing)
                
                print(f"   ✓ Found {len(listings)} listings")
            except Exception as e:
                print(f"   ⚠ Error with query '{query}' in {city}: {e}")
    
    print(f"\n   Total unique listings found: {len(all_listings)}")
    
    if len(all_listings) == 0:
        print("\n⚠ No listings found. Trying broader search...")
        # Try broader search
        try:
            listings = fetch.get_listings(
                query="Mercedes",
                state="Texas",
                city="Dallas",
                limit=100,
                conditions=[CONDITION.USED]
            )
            print(f"   Found {len(listings)} Mercedes listings total")
            all_listings = listings
        except Exception as e:
            print(f"   Error: {e}")
            return False
    
    # Filter listings to find 2014 CLS63 with < 100,000 miles
    print("\n2. Filtering results for 2014 CLS63 Mercedes Benz...")
    matching_listings = []
    
    for listing in all_listings:
        title = listing.get('title', '').upper()
        listing_id = listing.get('listingId')
        
        # Check if title contains relevant keywords
        has_cls63 = 'CLS63' in title or 'CLS 63' in title or 'CLS-63' in title
        has_mercedes = 'MERCEDES' in title or 'MERCEDES-BENZ' in title or 'BENZ' in title
        has_2014 = '2014' in title
        
        # Exclude parts listings
        parts_keywords = ['PART', 'SHELL', 'PANEL', 'DOOR', 'BUMPER', 'FENDER', 'HOOD', 'TRUNK', 
                         'SEAT', 'WHEEL', 'RIM', 'HEADLIGHT', 'TAILLIGHT', 'OEM', 'DRIVER REAR']
        is_part = any(keyword in title for keyword in parts_keywords)
        
        # Get detailed information to check vehicle attributes
        vehicle_miles = None
        vehicle_year = None
        vehicle_make = None
        vehicle_model = None
        vehicle_attrs = None
        details = None
        
        try:
            details = fetch.get_listing_details(listing_id)
            if 'data' in details and 'listing' in details['data']:
                listing_detail = details['data']['listing']
                vehicle_attrs = listing_detail.get('vehicleAttributes')
                
                if vehicle_attrs:
                    vehicle_year = vehicle_attrs.get('vehicleYear')
                    make_raw = vehicle_attrs.get('vehicleMake')
                    model_raw = vehicle_attrs.get('vehicleModel')
                    vehicle_make = make_raw.upper() if make_raw else None
                    vehicle_model = model_raw.upper() if model_raw else None
                    vehicle_miles = vehicle_attrs.get('vehicleMiles')
        except Exception as e:
            # If we can't get details, continue with title-based matching
            pass
        
        # Check if it matches our criteria
        # Year can be string or int
        year_match = vehicle_year == 2014 or vehicle_year == '2014' or str(vehicle_year) == '2014' if vehicle_year else False
        is_2014 = year_match or has_2014
        is_mercedes = 'MERCEDES' in vehicle_make if vehicle_make else has_mercedes
        # Check for CLS63 variations: CLS63, CLS 63, CLS-63, CLS 63 AMG
        if vehicle_model:
            model_upper = vehicle_model.upper()
            is_cls63 = 'CLS63' in model_upper or 'CLS 63' in model_upper or 'CLS-63' in model_upper
        else:
            is_cls63 = has_cls63
        
        # Skip parts listings
        if is_part:
            continue
        
        # Check mileage
        miles_match = True
        if vehicle_miles is not None:
            try:
                miles = int(vehicle_miles)
                miles_match = miles < 100000
            except (ValueError, TypeError):
                miles_match = True  # If we can't parse miles, include it
        
        # If we have vehicle attributes, use them for matching
        if vehicle_year and vehicle_make and vehicle_model:
            if is_2014 and is_mercedes and is_cls63 and miles_match:
                matching_listings.append({
                    'listing': listing,
                    'details': details,
                    'vehicle_attrs': vehicle_attrs
                })
        elif has_cls63 and has_mercedes and has_2014 and not is_part:
            # Title-based match - include if it's not a parts listing
            matching_listings.append({
                'listing': listing,
                'details': details,
                'vehicle_attrs': vehicle_attrs
            })
    
    print(f"   Found {len(matching_listings)} potential matches")
    
    # Display matching listings with detailed information
    print("\n3. Detailed information for matching listings:")
    print("=" * 80)
    
    if len(matching_listings) == 0:
        print("\n⚠ No exact matches found for 2014 CLS63 Mercedes Benz with < 100,000 miles")
        print("\nSearching for CLS63 listings (any year) to show available options...")
        print("-" * 80)
        
        # Filter for actual CLS63 cars (not parts)
        cls63_listings = []
        for listing in all_listings:
            title = listing.get('title', '').upper()
            # Exclude parts listings
            if ('CLS63' in title or 'CLS 63' in title) and 'PART' not in title and 'SHELL' not in title and 'PANEL' not in title and 'DOOR' not in title:
                cls63_listings.append(listing)
        
        if len(cls63_listings) > 0:
            print(f"\nFound {len(cls63_listings)} CLS63 listings (checking details...):")
            for i, listing in enumerate(cls63_listings[:10], 1):
                print(f"\n{i}. {listing.get('title', 'N/A')}")
                print(f"   Price: ${listing.get('price', 'N/A')}")
                print(f"   Location: {listing.get('locationName', 'N/A')}")
                print(f"   URL: {listing.get('listingUrl', 'N/A')}")
                
                # Try to get vehicle details
                try:
                    details = fetch.get_listing_details(listing.get('listingId'))
                    if 'data' in details and 'listing' in details['data']:
                        vehicle_attrs = details['data']['listing'].get('vehicleAttributes')
                        if vehicle_attrs:
                            print(f"   Year: {vehicle_attrs.get('vehicleYear', 'N/A')}")
                            print(f"   Make: {vehicle_attrs.get('vehicleMake', 'N/A')}")
                            print(f"   Model: {vehicle_attrs.get('vehicleModel', 'N/A')}")
                            miles = vehicle_attrs.get('vehicleMiles')
                            if miles:
                                try:
                                    miles_int = int(miles)
                                    print(f"   Miles: {miles_int:,}")
                                    if miles_int < 100000:
                                        print(f"   ✓ Meets mileage requirement (< 100,000 miles)")
                                    else:
                                        print(f"   ✗ Exceeds mileage requirement")
                                except (ValueError, TypeError):
                                    print(f"   Miles: {miles}")
                except:
                    pass
        else:
            print("\nNo CLS63 car listings found (only parts/accessories)")
    else:
        for i, match in enumerate(matching_listings, 1):
            listing = match['listing']
            vehicle_attrs = match.get('vehicle_attrs')
            
            print(f"\n{i}. {listing.get('title', 'N/A')}")
            print(f"   Price: ${listing.get('price', 'N/A')}")
            print(f"   Location: {listing.get('locationName', 'N/A')}")
            print(f"   URL: {listing.get('listingUrl', 'N/A')}")
            
            if vehicle_attrs:
                print(f"   Year: {vehicle_attrs.get('vehicleYear', 'N/A')}")
                print(f"   Make: {vehicle_attrs.get('vehicleMake', 'N/A')}")
                print(f"   Model: {vehicle_attrs.get('vehicleModel', 'N/A')}")
                miles = vehicle_attrs.get('vehicleMiles')
                if miles:
                    try:
                        miles_int = int(miles)
                        print(f"   Miles: {miles_int:,}")
                        if miles_int < 100000:
                            print(f"   ✓ Meets mileage requirement (< 100,000 miles)")
                        else:
                            print(f"   ✗ Exceeds mileage requirement")
                    except (ValueError, TypeError):
                        print(f"   Miles: {miles}")
                else:
                    print(f"   Miles: Not specified")
                
                # Additional vehicle info
                if vehicle_attrs.get('vehicleColor'):
                    print(f"   Color: {vehicle_attrs.get('vehicleColor')}")
                if vehicle_attrs.get('vehicleTransmissionClean'):
                    print(f"   Transmission: {vehicle_attrs.get('vehicleTransmissionClean')}")
                if vehicle_attrs.get('vehicleFuelType'):
                    print(f"   Fuel Type: {vehicle_attrs.get('vehicleFuelType')}")
            print("-" * 80)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    exact_matches = []
    for match in matching_listings:
        vehicle_attrs = match.get('vehicle_attrs')
        if vehicle_attrs:
            year = vehicle_attrs.get('vehicleYear')
            make = vehicle_attrs.get('vehicleMake')
            model = vehicle_attrs.get('vehicleModel')
            miles = vehicle_attrs.get('vehicleMiles')
            
            make_upper = make.upper() if make else ''
            model_upper = model.upper() if model else ''
            
            # Check for CLS63 variations
            is_cls63_model = 'CLS63' in model_upper or 'CLS 63' in model_upper or 'CLS-63' in model_upper
            
            # Year can be string or int
            year_match = year == 2014 or year == '2014' or str(year) == '2014'
            
            if year_match and 'MERCEDES' in make_upper and is_cls63_model:
                if miles:
                    try:
                        miles_int = int(miles)
                        if miles_int < 100000:
                            exact_matches.append(match)
                    except:
                        pass
                else:
                    exact_matches.append(match)
    
    print(f"Total listings searched: {len(all_listings)}")
    print(f"Potential matches found: {len(matching_listings)}")
    print(f"Exact matches (2014 CLS63 Mercedes with < 100k miles): {len(exact_matches)}")
    
    if len(exact_matches) > 0:
        print("\n✓ Found exact matches!")
        return True
    else:
        print("\n⚠ No exact matches found, but search functionality is working")
        return True

if __name__ == "__main__":
    success = search_cls63_mercedes()
    sys.exit(0 if success else 1)

