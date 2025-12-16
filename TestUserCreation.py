from datetime import datetime, timedelta
import random
import NyxDB as db

# ---------- Step 1: Create test user ----------
username = "TestUser"
password = "password123"

# Check if user already exists
user = db.get_user_by_name(username)
if not user:
    db.create_user(username, password)
    user = db.get_user_by_name(username)

user_id = user['user_id']  # assuming your table's PK column is 'id'

# ---------- Step 2: Generate sleep sessions for 2 months ----------
# We'll generate random sleep hours between 5.0 and 9.0
start_date = datetime.now() - timedelta(days=60)  # 2 months ago
sessions_to_create = 60  # roughly 2 months

for i in range(sessions_to_create):
    date = start_date + timedelta(days=i)
    hours = round(random.uniform(5, 9), 1)  # random sleep between 5-9 hours
    db.add_sleep_session(user_id, date.year, date.month, date.day, hours)

print(f"Test user '{username}' created with {sessions_to_create} sleep sessions.")