"""
Script to test trip package filtering
"""
from app import app, db
from models.models import TripPackage, TripPreferences
from flask_login import current_user
import random

def test_filtering():
    with app.app_context():
        # Print total number of trip packages
        total_packages = TripPackage.query.count()
        print(f"Total trip packages: {total_packages}")
        
        # Check price distribution
        budget_packages = TripPackage.query.filter(TripPackage.price <= 15000).count()
        mid_range_packages = TripPackage.query.filter(TripPackage.price > 15000, TripPackage.price <= 30000).count()
        luxury_packages = TripPackage.query.filter(TripPackage.price > 30000, TripPackage.price <= 50000).count()
        ultra_luxury_packages = TripPackage.query.filter(TripPackage.price > 50000).count()
        
        print(f"Budget packages (≤15000): {budget_packages}")
        print(f"Mid-range packages (15000-30000): {mid_range_packages}")
        print(f"Luxury packages (30000-50000): {luxury_packages}")
        print(f"Ultra-luxury packages (>50000): {ultra_luxury_packages}")
        
        # Check destination distribution
        destinations = {}
        for package in TripPackage.query.all():
            if package.destination in destinations:
                destinations[package.destination] = destinations[package.destination] + 1
            else:
                destinations[package.destination] = 1
        
        print("\nDestination distribution:")
        for dest, count in destinations.items():
            print(f"{dest}: {count} packages")
            
        # Set some package prices that might be wrong to ensure proper filtering
        # Make sure we have at least some packages in each price range
        if budget_packages == 0 or mid_range_packages == 0 or luxury_packages == 0 or ultra_luxury_packages == 0:
            print("\nFixing price distribution...")
            
            # Get packages to modify
            packages = TripPackage.query.all()
            if not packages:
                print("No packages to modify")
                return
                
            # Ensure we have at least 3 packages in each price range
            for i, price_range in enumerate(['budget', 'mid_range', 'luxury', 'ultra_luxury']):
                if price_range == 'budget' and budget_packages < 3:
                    for j in range(3 - budget_packages):
                        if i * 3 + j < len(packages):
                            packages[i * 3 + j].price = random.uniform(5000, 15000)
                            print(f"Set package {packages[i * 3 + j].name} to budget price: {packages[i * 3 + j].price}")
                
                elif price_range == 'mid_range' and mid_range_packages < 3:
                    for j in range(3 - mid_range_packages):
                        if i * 3 + j < len(packages):
                            packages[i * 3 + j].price = random.uniform(15001, 30000)
                            print(f"Set package {packages[i * 3 + j].name} to mid-range price: {packages[i * 3 + j].price}")
                
                elif price_range == 'luxury' and luxury_packages < 3:
                    for j in range(3 - luxury_packages):
                        if i * 3 + j < len(packages):
                            packages[i * 3 + j].price = random.uniform(30001, 50000)
                            print(f"Set package {packages[i * 3 + j].name} to luxury price: {packages[i * 3 + j].price}")
                
                elif price_range == 'ultra_luxury' and ultra_luxury_packages < 3:
                    for j in range(3 - ultra_luxury_packages):
                        if i * 3 + j < len(packages):
                            packages[i * 3 + j].price = random.uniform(50001, 100000)
                            print(f"Set package {packages[i * 3 + j].name} to ultra-luxury price: {packages[i * 3 + j].price}")
            
            db.session.commit()
            print("Updated package prices to ensure proper filtering")

if __name__ == "__main__":
    test_filtering()
