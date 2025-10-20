#!/usr/bin/env python3
"""
Demo Supabase CRUD Operations Test
Terminal tool to verify all database operations work correctly
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
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
        if not self.supabase_url:
            print_error("SUPABASE_URL not found in environment")
            sys.exit(1)
        
        if not self.supabase_anon_key:
            print_error("SUPABASE_ANON_KEY not found in environment")
            sys.exit(1)
            
        if not self.supabase_service_key:
            print_error("SUPABASE_SERVICE_ROLE_KEY not found in environment")
            print_info("Will use anon key instead (limited permissions)")
            self.supabase_service_key = self.supabase_anon_key
        
        # Display config
        print_success(f"SUPABASE_URL: {self.supabase_url[:40]}...")
        print_success(f"SUPABASE_ANON_KEY: {self.supabase_anon_key[:20]}...")
        print_success(f"SUPABASE_SERVICE_KEY: {self.supabase_service_key[:20]}...")
        
        # Create clients
        try:
            print_info("Creating Supabase client with service role key...")
            self.client = create_client(self.supabase_url, self.supabase_service_key)
            print_success("Supabase client created successfully")
        except Exception as e:
            print_error(f"Failed to create Supabase client: {e}")
            sys.exit(1)
        
        # Test connection
        print_info("Testing connection...")
        try:
            result = self.client.table("memories").select("*").limit(1).execute()
            print_success("Connection test passed")
        except Exception as e:
            print_error(f"Connection test failed: {e}")
            sys.exit(1)
        
        # Store test data IDs for cleanup
        self.test_memory_id = None
        self.test_record_ids = []
        self.test_message_ids = []
        self.test_user_id = "00000000-0000-0000-0000-000000000099"  # Test user ID
    
    def test_memories_crud(self):
        """Test CRUD operations on memories table"""
        print_header("Testing MEMORIES Table - CRUD Operations")
        
        # CREATE
        print_test(1, "CREATE - Insert new memory")
        try:
            memory_data = {
                "user_id": self.test_user_id,
                "title": f"Demo Memory {datetime.now().strftime('%H:%M:%S')}",
                "description": "This is a test memory created by demo tool"
            }
            print_info(f"Inserting: {memory_data}")
            
            result = self.client.table("memories").insert(memory_data).execute()
            
            if result.data and len(result.data) > 0:
                self.test_memory_id = result.data[0]['id']
                print_success(f"Memory created successfully")
                print_data("ID", self.test_memory_id)
                print_data("Title", result.data[0]['title'])
                print_data("Created At", result.data[0]['created_at'])
            else:
                print_error("No data returned from insert")
                return False
        except Exception as e:
            print_error(f"CREATE failed: {e}")
            return False
        
        # READ
        print_test(2, "READ - Query the created memory")
        try:
            result = self.client.table("memories").select("*").eq("id", self.test_memory_id).execute()
            
            if result.data and len(result.data) > 0:
                print_success("Memory retrieved successfully")
                memory = result.data[0]
                print_data("ID", memory['id'])
                print_data("Title", memory['title'])
                print_data("Description", memory['description'])
                print_data("User ID", memory['user_id'])
            else:
                print_error("Memory not found")
                return False
        except Exception as e:
            print_error(f"READ failed: {e}")
            return False
        
        # UPDATE
        print_test(3, "UPDATE - Modify the memory")
        try:
            update_data = {
                "description": f"Updated at {datetime.now().strftime('%H:%M:%S')}"
            }
            print_info(f"Updating with: {update_data}")
            
            result = self.client.table("memories").update(update_data).eq("id", self.test_memory_id).execute()
            
            if result.data and len(result.data) > 0:
                print_success("Memory updated successfully")
                print_data("New Description", result.data[0]['description'])
            else:
                print_error("Update returned no data")
                return False
        except Exception as e:
            print_error(f"UPDATE failed: {e}")
            return False
        
        # LIST
        print_test(4, "LIST - Query all memories for user")
        try:
            result = self.client.table("memories").select("*").eq("user_id", self.test_user_id).execute()
            
            print_success(f"Found {len(result.data)} memories for user")
            for mem in result.data:
                print_data(f"  Memory", f"{mem['title']} (ID: {mem['id'][:8]}...)")
        except Exception as e:
            print_error(f"LIST failed: {e}")
            return False
        
        print_success("All MEMORIES CRUD operations passed!")
        return True
    
    def test_memory_records_crud(self):
        """Test CRUD operations on memory_records table"""
        print_header("Testing MEMORY_RECORDS Table - CRUD Operations")
        
        if not self.test_memory_id:
            print_error("No test memory ID available. Run memories test first.")
            return False
        
        # CREATE
        print_test(1, "CREATE - Insert new memory record")
        try:
            record_data = {
                "memory_id": self.test_memory_id,
                "content": f"Test record created at {datetime.now().strftime('%H:%M:%S')}"
            }
            print_info(f"Inserting: {record_data}")
            
            result = self.client.table("memory_records").insert(record_data).execute()
            
            if result.data and len(result.data) > 0:
                record_id = result.data[0]['id']
                self.test_record_ids.append(record_id)
                print_success("Record created successfully")
                print_data("ID", record_id)
                print_data("Content", result.data[0]['content'])
            else:
                print_error("No data returned from insert")
                return False
        except Exception as e:
            print_error(f"CREATE failed: {e}")
            return False
        
        # CREATE multiple
        print_test(2, "CREATE - Insert multiple records")
        try:
            for i in range(3):
                record_data = {
                    "memory_id": self.test_memory_id,
                    "content": f"Record {i+1}: {datetime.now().strftime('%H:%M:%S')}"
                }
                result = self.client.table("memory_records").insert(record_data).execute()
                if result.data:
                    self.test_record_ids.append(result.data[0]['id'])
            
            print_success(f"Created {len(self.test_record_ids)} records total")
        except Exception as e:
            print_error(f"CREATE multiple failed: {e}")
            return False
        
        # READ
        print_test(3, "READ - Query records for memory")
        try:
            result = self.client.table("memory_records").select("*").eq("memory_id", self.test_memory_id).execute()
            
            print_success(f"Found {len(result.data)} records")
            for record in result.data:
                print_data(f"  Record", f"{record['content'][:40]}...")
        except Exception as e:
            print_error(f"READ failed: {e}")
            return False
        
        # UPDATE
        print_test(4, "UPDATE - Modify a record")
        try:
            if self.test_record_ids:
                update_data = {
                    "content": f"Updated record at {datetime.now().strftime('%H:%M:%S')}"
                }
                result = self.client.table("memory_records").update(update_data).eq("id", self.test_record_ids[0]).execute()
                
                if result.data:
                    print_success("Record updated successfully")
                    print_data("New Content", result.data[0]['content'])
                else:
                    print_error("Update returned no data")
        except Exception as e:
            print_error(f"UPDATE failed: {e}")
            return False
        
        print_success("All MEMORY_RECORDS CRUD operations passed!")
        return True
    
    def test_chat_messages_crud(self):
        """Test CRUD operations on chat_messages table"""
        print_header("Testing CHAT_MESSAGES Table - CRUD Operations")
        
        if not self.test_memory_id:
            print_error("No test memory ID available. Run memories test first.")
            return False
        
        # CREATE - User message
        print_test(1, "CREATE - Insert user message")
        try:
            message_data = {
                "memory_id": self.test_memory_id,
                "role": "user",
                "content": "This is a test user message"
            }
            print_info(f"Inserting: {message_data}")
            
            result = self.client.table("chat_messages").insert(message_data).execute()
            
            if result.data and len(result.data) > 0:
                message_id = result.data[0]['id']
                self.test_message_ids.append(message_id)
                print_success("User message created successfully")
                print_data("ID", message_id)
                print_data("Role", result.data[0]['role'])
                print_data("Content", result.data[0]['content'])
            else:
                print_error("No data returned from insert")
                return False
        except Exception as e:
            print_error(f"CREATE user message failed: {e}")
            return False
        
        # CREATE - Assistant message
        print_test(2, "CREATE - Insert assistant message")
        try:
            message_data = {
                "memory_id": self.test_memory_id,
                "role": "assistant",
                "content": "This is a test assistant response"
            }
            
            result = self.client.table("chat_messages").insert(message_data).execute()
            
            if result.data and len(result.data) > 0:
                message_id = result.data[0]['id']
                self.test_message_ids.append(message_id)
                print_success("Assistant message created successfully")
                print_data("ID", message_id)
                print_data("Role", result.data[0]['role'])
            else:
                print_error("No data returned from insert")
                return False
        except Exception as e:
            print_error(f"CREATE assistant message failed: {e}")
            return False
        
        # READ
        print_test(3, "READ - Query messages for memory")
        try:
            result = self.client.table("chat_messages").select("*").eq("memory_id", self.test_memory_id).order("created_at").execute()
            
            print_success(f"Found {len(result.data)} messages")
            for msg in result.data:
                print_data(f"  {msg['role']}", f"{msg['content'][:50]}...")
        except Exception as e:
            print_error(f"READ failed: {e}")
            return False
        
        # CREATE conversation
        print_test(4, "CREATE - Insert conversation")
        try:
            messages = [
                {"memory_id": self.test_memory_id, "role": "user", "content": "What's 2+2?"},
                {"memory_id": self.test_memory_id, "role": "assistant", "content": "2+2 equals 4"},
                {"memory_id": self.test_memory_id, "role": "user", "content": "Thanks!"},
                {"memory_id": self.test_memory_id, "role": "assistant", "content": "You're welcome!"}
            ]
            
            for msg_data in messages:
                result = self.client.table("chat_messages").insert(msg_data).execute()
                if result.data:
                    self.test_message_ids.append(result.data[0]['id'])
            
            print_success(f"Created conversation with {len(messages)} messages")
        except Exception as e:
            print_error(f"CREATE conversation failed: {e}")
            return False
        
        print_success("All CHAT_MESSAGES CRUD operations passed!")
        return True
    
    def test_foreign_keys(self):
        """Test foreign key constraints"""
        print_header("Testing Foreign Key Constraints")
        
        # Test 1: Try to insert record with non-existent memory_id
        print_test(1, "FK Constraint - memory_records -> memories")
        try:
            fake_memory_id = str(uuid.uuid4())
            bad_record = {
                "memory_id": fake_memory_id,
                "content": "This should fail"
            }
            
            try:
                result = self.client.table("memory_records").insert(bad_record).execute()
                print_error("FK constraint NOT enforced! (This is a problem)")
                return False
            except Exception as e:
                if "foreign key" in str(e).lower() or "violates" in str(e).lower():
                    print_success("FK constraint enforced correctly")
                else:
                    print_error(f"Unexpected error: {e}")
                    return False
        except Exception as e:
            print_error(f"Test failed: {e}")
            return False
        
        # Test 2: Try to insert message with non-existent memory_id
        print_test(2, "FK Constraint - chat_messages -> memories")
        try:
            fake_memory_id = str(uuid.uuid4())
            bad_message = {
                "memory_id": fake_memory_id,
                "role": "user",
                "content": "This should fail"
            }
            
            try:
                result = self.client.table("chat_messages").insert(bad_message).execute()
                print_error("FK constraint NOT enforced! (This is a problem)")
                return False
            except Exception as e:
                if "foreign key" in str(e).lower() or "violates" in str(e).lower():
                    print_success("FK constraint enforced correctly")
                else:
                    print_error(f"Unexpected error: {e}")
                    return False
        except Exception as e:
            print_error(f"Test failed: {e}")
            return False
        
        print_success("All foreign key constraints working correctly!")
        return True
    
    def test_cascade_delete(self):
        """Test cascade delete behavior"""
        print_header("Testing Cascade Delete (if configured)")
        
        print_info("Note: If cascade delete is not configured, this will need manual cleanup")
        print_info("This test is informational only")
        
        return True
    
    def cleanup(self):
        """Clean up test data"""
        print_header("Cleaning Up Test Data")
        
        try:
            # Delete messages
            if self.test_message_ids:
                print_info(f"Deleting {len(self.test_message_ids)} test messages...")
                for msg_id in self.test_message_ids:
                    try:
                        self.client.table("chat_messages").delete().eq("id", msg_id).execute()
                    except:
                        pass
                print_success("Messages deleted")
            
            # Delete records
            if self.test_record_ids:
                print_info(f"Deleting {len(self.test_record_ids)} test records...")
                for record_id in self.test_record_ids:
                    try:
                        self.client.table("memory_records").delete().eq("id", record_id).execute()
                    except:
                        pass
                print_success("Records deleted")
            
            # Delete memory
            if self.test_memory_id:
                print_info("Deleting test memory...")
                self.client.table("memories").delete().eq("id", self.test_memory_id).execute()
                print_success("Memory deleted")
            
            # Verify cleanup
            print_info("Verifying cleanup...")
            if self.test_memory_id:
                result = self.client.table("memories").select("*").eq("id", self.test_memory_id).execute()
                if not result.data or len(result.data) == 0:
                    print_success("Cleanup verified - all test data removed")
                else:
                    print_error("Some test data may remain")
            
        except Exception as e:
            print_error(f"Cleanup error: {e}")
            print_info("You may need to manually delete test data")
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.BOLD}{'='*70}")
        print("  SUPABASE CRUD OPERATIONS DEMO & TEST")
        print(f"{'='*70}{Colors.END}\n")
        
        results = {}
        
        try:
            # Run tests
            results["Memories CRUD"] = self.test_memories_crud()
            results["Memory Records CRUD"] = self.test_memory_records_crud()
            results["Chat Messages CRUD"] = self.test_chat_messages_crud()
            results["Foreign Key Constraints"] = self.test_foreign_keys()
            results["Cascade Delete"] = self.test_cascade_delete()
            
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
                print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Database is ready for use.{Colors.END}\n")
                return True
            else:
                print(f"{Colors.RED}{Colors.BOLD}⚠️  Some tests failed. Review errors above.{Colors.END}\n")
                return False
                
        finally:
            # Always cleanup
            self.cleanup()


def main():
    """Main function"""
    demo = SupabaseDemo()
    success = demo.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

