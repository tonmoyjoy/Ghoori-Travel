"""
Script to check and update destinations in the trip_package table
"""
from app import app, db
from models.models import TripPackage
import random

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

def check_and_update_destinations():
    with app.app_context():
        # Get all trip packages
        packages = TripPackage.query.all()
        
        if not packages:
            print("No packages found in the database.")
            return
        
        print(f"Found {len(packages)} packages in the database")
        
        # Check and update destinations
        updates_needed = 0
        for package in packages:
            print(f"Package '{package.name}': destination = '{package.destination}'")
            
            # If destination is None or empty, assign a random destination
            if not package.destination:
                package.destination = random.choice(destinations)
                updates_needed += 1
                print(f"  -> Updated to '{package.destination}'")
        
        # Commit if there were updates
        if updates_needed > 0:
            db.session.commit()
            print(f"Updated {updates_needed} packages with missing destinations")
        else:
            print("All packages already have destinations assigned")

if __name__ == "__main__":
    check_and_update_destinations()
