"""
Script to safely add the destination column to the TripPackage table
and populate it with destination data
"""
import sqlite3
import os
import random
from app import app

# Bangladesh popular destinations
destinations = [
    "Cox's Bazar",
    "Sylhet",
    "Rangamati",
    "Bandarban",
    "Saint Martin's Island", 
    "Dhaka",
    "Chittagong",
    "Khulna",
    "Kuakata",
    "Sundarban"
]

def add_destination_column():
    # Get the database path from app config
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the destination column already exists
        cursor.execute("PRAGMA table_info(trip_package)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'destination' not in column_names:
            # Add the destination column
            cursor.execute("ALTER TABLE trip_package ADD COLUMN destination TEXT")
            print("Added 'destination' column to the trip_package table")
            
            # Get all package IDs
            cursor.execute("SELECT id FROM trip_package")
            package_ids = [row[0] for row in cursor.fetchall()]
            
            # Update each package with a random destination
            for package_id in package_ids:
                destination = random.choice(destinations)
                cursor.execute(
                    "UPDATE trip_package SET destination = ? WHERE id = ?", 
                    (destination, package_id)
                )
                print(f"Updated package {package_id} with destination '{destination}'")
            
            # Commit the changes
            conn.commit()
            print("All packages updated with destinations!")
        else:
            print("The 'destination' column already exists in the trip_package table")
    
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        conn.rollback()
    
    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    add_destination_column()
