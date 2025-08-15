#!/usr/bin/env python3
"""
Test runner for StationAgent tests.

Usage: 
    python run_tests.py mock                    # Run mock tests (no API required)
    python run_tests.py real [token] [url]     # Run real API tests
    python run_tests.py all [token] [url]      # Run both mock and real tests
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def print_usage():
    """Print usage instructions."""
    print("🧪 StationAgent Test Runner")
    print("=" * 50)
    print("Usage:")
    print("  python run_tests.py mock                    # Mock tests (no API)")
    print("  python run_tests.py real [token] [url]     # Real API tests")
    print("  python run_tests.py all [token] [url]      # Both test suites")
    print()
    print("Examples:")
    print("  python run_tests.py mock")
    print("  python run_tests.py real dev-token-123")
    print("  python run_tests.py real dev-token-123 https://api.example.com/prod")
    print("  python run_tests.py all dev-token-123")
    print()

def run_mock_tests():
    """Run mock tests."""
    try:
        from mock.test_station_agent_mock import run_mock_tests
        print("🧪 Running Mock Tests (no API required)...")
        print("=" * 50)
        return run_mock_tests()
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure tests/mock/test_station_agent_mock.py exists")
        return False
    except Exception as e:
        print(f"❌ Mock Test Error: {e}")
        return False

def run_real_tests(token=None, url=None):
    """Run real API tests."""
    try:
        from real_api.test_station_agent_real import main as run_real_tests_main
        
        # Set up environment variables if provided
        if token:
            os.environ["SHARED_STATE_TOKEN"] = token
            print(f"✅ Using provided token: {token[:10]}...")
        
        if url:
            os.environ["SHARED_STATE_URL"] = url
            print(f"✅ Using provided URL: {url}")
        
        print("🧪 Running Real API Tests...")
        print("=" * 50)
        
        # Patch sys.argv to pass parameters
        original_argv = sys.argv.copy()
        if token:
            sys.argv = ["test_station_agent_real.py", token]
            if url:
                sys.argv.append(url)
        
        try:
            run_real_tests_main()
            return True
        finally:
            sys.argv = original_argv
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure tests/real_api/test_station_agent_real.py exists")
        return False
    except Exception as e:
        print(f"❌ Real Test Error: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    test_type = sys.argv[1].lower()
    
    if test_type == "mock":
        success = run_mock_tests()
        sys.exit(0 if success else 1)
        
    elif test_type == "real":
        token = sys.argv[2] if len(sys.argv) > 2 else None
        url = sys.argv[3] if len(sys.argv) > 3 else None
        
        if not token:
            token = "dev-token-123"  # Default working token
            print(f"Using default token: {token}")
        
        success = run_real_tests(token, url)
        sys.exit(0 if success else 1)
        
    elif test_type == "all":
        token = sys.argv[2] if len(sys.argv) > 2 else None
        url = sys.argv[3] if len(sys.argv) > 3 else None
        
        print("🚀 Running Complete Test Suite")
        print("=" * 60)
        
        # Run mock tests first
        mock_success = run_mock_tests()
        print("\n" + "="*60)
        
        # Run real tests
        if not token:
            token = "dev-token-123"  # Default working token
            print(f"Using default token for real tests: {token}")
            
        real_success = run_real_tests(token, url)
        
        # Final summary
        print("\n" + "="*60)
        print("🎯 COMPLETE TEST SUMMARY")
        print("="*60)
        print(f"Mock Tests: {'✅ PASSED' if mock_success else '❌ FAILED'}")
        print(f"Real Tests: {'✅ PASSED' if real_success else '❌ FAILED'}")
        
        overall_success = mock_success and real_success
        print(f"Overall: {'🎉 ALL PASSED' if overall_success else '⚠️ SOME FAILED'}")
        
        sys.exit(0 if overall_success else 1)
        
    else:
        print(f"❌ Unknown test type: {test_type}")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main() 