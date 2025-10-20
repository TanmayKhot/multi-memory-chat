#!/usr/bin/env python3
"""
Quick API test to verify the backend is working correctly
"""

import requests
import os
from dotenv import load_dotenv
from supabase import create_client
import json

# Load environment
load_dotenv()

BACKEND_URL = "http://localhost:8000"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

def test_backend_health():
    """Test if backend is responding"""
    print("\n🔍 Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend is healthy: {response.json()}")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend is not reachable: {e}")
        return False

def test_supabase_auth():
    """Test Supabase authentication"""
    print("\n🔍 Testing Supabase Authentication...")
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("✅ Supabase client created successfully")
        
        # Try to query memories table
        response = supabase.table("memories").select("*").limit(1).execute()
        print(f"✅ Successfully queried memories table (found {len(response.data)} items)")
        return True
    except Exception as e:
        print(f"❌ Supabase authentication failed: {e}")
        return False

def test_create_memory_with_auth():
    """Test creating a memory with proper authentication"""
    print("\n🔍 Testing Create Memory API (with test user)...")
    
    # First, we need to get a valid auth token
    # For testing, let's try to sign in or create a test user
    print("Note: You need to be logged in through the frontend to test this properly")
    print("The frontend stores the auth token in the session")
    
    print("\n📝 To test manually:")
    print("1. Open browser DevTools (F12)")
    print("2. Go to Network tab")
    print("3. Try to create a memory in the UI")
    print("4. Look for the POST request to /api/memories")
    print("5. Check:")
    print("   - Request URL")
    print("   - Request Headers (especially Authorization)")
    print("   - Request Payload")
    print("   - Response Status and Body")

def test_cors():
    """Test CORS configuration"""
    print("\n🔍 Testing CORS Configuration...")
    try:
        response = requests.options(
            f"{BACKEND_URL}/api/memories",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
        )
        
        if response.status_code in [200, 204]:
            print("✅ CORS preflight passed")
            print(f"   Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
            print(f"   Allow-Methods: {response.headers.get('Access-Control-Allow-Methods')}")
            print(f"   Allow-Headers: {response.headers.get('Access-Control-Allow-Headers')}")
            return True
        else:
            print(f"❌ CORS preflight failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def main():
    print("="*60)
    print("  API Diagnostic Test")
    print("="*60)
    
    results = {
        "Backend Health": test_backend_health(),
        "Supabase Auth": test_supabase_auth(),
        "CORS": test_cors(),
    }
    
    test_create_memory_with_auth()
    
    print("\n" + "="*60)
    print("  Summary")
    print("="*60)
    
    for test, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test}")
    
    print("\n" + "="*60)
    print("  Common Issues and Solutions")
    print("="*60)
    
    print("\n1. NetworkError when attempting to fetch resource:")
    print("   Causes:")
    print("   - Frontend .env.local not loaded (need to restart dev server)")
    print("   - Backend server not running")
    print("   - CORS misconfiguration")
    print("   - Wrong API URL")
    
    print("\n2. If backend is running but frontend can't reach it:")
    print("   - Restart frontend dev server:")
    print("     cd frontend && npm run dev")
    print("   - Check browser console for exact error")
    print("   - Check Network tab for failed requests")
    
    print("\n3. If authentication fails:")
    print("   - Make sure you're logged in through Supabase")
    print("   - Check that access_token is being sent in Authorization header")
    print("   - Verify token is not expired")
    
    print("\n4. Restart both servers after .env changes:")
    print("   Backend:")
    print("     cd /home/tanmay/Desktop/python-projects/mem0")
    print("     source mem0-env/bin/activate")
    print("     uvicorn app.main:app --reload")
    print("   Frontend:")
    print("     cd /home/tanmay/Desktop/python-projects/mem0/frontend")
    print("     npm run dev")
    
    print("\n5. Check browser console:")
    print("   The frontend logs detailed information about API calls")
    print("   Look for lines starting with 🔵, 📡, ✅, or ❌")

if __name__ == "__main__":
    main()

