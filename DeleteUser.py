"""
DeleteUser.py - Console-based user deletion tool for Nyx Sleep Tracker
Allows deletion of user accounts by user_id, username, or email
"""

import NyxDB as db
import mysql.connector


def display_all_users():
    """Display all users in the database"""
    try:
        connection = db.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, username, email, created_at FROM users ORDER BY user_id")
        users = cursor.fetchall()
        connection.close()
        
        if not users:
            print("\n❌ No users found in database.")
            return []
        
        print("\n" + "="*80)
        print("📋 ALL USERS IN DATABASE")
        print("="*80)
        print(f"{'ID':<6} {'Username':<20} {'Email':<30} {'Created':<20}")
        print("-"*80)
        
        for user in users:
            print(f"{user['user_id']:<6} {user['username']:<20} {user['email']:<30} {str(user['created_at']):<20}")
        
        print("="*80)
        return users
    
    except Exception as e:
        print(f"\n❌ Error fetching users: {e}")
        return []


def get_user_details(user_id):
    """Get detailed information about a user"""
    try:
        connection = db.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user info
        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            connection.close()
            return None
        
        # Get sleep sessions count
        cursor.execute("SELECT COUNT(*) as session_count, SUM(hours) as total_hours FROM sleep_sessions WHERE user_id=%s", (user_id,))
        stats = cursor.fetchone()
        
        # Get settings
        cursor.execute("SELECT * FROM user_settings WHERE user_id=%s", (user_id,))
        settings = cursor.fetchone()
        
        connection.close()
        
        return {
            'user': user,
            'stats': stats,
            'settings': settings
        }
    
    except Exception as e:
        print(f"\n❌ Error getting user details: {e}")
        return None


