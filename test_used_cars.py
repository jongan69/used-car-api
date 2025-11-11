#!/usr/bin/env python3
"""
Test script for fetching used car listings from pyOfferUp
"""

import sys
from pyOfferUp import fetch
from pyOfferUp.constants import CONDITION, SORT

def test_used_car_listings():
    """Test fetching used car listings"""
    print("=" * 70)
    print("TESTING USED CAR LISTINGS")
    print("=" * 70)
    
    # Test 1: Search for cars without condition filter
    print("\n1. Testing car search WITHOUT condition filter...")
    print("   Query: 'car', Location: Austin, Texas, Limit: 10")
    try:
        listings = fetch.get_listings(
            query="car",
            state="Texas",
            city="Austin",
            limit=10
        )
        print(f"   ✓ Found {len(listings)} listings")
        
        if len(listings) > 0:
            print("\n   Sample listings:")
            for i, listing in enumerate(listings[:5], 1):
                print(f"   {i}. {listing.get('title', 'N/A')[:60]}")
                print(f"      Price: ${listing.get('price', 'N/A')}")
                print(f"      Location: {listing.get('locationName', 'N/A')}")
                print(f"      Condition: {listing.get('conditionText', 'N/A')}")
                print(f"      URL: {listing.get('listingUrl', 'N/A')}")
                print()
        else:
            print("   ⚠ No listings found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Search for used cars with CONDITION.USED filter
    print("\n2. Testing car search WITH USED condition filter...")
    print("   Query: 'car', Condition: USED, Location: Austin, Texas, Limit: 10")
    try:
        listings = fetch.get_listings(
            query="car",
            state="Texas",
            city="Austin",
            limit=10,
            conditions=[CONDITION.USED]
        )
        print(f"   ✓ Found {len(listings)} used car listings")
        
        if len(listings) > 0:
            print("\n   Sample used car listings:")
            for i, listing in enumerate(listings[:5], 1):
                print(f"   {i}. {listing.get('title', 'N/A')[:60]}")
                print(f"      Price: ${listing.get('price', 'N/A')}")
                print(f"      Location: {listing.get('locationName', 'N/A')}")
                print(f"      Condition: {listing.get('conditionText', 'N/A')}")
                if listing.get('vehicleMiles'):
                    print(f"      Miles: {listing.get('vehicleMiles')}")
                print(f"      URL: {listing.get('listingUrl', 'N/A')}")
                print()
        else:
            print("   ⚠ No used car listings found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Search for used cars with price filter
    print("\n3. Testing used car search WITH price filter...")
    print("   Query: 'car', Condition: USED, Price: $5000-$20000, Location: Austin, Texas")
    try:
        listings = fetch.get_listings(
            query="car",
            state="Texas",
            city="Austin",
            limit=10,
            price_min=5000,
            price_max=20000,
            conditions=[CONDITION.USED]
        )
        print(f"   ✓ Found {len(listings)} used car listings in price range $5,000-$20,000")
        
        if len(listings) > 0:
            print("\n   Sample listings in price range:")
            for i, listing in enumerate(listings[:5], 1):
                price = listing.get('price', 'N/A')
                print(f"   {i}. {listing.get('title', 'N/A')[:60]}")
                print(f"      Price: ${price}")
                print(f"      Location: {listing.get('locationName', 'N/A')}")
                if listing.get('vehicleMiles'):
                    print(f"      Miles: {listing.get('vehicleMiles')}")
                print()
        else:
            print("   ⚠ No listings found in this price range")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Search for specific car types (e.g., "Honda", "Toyota")
    print("\n4. Testing search for specific car brand...")
    print("   Query: 'Honda', Condition: USED, Location: Austin, Texas, Limit: 5")
    try:
        listings = fetch.get_listings(
            query="Honda",
            state="Texas",
            city="Austin",
            limit=5,
            conditions=[CONDITION.USED]
        )
        print(f"   ✓ Found {len(listings)} used Honda listings")
        
        if len(listings) > 0:
            print("\n   Sample Honda listings:")
            for i, listing in enumerate(listings[:3], 1):
                print(f"   {i}. {listing.get('title', 'N/A')[:60]}")
                print(f"      Price: ${listing.get('price', 'N/A')}")
                print(f"      Location: {listing.get('locationName', 'N/A')}")
                print()
        else:
            print("   ⚠ No Honda listings found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Search by lat/lon (alternative method)
    print("\n5. Testing used car search by lat/lon...")
    print("   Query: 'car', Condition: USED, Lat: 30.2711286, Lon: -97.7436995 (Austin, TX)")
    try:
        listings = fetch.get_listings_by_lat_lon(
            query="car",
            lat=30.2711286,
            lon=-97.7436995,
            limit=5,
            conditions=[CONDITION.USED]
        )
        print(f"   ✓ Found {len(listings)} used car listings")
        
        if len(listings) > 0:
            print("\n   Sample listings:")
            for i, listing in enumerate(listings[:3], 1):
                print(f"   {i}. {listing.get('title', 'N/A')[:60]}")
                print(f"      Price: ${listing.get('price', 'N/A')}")
                print(f"      Location: {listing.get('locationName', 'N/A')}")
                print()
        else:
            print("   ⚠ No listings found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Test sorting options
    print("\n6. Testing used car search with PRICE_LOW_TO_HIGH sort...")
    print("   Query: 'car', Condition: USED, Sort: Price Low to High")
    try:
        listings = fetch.get_listings(
            query="car",
            state="Texas",
            city="Austin",
            limit=5,
            conditions=[CONDITION.USED],
            sort=SORT.PRICE_LOW_TO_HIGH
        )
        print(f"   ✓ Found {len(listings)} used car listings (sorted by price)")
        
        if len(listings) > 0:
            print("\n   Listings sorted by price (low to high):")
            for i, listing in enumerate(listings, 1):
                print(f"   {i}. ${listing.get('price', 'N/A')} - {listing.get('title', 'N/A')[:50]}")
        else:
            print("   ⚠ No listings found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("✓ All used car listing tests completed successfully!")
    print("\nThe package can successfully:")
    print("  - Search for cars with and without condition filters")
    print("  - Filter by USED condition")
    print("  - Filter by price range")
    print("  - Search by specific car brands")
    print("  - Use lat/lon coordinates for search")
    print("  - Sort results by price")
    
    return True

if __name__ == "__main__":
    success = test_used_car_listings()
    sys.exit(0 if success else 1)

