#!/usr/bin/env python3
"""
Database setup script for the school activities system.
This script creates the MySQL database and tables.
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the school_activities database if it doesn't exist."""
    try:
        # Connect to MySQL server (without specifying a database)
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "")
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS school_activities")
            print("Database 'school_activities' created successfully")

            cursor.close()
            connection.close()
            print("MySQL connection closed")

    except Error as e:
        print(f"Error creating database: {e}")
        return False

    return True

def setup_database():
    """Set up the database and create tables using SQLAlchemy."""
    try:
        # Import here to avoid import errors if database isn't set up
        from database import create_tables, engine
        from sqlalchemy import text

        # Create all tables
        create_tables()
        print("Database tables created successfully")

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connection test successful")

        return True

    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

if __name__ == "__main__":
    print("Setting up school activities database...")

    # Step 1: Create database
    if create_database():
        print("✓ Database creation completed")

        # Step 2: Create tables
        if setup_database():
            print("✓ Database setup completed successfully!")
            print("\nYou can now run the application with: python src/app.py")
        else:
            print("✗ Database setup failed")
    else:
        print("✗ Database creation failed")