import os
import sys
import subprocess
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import urllib.parse

def create_database():
    """Create the PostgreSQL database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server - connect to the default 'postgres' database first
        conn = psycopg2.connect(
            user="nagajyothiprakash",
            password="Login@123",
            host="localhost",
            port="5432",
            database="postgres"  # Connect to the default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'waffy_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'waffy_db'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("waffy_db")))
            print("Database created successfully!")
        else:
            print("Database 'waffy_db' already exists.")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    # URL encode the password to handle special characters
    password = urllib.parse.quote_plus("Login@123")
    
    if not os.path.exists(env_path):
        print("Creating .env file...")
        with open(env_path, 'w') as f:
            f.write(f"DATABASE_URL=postgresql://nagajyothiprakash:{password}@localhost/waffy_db\n")
            f.write("PORT=8000\n")
            f.write("HOST=0.0.0.0\n")
        print(".env file created successfully!")
    else:
        print(".env file already exists.")
        # Update the existing .env file
        print("Updating .env file with correct database URL...")
        with open(env_path, 'w') as f:
            f.write(f"DATABASE_URL=postgresql://nagajyothiprakash:{password}@localhost/waffy_db\n")
            f.write("PORT=8000\n")
            f.write("HOST=0.0.0.0\n")
        print(".env file updated successfully!")

def main():
    print("Setting up WAffy backend...")
    
    # Create .env file
    create_env_file()
    
    # Create database
    if create_database():
        print("\nSetup completed successfully!")
        print("\nYou can now start the backend server with:")
        print("python main.py")
    else:
        print("\nSetup failed. Please check your PostgreSQL installation and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
