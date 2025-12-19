"""
TestUserCreation.py
Create test users with realistic sleep data for Nyx Sleep Tracker
"""

from datetime import datetime, timedelta
import random
import NyxDB as db
import sys
import time


def create_test_user(username, password, email=None):
    """Create a test user with email"""
    if not email:
        email = f"{username.lower()}@test.com"
    
    # Check if user already exists
    user = db.get_user_by_name(username)
    if user:
        print(f"⚠️  User '{username}' already exists. Updating password...")
        db.update_user_password(user['user_id'], password)
        return user['user_id']
    
    try:
        db.create_user(username, password, email)
        user = db.get_user_by_name(username)
        if user:
            print(f"✅ Created user: {username} (ID: {user['user_id']})")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            return user['user_id']
        else:
            print(f"❌ Failed to create user: {username}")
            return None
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None


def generate_sleep_sessions(user_id, days_back=60, sessions_per_day=1):
    """Generate realistic sleep sessions for a user"""
    print(f"\n📊 Generating sleep sessions for user ID: {user_id}")
    print(f"   Time range: Last {days_back} days")
    print(f"   Sessions per day: {sessions_per_day}")
    
    start_date = datetime.now() - timedelta(days=days_back)
    total_sessions = 0
    
    # Track weekends for different sleep patterns
    weekend_days = [5, 6]  # Saturday, Sunday (0=Monday, 6=Sunday)
    
    for day_offset in range(days_back):
        current_date = start_date + timedelta(days=day_offset)
        is_weekend = current_date.weekday() in weekend_days
        
        # Generate sessions for this day (usually 1, but sometimes none or multiple)
        if random.random() < 0.85:  # 85% chance of having sleep data for a day
            # Base sleep hours - longer on weekends
            if is_weekend:
                base_hours = random.uniform(7.5, 10.5)
            else:
                base_hours = random.uniform(6.0, 9.0)
            
            # Add some random variation
            hours = round(base_hours + random.uniform(-0.5, 0.5), 1)
            
            # Ensure reasonable values
            hours = max(4.0, min(12.0, hours))
            
            try:
                db.add_sleep_session(
                    user_id,
                    current_date.year,
                    current_date.month,
                    current_date.day,
                    hours
                )
                total_sessions += 1
                
                # Occasionally add a nap session (20% chance)
                if random.random() < 0.2:
                    nap_hours = round(random.uniform(0.5, 2.0), 1)
                    db.add_sleep_session(
                        user_id,
                        current_date.year,
                        current_date.month,
                        current_date.day,
                        nap_hours
                    )
                    total_sessions += 1
                    
            except Exception as e:
                print(f"⚠️  Error adding session for {current_date}: {e}")
    
    print(f"✅ Generated {total_sessions} sleep sessions")
    return total_sessions


def generate_user_statistics(user_id):
    """Generate and display user statistics"""
    print("\n📈 User Statistics:")
    
    sessions = db.get_all_sessions(user_id)
    
    if not sessions:
        print("   No sleep sessions found")
        return
    
    total_hours = sum(s['hours'] for s in sessions)
    avg_hours = total_hours / len(sessions)
    
    # Find best and worst sleep days
    sessions_by_hours = sorted(sessions, key=lambda x: x['hours'])
    worst_session = sessions_by_hours[0]
    best_session = sessions_by_hours[-1]
    
    print(f"   Total sessions: {len(sessions)}")
    print(f"   Total hours: {total_hours:.1f}")
    print(f"   Average per session: {avg_hours:.1f} hours")
    print(f"   Best sleep: {best_session['hours']:.1f} hours on {best_session['year']}-{best_session['month']:02d}-{best_session['day']:02d}")
    print(f"   Worst sleep: {worst_session['hours']:.1f} hours on {worst_session['year']}-{worst_session['month']:02d}-{worst_session['day']:02d}")
    
    # Calculate recent average (last 7 days)
    recent_sessions = [s for s in sessions if 
                      datetime(s['year'], s['month'], s['day']) > datetime.now() - timedelta(days=7)]
    if recent_sessions:
        recent_avg = sum(s['hours'] for s in recent_sessions) / len(recent_sessions)
        print(f"   Recent average (7 days): {recent_avg:.1f} hours")


def create_sample_users():
    """Create multiple sample users with different sleep patterns"""
    
    print("="*60)
    print("🛏️  NYX SLEEP TRACKER - TEST DATA GENERATOR")
    print("="*60)
    
    users = [
        # (username, password, description)
        ("TestUser", "password123", "Regular sleeper"),
        ("NightOwl", "password123", "Late night sleeper"),
        ("EarlyBird", "password123", "Early morning person"),
        ("WeekendWarrior", "password123", "Sleeps more on weekends"),
        ("LightSleeper", "password123", "Short sleep sessions"),
    ]
    
    created_users = []
    
    for username, password, description in users:
        print(f"\n👤 Creating: {username} ({description})")
        user_id = create_test_user(username, password)
        
        if user_id:
            # Different sleep patterns for different users
            if username == "NightOwl":
                sessions = generate_sleep_sessions(user_id, days_back=45, sessions_per_day=1)
            elif username == "EarlyBird":
                sessions = generate_sleep_sessions(user_id, days_back=30, sessions_per_day=1)
            elif username == "WeekendWarrior":
                sessions = generate_sleep_sessions(user_id, days_back=90, sessions_per_day=1)
            elif username == "LightSleeper":
                sessions = generate_sleep_sessions(user_id, days_back=20, sessions_per_day=2)
            else:
                sessions = generate_sleep_sessions(user_id, days_back=60, sessions_per_day=1)
            
            generate_user_statistics(user_id)
            created_users.append((username, user_id, sessions))
    
    return created_users


