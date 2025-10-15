#!/usr/bin/env python3
"""
TripLens Server Startup Script
This script starts the Flask API server for the TripLens application.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_cors
        import pandas
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def setup_database():
    """Setup database if it doesn't exist"""
    db_path = Path("database/triplens.db")
    if not db_path.exists():
        print("Setting up database...")
        try:
            # Run the database setup script
            subprocess.run([sys.executable, "database/database.py"], check=True)
            print("✓ Database setup completed")
        except subprocess.CalledProcessError:
            print("✗ Database setup failed")
            return False
    else:
        print("✓ Database already exists")
    return True

def start_server():
    """Start the Flask server"""
    print("Starting TripLens API server...")
    print("Server will be available at: http://localhost:5000")
    print("Frontend should be served from: http://localhost:3000 or file://")
    print("\nPress Ctrl+C to stop the server")
    
    # Change to the api directory
    os.chdir("api")
    
    # Start the Flask server
    try:
        subprocess.run([sys.executable, "server.py"])
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error starting server: {e}")

def main():
    """Main function"""
    print("TripLens Server Startup")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not Path("api").exists():
        print("✗ Please run this script from the TripLens root directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
