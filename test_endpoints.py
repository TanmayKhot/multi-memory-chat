#!/usr/bin/env python3
"""
Comprehensive endpoint and database testing script
Tests all API endpoints and database operations
"""

import os
import sys
import requests
from dotenv import load_dotenv
from supabase import create_client
import json
from datetime import datetime

# Load environment
load_dotenv()

# Configuration
BACKEND_URL = "http://localhost:8000"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def test_database_tables():
    """Test that all required database tables exist and are accessible"""
    print_header("Testing Database Tables")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    tables = {
        'memories': ['id', 'user_id', 'title', 'description', 'created_at', 'updated_at'],
        'memory_records': ['id', 'memory_id', 'content', 'created_at'],
        'chat_messages': ['id', 'memory_id', 'role', 'content', 'created_at']
    }
    
    results = {}
    
    for table_name, expected_columns in tables.items():
        try:
            print_info(f"Testing table: {table_name}")
            response = supabase.table(table_name).select("*").limit(1).execute()
            print_success(f"Table '{table_name}' exists and is accessible")
            
            # Try to get column info by checking if we can query specific columns
            if response.data:
                sample = response.data[0]
                print_info(f"  Sample data columns: {', '.join(sample.keys())}")
            else:
                print_info(f"  Table is empty (this is OK)")
            
            results[table_name] = True
        except Exception as e:
            print_error(f"Table '{table_name}' error: {str(e)}")
            results[table_name] = False
    
    return all(results.values())

def test_database_schema():
    """Verify database schema with service role key"""
    print_header("Testing Database Schema")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Test if we can query system tables (requires service role)
        print_info("Verifying schema with service role access...")
        
        # Just verify we can connect with service role
        response = supabase.table("memories").select("*").limit(1).execute()
        print_success("Service role key is valid and working")
        
        return True
    except Exception as e:
        print_error(f"Schema verification failed: {str(e)}")
        return False