def delete_test_users():
    """Delete all test users (use with caution!)"""
    print("\n" + "="*60)
    print("⚠️  DELETE ALL TEST USERS")
    print("="*60)
    
    test_usernames = ["TestUser", "NightOwl", "EarlyBird", "WeekendWarrior", "LightSleeper"]
    
    confirm = input("Are you sure you want to delete all test users? (yes/NO): ").strip().lower()
    
    if confirm == "yes":
        for username in test_usernames:
            user = db.get_user_by_name(username)
            if user:
                print(f"🗑️  Deleting user: {username} (ID: {user['user_id']})")
                
                # Note: You'll need to implement delete_user function in NyxDB.py
                # For now, we'll just print a message
                print(f"   [Would delete user {username}]")
                # To actually delete, you would need:
                # db.delete_user(user['user_id'])
        print("✅ All test users marked for deletion")
    else:
        print("❌ Deletion cancelled")


def interactive_menu():
    """Interactive menu for test data creation"""
    while True:
        print("\n" + "="*60)
        print("🛏️  NYX SLEEP TRACKER - TEST DATA MENU")
        print("="*60)
        print("1. Create single test user")
        print("2. Create all sample users")
        print("3. Add more data to existing user")
        print("4. View user statistics")
        print("5. Delete test users (DANGER!)")
        print("6. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip() or "password123"
            email = input("Enter email (optional): ").strip()
            
            if username:
                user_id = create_test_user(username, password, email if email else None)
                if user_id:
                    days = input("How many days of data? (default: 60): ").strip()
                    days = int(days) if days.isdigit() else 60
                    
                    sessions = generate_sleep_sessions(user_id, days_back=days)
                    generate_user_statistics(user_id)
        
        elif choice == "2":
            created_users = create_sample_users()
            print(f"\n🎉 Created {len(created_users)} test users with sleep data")
        
        elif choice == "3":
            username = input("Enter username to add data to: ").strip()
            user = db.get_user_by_name(username)
            
            if user:
                days = input("How many more days of data? (default: 30): ").strip()
                days = int(days) if days.isdigit() else 30
                
                sessions = generate_sleep_sessions(user['user_id'], days_back=days)
                generate_user_statistics(user['user_id'])
            else:
                print(f"❌ User '{username}' not found")
        
        elif choice == "4":
            username = input("Enter username to view statistics: ").strip()
            user = db.get_user_by_name(username)
            
            if user:
                generate_user_statistics(user['user_id'])
            else:
                print(f"❌ User '{username}' not found")
        
        elif choice == "5":
            delete_test_users()
        
        elif choice == "6":
            print("\n👋 Exiting test data generator. Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 6.")


def quick_create():
    """Quick create mode - for command line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("\n🛏️  NYX SLEEP TRACKER - TEST DATA GENERATOR")
        print("="*60)
        print("Usage:")
        print("  python TestUserCreation.py --create <username>")
        print("  python TestUserCreation.py --sample (creates all sample users)")
        print("  python TestUserCreation.py --add <username>")
        print("  python TestUserCreation.py --interactive")
        print("="*60)
        return False
    
    mode = sys.argv[1]
    
    if mode == "--interactive" or mode == "-i":
        return True
    
    if mode == "--sample":
        create_sample_users()
        return False
    
    if len(sys.argv) < 3:
        print("\n❌ Missing username.")
        return False
    
    username = sys.argv[2]
    
    if mode == "--create":
        user_id = create_test_user(username, "password123")
        if user_id:
            generate_sleep_sessions(user_id, days_back=60)
            generate_user_statistics(user_id)
    
    elif mode == "--add":
        user = db.get_user_by_name(username)
        if user:
            generate_sleep_sessions(user['user_id'], days_back=30)
            generate_user_statistics(user['user_id'])
        else:
            print(f"❌ User '{username}' not found")
    
    else:
        print(f"❌ Unknown mode: {mode}")
        return False


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("🛏️  NYX SLEEP TRACKER - TEST DATA GENERATOR")
    print("="*60)
    
    # Check database connection first
    try:
        connection = db.get_connection()
        print("✅ Database connection successful")
        connection.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure MySQL is running and nyx_sleep database exists")
        sys.exit(1)
    
    # Check if running in quick mode or interactive mode
    if len(sys.argv) > 1:
        should_continue = quick_create()
        if not should_continue:
            sys.exit(0)
    
    # Run interactive menu
    interactive_menu()
