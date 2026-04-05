"""
Script to fix packages with None destination
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

def fix_null_destinations():
    with app.app_context():
        # Find packages with None destination
        null_dest_packages = TripPackage.query.filter(TripPackage.destination.is_(None)).all()
        print(f"Found {len(null_dest_packages)} packages with None destination")
        
        # Update each package with a random destination
        for package in null_dest_packages:
            destination = random.choice(destinations)
            package.destination = destination
            print(f"Updated package {package.name} with destination: {destination}")
        
        # Commit the changes
        db.session.commit()
        print("All null destinations updated successfully!")

if __name__ == "__main__":
    fix_null_destinations()