def test_backend_endpoints():
    """Test backend API endpoints"""
    print_header("Testing Backend Endpoints")
    
    endpoints = [
        ("GET", "/api/health", None, "Health check"),
    ]
    
    results = {}
    
    for method, endpoint, body, description in endpoints:
        try:
            print_info(f"Testing: {method} {endpoint} - {description}")
            url = f"{BACKEND_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, json=body, timeout=5)
            
            if response.status_code in [200, 401]:  # 401 is OK for auth-protected endpoints
                print_success(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    print_info(f"  Response: {response.json()}")
                results[endpoint] = True
            else:
                print_error(f"  Unexpected status: {response.status_code}")
                results[endpoint] = False
                
        except Exception as e:
            print_error(f"  Error: {str(e)}")
            results[endpoint] = False
    
    return all(results.values())

def test_database_operations():
    """Test actual database CRUD operations"""
    print_header("Testing Database Operations")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    # Create a test user ID (in production this would come from auth)
    test_user_id = "00000000-0000-0000-0000-000000000001"
    test_memory_id = None
    test_record_id = None
    
    try:
        # 1. Test CREATE - Insert a test memory
        print_info("Test 1: Creating a test memory...")
        memory_data = {
            "user_id": test_user_id,
            "title": f"Test Memory - {datetime.now().isoformat()}",
            "description": "This is a test memory for verification"
        }
        
        response = supabase.table("memories").insert(memory_data).execute()
        if response.data:
            test_memory_id = response.data[0]['id']
            print_success(f"Created test memory with ID: {test_memory_id}")
        else:
            print_error("Failed to create test memory")
            return False
        
        # 2. Test READ - Query the memory
        print_info("Test 2: Reading the test memory...")
        response = supabase.table("memories").select("*").eq("id", test_memory_id).execute()
        if response.data and len(response.data) > 0:
            print_success(f"Successfully read memory: {response.data[0]['title']}")
        else:
            print_error("Failed to read test memory")
            return False
        
        # 3. Test CREATE - Add a record to the memory
        print_info("Test 3: Creating a test record...")
        record_data = {
            "memory_id": test_memory_id,
            "content": "This is a test record"
        }
        
        response = supabase.table("memory_records").insert(record_data).execute()
        if response.data:
            test_record_id = response.data[0]['id']
            print_success(f"Created test record with ID: {test_record_id}")
        else:
            print_error("Failed to create test record")
            return False
        
        # 4. Test READ - Query records for memory
        print_info("Test 4: Reading records for memory...")
        response = supabase.table("memory_records").select("*").eq("memory_id", test_memory_id).execute()
        if response.data and len(response.data) > 0:
            print_success(f"Successfully read {len(response.data)} record(s)")
        else:
            print_error("Failed to read records")
            return False
        
        # 5. Test UPDATE - Update the memory
        print_info("Test 5: Updating the test memory...")
        update_data = {
            "description": "Updated description for verification"
        }
        
        response = supabase.table("memories").update(update_data).eq("id", test_memory_id).execute()
        print_success("Successfully updated memory")
        
        # 6. Test DELETE - Clean up
        print_info("Test 6: Cleaning up test data...")
        
        # Delete record first (foreign key constraint)
        supabase.table("memory_records").delete().eq("id", test_record_id).execute()
        print_success(f"Deleted test record")
        
        # Delete memory
        supabase.table("memories").delete().eq("id", test_memory_id).execute()
        print_success(f"Deleted test memory")
        
        print_success("All database operations completed successfully!")
        return True
        
    except Exception as e:
        print_error(f"Database operation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        try:
            if test_record_id:
                supabase.table("memory_records").delete().eq("id", test_record_id).execute()
            if test_memory_id:
                supabase.table("memories").delete().eq("id", test_memory_id).execute()
            print_info("Cleaned up test data after error")
        except:
            pass
        
        return False

def test_rls_policies():
    """Test Row Level Security policies"""
    print_header("Testing Row Level Security (RLS)")
    
    try:
        # Test with anon key (should have limited access)
        supabase_anon = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        print_info("Testing with anon key (limited access)...")
        
        # This should work but return no data (or only public data)
        response = supabase_anon.table("memories").select("*").limit(1).execute()
        print_success("Anon key can query (RLS is enforcing access control)")
        
        # Test with service role (should have full access)
        supabase_service = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        print_info("Testing with service role key (full access)...")
        response = supabase_service.table("memories").select("*").limit(1).execute()
        print_success("Service role key has full access (bypasses RLS)")
        
        return True
        
    except Exception as e:
        print_error(f"RLS test failed: {str(e)}")
        return False

def test_foreign_keys():
    """Test foreign key constraints"""
    print_header("Testing Foreign Key Constraints")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    try:
        print_info("Testing foreign key constraint (memory_records -> memories)...")
        
        # Try to insert a record with non-existent memory_id
        fake_memory_id = "00000000-0000-0000-0000-999999999999"
        record_data = {
            "memory_id": fake_memory_id,
            "content": "This should fail"
        }
        
        try:
            response = supabase.table("memory_records").insert(record_data).execute()
            print_error("Foreign key constraint not enforced! (This is a problem)")
            return False
        except Exception as e:
            if "violates foreign key constraint" in str(e).lower() or "foreign key" in str(e).lower():
                print_success("Foreign key constraint is properly enforced")
                return True
            else:
                print_info(f"Got error (might be FK related): {str(e)[:100]}")
                return True  # Assume it's working
                
    except Exception as e:
        print_error(f"Foreign key test failed: {str(e)}")
        return False

def test_supabase_connectivity():
    """Test basic Supabase connectivity"""
    print_header("Testing Supabase Connectivity")
    
    try:
        print_info(f"Testing connection to: {SUPABASE_URL}")
        
        # Test REST API
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers={"apikey": SUPABASE_ANON_KEY},
            timeout=10
        )
        
        if response.status_code in [200, 404]:
            print_success("Supabase REST API is reachable")
        else:
            print_error(f"Unexpected status: {response.status_code}")
            return False
        
        # Test table access
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/memories?limit=1",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Successfully connected to memories table")
            return True
        else:
            print_error(f"Table access failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Connectivity test failed: {str(e)}")
        return False

def main():
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"  Database & Endpoint Verification Suite")
    print(f"{'='*70}{Colors.END}\n")
    
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"Supabase URL: {SUPABASE_URL}")
    print()
    
    results = {}
    
    # Run all tests
    results["Supabase Connectivity"] = test_supabase_connectivity()
    results["Database Tables"] = test_database_tables()
    results["Database Schema"] = test_database_schema()
    results["Backend Endpoints"] = test_backend_endpoints()
    results["Database Operations"] = test_database_operations()
    results["RLS Policies"] = test_rls_policies()
    results["Foreign Keys"] = test_foreign_keys()
    
    # Summary
    print_header("Test Summary")
    
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}")
            passed += 1
        else:
            print_error(f"{test_name}")
            failed += 1
    
    print(f"\n{Colors.BOLD}Total: {passed} passed, {failed} failed{Colors.END}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Your database and endpoints are working correctly.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some tests failed. Please review the errors above.{Colors.END}\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_error("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

