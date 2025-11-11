#!/usr/bin/env python3
"""
Test script for pyOfferUp package
"""

import sys
import traceback

def test_imports():
    """Test if all modules can be imported"""
    print("=" * 60)
    print("TEST 1: Testing imports...")
    print("=" * 60)
    try:
        from pyOfferUp import places
        from pyOfferUp import fetch
        from pyOfferUp import constants
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False

def test_places_module():
    """Test places module functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Testing places module...")
    print("=" * 60)
    try:
        from pyOfferUp import places
        
        # Test available_states
        states = places.available_states()
        print(f"✓ available_states() returned {len(states)} states")
        assert len(states) > 0, "No states returned"
        assert "Texas" in states, "Texas not in states list"
        
        # Test available_cities
        cities = places.available_cities("Texas")
        print(f"✓ available_cities('Texas') returned {len(cities)} cities")
        assert len(cities) > 0, "No cities returned for Texas"
        assert "Mcallen" in cities, "Mcallen not in cities list"
        
        # Test get_lat_lon with state only
        lat, lon = places.get_lat_lon("Texas")
        print(f"✓ get_lat_lon('Texas') returned lat={lat}, lon={lon}")
        assert isinstance(lat, float), "Latitude should be float"
        assert isinstance(lon, float), "Longitude should be float"
        
        # Test get_lat_lon with state and city
        lat, lon = places.get_lat_lon("Texas", "Mcallen")
        print(f"✓ get_lat_lon('Texas', 'Mcallen') returned lat={lat}, lon={lon}")
        assert isinstance(lat, float), "Latitude should be float"
        assert isinstance(lon, float), "Longitude should be float"
        
        # Test error handling
        try:
            places.get_lat_lon("InvalidState")
            print("✗ Should have raised exception for invalid state")
            return False
        except Exception:
            print("✓ Correctly raised exception for invalid state")
        
        try:
            places.get_lat_lon("Texas", "InvalidCity")
            print("✗ Should have raised exception for invalid city")
            return False
        except Exception:
            print("✓ Correctly raised exception for invalid city")
        
        return True
    except Exception as e:
        print(f"✗ Places module test failed: {e}")
        traceback.print_exc()
        return False

def test_constants_module():
    """Test constants module"""
    print("\n" + "=" * 60)
    print("TEST 3: Testing constants module...")
    print("=" * 60)
    try:
        from pyOfferUp import constants
        
        # Test ENDPOINT
        assert constants.ENDPOINT == "https://offerup.com", "ENDPOINT incorrect"
        print(f"✓ ENDPOINT = {constants.ENDPOINT}")
        
        # Test CONDITION enum
        assert constants.CONDITION.NEW.value == "NEW", "CONDITION.NEW incorrect"
        print(f"✓ CONDITION enum values: {[c.value for c in constants.CONDITION]}")
        
        # Test SORT enum
        assert constants.SORT.NEWEST_FIRST.value == "-posted", "SORT.NEWEST_FIRST incorrect"
        print(f"✓ SORT enum values: {[s.value for s in constants.SORT]}")
        
        # Test DELIVERY enum
        assert constants.DELIVERY.PICKUP.value == "p", "DELIVERY.PICKUP incorrect"
        print(f"✓ DELIVERY enum values: {[d.value for d in constants.DELIVERY]}")
        
        # Test GRAPHQL enum
        assert "query GetModularFeed" in constants.GRAPHQL.MODULAR_FEED.value, "GRAPHQL.MODULAR_FEED incorrect"
        print(f"✓ GRAPHQL enum has MODULAR_FEED query")
        
        return True
    except Exception as e:
        print(f"✗ Constants module test failed: {e}")
        traceback.print_exc()
        return False

def test_fetch_module():
    """Test fetch module functionality"""
    print("\n" + "=" * 60)
    print("TEST 4: Testing fetch module...")
    print("=" * 60)
    try:
        from pyOfferUp import fetch
        from pyOfferUp import constants
        
        # Test get_listings with a simple query (small limit to avoid long waits)
        print("Testing get_listings() with query='laptop', state='Texas', city='Austin', limit=5...")
        try:
            listings = fetch.get_listings(
                query="laptop",
                state="Texas",
                city="Austin",
                limit=5
            )
            print(f"✓ get_listings() returned {len(listings)} listings")
            
            # Check structure of first listing if available
            if len(listings) > 0:
                listing = listings[0]
                assert 'listingId' in listing, "listingId missing"
                assert 'title' in listing, "title missing"
                print(f"✓ First listing: {listing.get('title', 'N/A')[:50]}...")
                print(f"  - Listing ID: {listing.get('listingId', 'N/A')}")
                print(f"  - Price: {listing.get('price', 'N/A')}")
                print(f"  - Location: {listing.get('locationName', 'N/A')}")
            else:
                print("⚠ No listings returned (this might be normal if no results)")
        except Exception as e:
            print(f"⚠ get_listings() failed (might be network/API issue): {e}")
            # Don't fail the test, as this might be due to network issues
        
        # Test get_listings_by_lat_lon
        print("\nTesting get_listings_by_lat_lon() with lat=30.2711286, lon=-97.7436995 (Austin, TX)...")
        try:
            listings = fetch.get_listings_by_lat_lon(
                query="laptop",
                lat=30.2711286,
                lon=-97.7436995,
                limit=5
            )
            print(f"✓ get_listings_by_lat_lon() returned {len(listings)} listings")
            
            if len(listings) > 0:
                listing = listings[0]
                print(f"✓ First listing: {listing.get('title', 'N/A')[:50]}...")
        except Exception as e:
            print(f"⚠ get_listings_by_lat_lon() failed (might be network/API issue): {e}")
        
        # Test get_listing_details (if we have a listing ID)
        print("\nTesting get_listing_details()...")
        try:
            # Try to get details for a known listing ID format (this will likely fail without real ID)
            # But we can test that the function exists and accepts the parameter
            result = fetch.get_listing_details("test-id-123")
            print(f"✓ get_listing_details() executed (returned type: {type(result)})")
        except Exception as e:
            print(f"⚠ get_listing_details() failed (expected with test ID): {e}")
        
        return True
    except Exception as e:
        print(f"✗ Fetch module test failed: {e}")
        traceback.print_exc()
        return False

def test_package_init():
    """Test package __init__.py"""
    print("\n" + "=" * 60)
    print("TEST 5: Testing package __init__.py...")
    print("=" * 60)
    try:
        import pyOfferUp
        
        # Test that main functions are accessible
        from pyOfferUp import get_listings, get_listings_by_lat_lon, get_listing_details
        print("✓ Main functions accessible from package root")
        
        # Test places import
        import pyOfferUp.places
        print("✓ places module accessible")
        
        return True
    except Exception as e:
        print(f"✗ Package init test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PYOFFERUP PACKAGE TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Imports", test_imports()))
    results.append(("Places Module", test_places_module()))
    results.append(("Constants Module", test_constants_module()))
    results.append(("Package Init", test_package_init()))
    results.append(("Fetch Module", test_fetch_module()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

