"""
Nyx Sleep Tracker - Database Setup Script
Run this to create all necessary tables
"""

import mysql.connector
from mysql.connector import Error

def create_database():
    """Create the database and all tables"""
    
    connection = None
    try:
        # Connect to MySQL (without specifying database)
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        
        cursor = connection.cursor()
        
        print("📦 Setting up Nyx Sleep Tracker database...")
        
        # 1. Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS nyx_sleep CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        cursor.execute("USE nyx_sleep")
        print("✅ Database 'nyx_sleep' created/verified")
        
        # 2. Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_email (email)
            )
        """)
        print("✅ 'users' table created")
        
        # 3. Create sleep_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sleep_sessions (
                session_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                year INT NOT NULL,
                month INT NOT NULL,
                day INT NOT NULL,
                hours DECIMAL(5,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                INDEX idx_user_date (user_id, year, month, day)
            )
        """)
        print("✅ 'sleep_sessions' table created")
        
        # 4. Create user_settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                setting_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL UNIQUE,
                bedtime_enabled TINYINT(1) DEFAULT 0,
                bedtime_hour VARCHAR(2) DEFAULT '10',
                bedtime_minute VARCHAR(2) DEFAULT '00',
                bedtime_ampm VARCHAR(2) DEFAULT 'PM',
                alarm_enabled TINYINT(1) DEFAULT 0,
                alarm_hour VARCHAR(2) DEFAULT '06',
                alarm_minute VARCHAR(2) DEFAULT '30',
                alarm_ampm VARCHAR(2) DEFAULT 'AM',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        print("✅ 'user_settings' table created")
        
        # 5. Create password_resets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                reset_id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) NOT NULL,
                code VARCHAR(6) NOT NULL,
                expires_at DATETIME NOT NULL,
                used TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_email_code (email, code)
            )
        """)
        print("✅ 'password_resets' table created")
        
        # 6. Create test user (optional)
        try:
            cursor.execute("""
                INSERT INTO users (username, password, email) 
                VALUES ('testuser', 'password123', 'test@example.com')
                ON DUPLICATE KEY UPDATE username=username
            """)
            print("✅ Test user created: testuser / password123")
        except:
            print("ℹ️  Test user already exists")
        
        connection.commit()
        print("\n" + "="*50)
        print("✨ DATABASE SETUP COMPLETE!")
        print("="*50)
        print("\nYou can now run the Nyx Sleep Tracker app.")
        print("\nTest credentials:")
        print("  Username: testuser")
        print("  Password: password123")
        print("  Email: test@example.com")
        
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Database connection closed")

if __name__ == "__main__":
    create_database()