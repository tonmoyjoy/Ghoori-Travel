"""
Script to update existing trip packages with destination information
"""
from app import app, db
from models.models import TripPackage

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

def update_package_destinations():
    with app.app_context():
        # Get all trip packages
        packages = TripPackage.query.all()
        
        if not packages:
            print("No packages found in the database.")
            return
        
        print(f"Found {len(packages)} packages to update")
        
        # Assign destinations to packages (in a real scenario, this would be more thoughtfully mapped)
        for i, package in enumerate(packages):
            # Assign destinations in a round-robin fashion
            destination = destinations[i % len(destinations)]
            
            # Update the package destination
            package.destination = destination
            print(f"Updating package '{package.name}' with destination '{destination}'")
        
        # Commit the changes
        db.session.commit()
        print("All package destinations updated successfully!")

if __name__ == "__main__":
    update_package_destinations()