def delete_user_by_id(user_id):
    """Delete a user and all associated data by user_id"""
    try:
        connection = db.get_connection()
        cursor = connection.cursor()
        
        # Check if user exists
        cursor.execute("SELECT username FROM users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            connection.close()
            print(f"\n❌ User with ID {user_id} not found.")
            return False
        
        username = user[0]
        
        # Get counts before deletion
        cursor.execute("SELECT COUNT(*) FROM sleep_sessions WHERE user_id=%s", (user_id,))
        session_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_settings WHERE user_id=%s", (user_id,))
        settings_count = cursor.fetchone()[0]
        
        # Delete user (CASCADE will delete related records)
        cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        connection.commit()
        connection.close()
        
        print(f"\n✅ Successfully deleted user: {username} (ID: {user_id})")
        print(f"   📊 Deleted {session_count} sleep sessions")
        print(f"   ⚙️  Deleted {settings_count} user settings")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error deleting user: {e}")
        return False


def delete_user_by_username(username):
    """Delete a user by username"""
    user = db.get_user_by_name(username)
    if user:
        return delete_user_by_id(user['user_id'])
    else:
        print(f"\n❌ User '{username}' not found.")
        return False


def delete_user_by_email(email):
    """Delete a user by email"""
    user = db.get_user_by_email(email)
    if user:
        return delete_user_by_id(user['user_id'])
    else:
        print(f"\n❌ User with email '{email}' not found.")
        return False


def confirm_deletion(user_id):
    """Ask for confirmation before deleting"""
    details = get_user_details(user_id)
    
    if not details:
        print(f"\n❌ User with ID {user_id} not found.")
        return False
    
    user = details['user']
    stats = details['stats']
    
    print("\n" + "="*80)
    print("⚠️  USER DELETION CONFIRMATION")
    print("="*80)
    print(f"User ID:       {user['user_id']}")
    print(f"Username:      {user['username']}")
    print(f"Email:         {user['email']}")
    print(f"Created:       {user['created_at']}")
    print(f"Sleep Sessions: {stats['session_count'] or 0}")
    print(f"Total Hours:   {stats['total_hours'] or 0:.1f} hours")
    print("="*80)
    print("⚠️  WARNING: This action CANNOT be undone!")
    print("   All user data, sleep sessions, and settings will be permanently deleted.")
    print("="*80)
    
    confirmation = input("\nType 'DELETE' to confirm deletion: ").strip()
    
    if confirmation == "DELETE":
        return delete_user_by_id(user_id)
    else:
        print("\n❌ Deletion cancelled.")
        return False


def interactive_menu():
    """Interactive menu for user deletion"""
    while True:
        print("\n" + "="*80)
        print("🗑️  NYX SLEEP TRACKER - USER DELETION TOOL")
        print("="*80)
        print("1. View all users")
        print("2. Delete user by ID")
        print("3. Delete user by username")
        print("4. Delete user by email")
        print("5. Delete multiple users by ID")
        print("6. Exit")
        print("="*80)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            display_all_users()
        
        elif choice == "2":
            display_all_users()
            try:
                user_id = int(input("\nEnter user ID to delete: ").strip())
                confirm_deletion(user_id)
            except ValueError:
                print("\n❌ Invalid user ID. Please enter a number.")
        
        elif choice == "3":
            display_all_users()
            username = input("\nEnter username to delete: ").strip()
            if username:
                user = db.get_user_by_name(username)
                if user:
                    confirm_deletion(user['user_id'])
                else:
                    print(f"\n❌ User '{username}' not found.")
        
        elif choice == "4":
            display_all_users()
            email = input("\nEnter email to delete: ").strip()
            if email:
                user = db.get_user_by_email(email)
                if user:
                    confirm_deletion(user['user_id'])
                else:
                    print(f"\n❌ User with email '{email}' not found.")
        
        elif choice == "5":
            display_all_users()
            ids_input = input("\nEnter user IDs to delete (comma-separated, e.g., 1,3,5): ").strip()
            try:
                user_ids = [int(id.strip()) for id in ids_input.split(',')]
                print(f"\n📋 You are about to delete {len(user_ids)} users")
                
                for user_id in user_ids:
                    print(f"\n--- Processing User ID: {user_id} ---")
                    confirm_deletion(user_id)
                
            except ValueError:
                print("\n❌ Invalid input. Please enter numbers separated by commas.")
        
        elif choice == "6":
            print("\n👋 Exiting user deletion tool. Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 6.")


def quick_delete():
    """Quick delete mode - for command line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("\n🗑️  NYX USER DELETION TOOL - Quick Mode")
        print("="*60)
        print("Usage:")
        print("  python DeleteUser.py --id <user_id>")
        print("  python DeleteUser.py --username <username>")
        print("  python DeleteUser.py --email <email>")
        print("  python DeleteUser.py --interactive")
        print("="*60)
        return False
    
    mode = sys.argv[1]
    
    if mode == "--interactive" or mode == "-i":
        return True
    
    if len(sys.argv) < 3:
        print("\n❌ Missing value. Please provide a user_id, username, or email.")
        return False
    
    value = sys.argv[2]
    
    if mode == "--id":
        try:
            user_id = int(value)
            return confirm_deletion(user_id)
        except ValueError:
            print("\n❌ Invalid user ID. Please enter a number.")
            return False
    
    elif mode == "--username":
        user = db.get_user_by_name(value)
        if user:
            return confirm_deletion(user['user_id'])
        else:
            print(f"\n❌ User '{value}' not found.")
            return False
    
    elif mode == "--email":
        user = db.get_user_by_email(value)
        if user:
            return confirm_deletion(user['user_id'])
        else:
            print(f"\n❌ User with email '{value}' not found.")
            return False
    
    else:
        print(f"\n❌ Unknown mode: {mode}")
        return False


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("🗑️  NYX SLEEP TRACKER - USER DELETION TOOL")
    print("="*80)
    
    # Check if running in quick mode or interactive mode
    if len(sys.argv) > 1:
        should_continue = quick_delete()
        if not should_continue:
            sys.exit(0)
    
    # Run interactive menu
    interactive_menu()