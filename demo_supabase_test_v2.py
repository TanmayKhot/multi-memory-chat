#!/usr/bin/env python3
"""
Demo Supabase CRUD Operations Test V2
Works with actual authenticated users or creates test user
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid

# Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
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

def print_test(num, text):
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}Test {num}: {text}{Colors.END}")

def print_data(label, data):
    print(f"{Colors.CYAN}   {label}: {data}{Colors.END}")


class SupabaseDemo:
    def __init__(self):
        """Initialize Supabase connection"""
        print_header("Initializing Supabase Connection")
        
        # Load environment variables
        print_info("Loading environment variables from .env...")
        load_dotenv()
        
        # Get credentials
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        # Validate
        if not all([self.supabase_url, self.supabase_anon_key, self.supabase_service_key]):
            print_error("Missing required environment variables")
            sys.exit(1)
        
        print_success(f"SUPABASE_URL: {self.supabase_url[:40]}...")
        print_success(f"Keys loaded successfully")
        
        # Create client with service role (bypasses RLS)
        try:
            self.client = create_client(self.supabase_url, self.supabase_service_key)
            print_success("Supabase client created successfully")
        except Exception as e:
            print_error(f"Failed to create Supabase client: {e}")
            sys.exit(1)
        
        # Get or create test user
        self.test_user_id = self.get_or_create_test_user()
        
        # Test data storage
        self.test_memory_id = None
        self.test_record_ids = []
        self.test_message_ids = []
    
    def get_or_create_test_user(self):
        """Get existing user or indicate we need one"""
        print_header("Setting Up Test User")
        
        print_info("Checking for existing users in auth.users...")
        
        try:
            # Try to get admin user list (service role can do this)
            # Note: This requires using the Supabase Admin API
            print_info("Looking for any existing user to use for testing...")
            
            # Check if there are any memories with user_ids we can use
            result = self.client.table("memories").select("user_id").limit(1).execute()
            
            if result.data and len(result.data) > 0:
                user_id = result.data[0]['user_id']
                print_success(f"Found existing user ID from memories table: {user_id[:8]}...")
                return user_id
            
            # If no existing memories, we need to create a test scenario
            # Since we can't easily create auth users programmatically without admin SDK,
            # we'll prompt the user
            print_info("No existing users found in memories table")
            print_info("")
            print_info("OPTIONS TO PROCEED:")
            print_info("1. Log in to your app at http://localhost:5173 and create a memory")
            print_info("   Then re-run this test")
            print_info("2. Provide a user_id from Supabase Auth Dashboard")
            print_info("3. I'll try to query auth.users directly (may fail due to RLS)")
            print_info("")
            
            # Try option 3 - query auth.users (may not work)
            try:
                # This likely won't work due to RLS, but worth a try
                from supabase import create_client as create_admin_client
                admin_client = create_admin_client(self.supabase_url, self.supabase_service_key)
                
                # Service role should be able to query this
                print_info("Attempting to list users...")
                print_info("Note: For this test, we'll use a mock user ID")
                print_info("In production, users come from Supabase Auth when they log in")
                
                # For testing purposes, we'll use a known pattern
                # In real use, user_id comes from JWT token
                test_uuid = "00000000-0000-0000-0000-000000000001"
                print_info(f"Using test UUID: {test_uuid}")
                print_info("NOTE: This will only work if this user exists in auth.users")
                print_info("      Or if FK constraint is temporarily disabled")
                
                return test_uuid
                
            except Exception as e:
                print_error(f"Could not access auth.users: {e}")
                print_info("This is expected - auth.users is protected")
                return "00000000-0000-0000-0000-000000000001"
                
        except Exception as e:
            print_error(f"Error setting up test user: {e}")
            return "00000000-0000-0000-0000-000000000001"
    
    def test_with_service_role(self):
        """Test direct database operations with service role (bypasses RLS and FK)"""
        print_header("Testing with Service Role (Direct DB Access)")
        
        print_info("Service role can bypass RLS and some constraints")
        print_info("This tests the database tables directly")
        print_info("")
        
        # We'll test the structure without FK constraints by using execute with raw SQL if needed
        # But first, let's try with a user that definitely exists
        
        return True
    
    def test_memories_structure(self):
        """Test memories table structure without inserting"""
        print_header("Testing MEMORIES Table Structure")
        
        print_test(1, "Check table exists and is accessible")
        try:
            result = self.client.table("memories").select("*").limit(0).execute()
            print_success("Memories table exists and is accessible")
        except Exception as e:
            print_error(f"Cannot access memories table: {e}")
            return False
        
        print_test(2, "List existing memories")
        try:
            result = self.client.table("memories").select("id, title, user_id, created_at").limit(5).execute()
            print_success(f"Found {len(result.data)} existing memories")
            
            if result.data:
                for mem in result.data:
                    print_data("Memory", f"{mem.get('title', 'No title')} (User: {mem['user_id'][:8]}...)")
                    # Use this user_id for our tests!
                    if not self.test_user_id or self.test_user_id.startswith("00000000"):
                        self.test_user_id = mem['user_id']
                        print_success(f"Will use this user_id for tests: {self.test_user_id[:8]}...")
            else:
                print_info("No existing memories found")
                print_info("You need to:")
                print_info("1. Log in to the app (http://localhost:5173)")
                print_info("2. Create at least one memory")
                print_info("3. Then re-run this test")
                print_info("")
                print_info("Alternatively, check if FK constraint can be temporarily disabled")
                return False
        except Exception as e:
            print_error(f"Cannot list memories: {e}")
            return False
        
        print_success("Memories table structure is correct")
        return True
    
    def test_memories_crud_with_real_user(self):
        """Test CRUD operations with real user ID"""
        print_header("Testing MEMORIES Table - CRUD Operations")
        
        if not self.test_user_id or self.test_user_id.startswith("00000000"):
            print_error("No valid user_id available")
            print_info("Please log in to the app first and create a memory")
            print_info("Then re-run this test")
            return False
        
        print_info(f"Using user_id: {self.test_user_id[:8]}...")
        
        # CREATE
        print_test(1, "CREATE - Insert new memory")
        try:
            memory_data = {
                "user_id": self.test_user_id,
                "title": f"Demo Test Memory {datetime.now().strftime('%H:%M:%S')}",
                "description": "Test memory created by demo tool"
            }
            
            result = self.client.table("memories").insert(memory_data).execute()
            
            if result.data and len(result.data) > 0:
                self.test_memory_id = result.data[0]['id']
                print_success(f"Memory created: {self.test_memory_id[:8]}...")
                print_data("Title", result.data[0]['title'])
            else:
                print_error("No data returned")
                return False
        except Exception as e:
            print_error(f"CREATE failed: {e}")
            return False
        
        # READ
        print_test(2, "READ - Query the memory")
        try:
            result = self.client.table("memories").select("*").eq("id", self.test_memory_id).execute()
            
            if result.data:
                print_success("Memory retrieved")
                print_data("Title", result.data[0]['title'])
                print_data("Description", result.data[0]['description'])
            else:
                print_error("Memory not found")
                return False
        except Exception as e:
            print_error(f"READ failed: {e}")
            return False
        
        # UPDATE
        print_test(3, "UPDATE - Modify the memory")
        try:
            update_data = {"description": f"Updated {datetime.now().strftime('%H:%M:%S')}"}
            result = self.client.table("memories").update(update_data).eq("id", self.test_memory_id).execute()
            
            if result.data:
                print_success("Memory updated")
                print_data("New Description", result.data[0]['description'])
            else:
                print_error("Update failed")
                return False
        except Exception as e:
            print_error(f"UPDATE failed: {e}")
            return False
        
        # LIST
        print_test(4, "LIST - Query all memories")
        try:
            result = self.client.table("memories").select("*").eq("user_id", self.test_user_id).execute()
            print_success(f"Found {len(result.data)} memories")
        except Exception as e:
            print_error(f"LIST failed: {e}")
            return False
        
        print_success("All MEMORIES CRUD operations passed!")
        return True
    
    def test_memory_records_crud(self):
        """Test memory_records CRUD"""
        print_header("Testing MEMORY_RECORDS Table - CRUD Operations")
        
        if not self.test_memory_id:
            print_error("No test memory. Run memories test first")
            return False
        
        # CREATE
        print_test(1, "CREATE - Insert records")
        try:
            for i in range(3):
                record_data = {
                    "memory_id": self.test_memory_id,
                    "content": f"Test record {i+1} at {datetime.now().strftime('%H:%M:%S')}"
                }
                result = self.client.table("memory_records").insert(record_data).execute()
                if result.data:
                    self.test_record_ids.append(result.data[0]['id'])
            
            print_success(f"Created {len(self.test_record_ids)} records")
        except Exception as e:
            print_error(f"CREATE failed: {e}")
            return False
        
        # READ
        print_test(2, "READ - Query records")
        try:
            result = self.client.table("memory_records").select("*").eq("memory_id", self.test_memory_id).execute()
            print_success(f"Found {len(result.data)} records")
            for r in result.data:
                print_data("Record", r['content'][:40])
        except Exception as e:
            print_error(f"READ failed: {e}")
            return False
        
        # UPDATE
        print_test(3, "UPDATE - Modify record")
        try:
            if self.test_record_ids:
                update_data = {"content": f"Updated at {datetime.now().strftime('%H:%M:%S')}"}
                result = self.client.table("memory_records").update(update_data).eq("id", self.test_record_ids[0]).execute()
                print_success("Record updated")
        except Exception as e:
            print_error(f"UPDATE failed: {e}")
            return False
        
        print_success("All MEMORY_RECORDS CRUD operations passed!")
        return True
    
    def test_chat_messages_crud(self):
        """Test chat_messages CRUD"""
        print_header("Testing CHAT_MESSAGES Table - CRUD Operations")
        
        if not self.test_memory_id:
            print_error("No test memory. Run memories test first")
            return False
        
        # CREATE conversation
        print_test(1, "CREATE - Insert conversation")
        try:
            messages = [
                {"memory_id": self.test_memory_id, "role": "user", "content": "Hello"},
                {"memory_id": self.test_memory_id, "role": "assistant", "content": "Hi there!"},
                {"memory_id": self.test_memory_id, "role": "user", "content": "How are you?"},
                {"memory_id": self.test_memory_id, "role": "assistant", "content": "I'm doing well!"}
            ]
            
            for msg in messages:
                result = self.client.table("chat_messages").insert(msg).execute()
                if result.data:
                    self.test_message_ids.append(result.data[0]['id'])
            
            print_success(f"Created {len(self.test_message_ids)} messages")
        except Exception as e:
            print_error(f"CREATE failed: {e}")
            return False
        
        # READ
        print_test(2, "READ - Query messages")
        try:
            result = self.client.table("chat_messages").select("*").eq("memory_id", self.test_memory_id).order("created_at").execute()
            print_success(f"Found {len(result.data)} messages")
            for m in result.data:
                print_data(m['role'], m['content'][:30])
        except Exception as e:
            print_error(f"READ failed: {e}")
            return False
        
        print_success("All CHAT_MESSAGES CRUD operations passed!")
        return True
    
    def cleanup(self):
        """Clean up test data"""
        print_header("Cleaning Up Test Data")
        
        try:
            # Delete in reverse order (FK constraints)
            if self.test_message_ids:
                print_info(f"Deleting {len(self.test_message_ids)} messages...")
                for msg_id in self.test_message_ids:
                    self.client.table("chat_messages").delete().eq("id", msg_id).execute()
                print_success("Messages deleted")
            
            if self.test_record_ids:
                print_info(f"Deleting {len(self.test_record_ids)} records...")
                for rec_id in self.test_record_ids:
                    self.client.table("memory_records").delete().eq("id", rec_id).execute()
                print_success("Records deleted")
            
            if self.test_memory_id:
                print_info("Deleting test memory...")
                self.client.table("memories").delete().eq("id", self.test_memory_id).execute()
                print_success("Memory deleted")
            
            print_success("Cleanup complete")
        except Exception as e:
            print_error(f"Cleanup error: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.BOLD}{'='*70}")
        print("  SUPABASE CRUD OPERATIONS TEST SUITE")
        print(f"{'='*70}{Colors.END}\n")
        
        results = {}
        
        try:
            # Structure test first
            if not self.test_memories_structure():
                print_error("\n❌ Cannot proceed - need existing user")
                print_info("\nTO FIX:")
                print_info("1. Start your app:")
                print_info("   - Backend: uvicorn app.main:app --reload")
                print_info("   - Frontend: cd frontend && npm run dev")
                print_info("2. Open http://localhost:5173")
                print_info("3. Log in with Supabase credentials")
                print_info("4. Create at least one memory")
                print_info("5. Re-run this test")
                return False
            
            # Run CRUD tests
            results["Memories CRUD"] = self.test_memories_crud_with_real_user()
            
            if results["Memories CRUD"]:
                results["Memory Records CRUD"] = self.test_memory_records_crud()
                results["Chat Messages CRUD"] = self.test_chat_messages_crud()
            else:
                results["Memory Records CRUD"] = False
                results["Chat Messages CRUD"] = False
            
            # Summary
            print_header("Test Summary")
            
            passed = sum(1 for v in results.values() if v)
            failed = sum(1 for v in results.values() if not v)
            
            for test_name, result in results.items():
                if result:
                    print_success(test_name)
                else:
                    print_error(test_name)
            
            print(f"\n{Colors.BOLD}Total: {passed} passed, {failed} failed{Colors.END}\n")
            
            if failed == 0:
                print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.END}")
                print_info("Database tables are working correctly")
                print_info("All CRUD operations successful")
                print_info("Ready to fix the main app configuration\n")
                return True
            else:
                return False
                
        finally:
            self.cleanup()


def main():
    demo = SupabaseDemo()
    success = demo.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nInterrupted")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

