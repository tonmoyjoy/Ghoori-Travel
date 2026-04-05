import sqlite3
import os
import sys

# Connect to the database
db_path = os.path.join('instance', 'app.db')
print(f"Database path: {os.path.abspath(db_path)}")
print(f"Current size: {os.path.getsize(db_path) / (1024 * 1024):.2f} MB")

# Make a backup before any modifications
backup_path = db_path + ".backup"
print(f"Creating backup at {backup_path}")
import shutil
shutil.copy2(db_path, backup_path)

# Connect to the database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get list of tables
print("\nList of tables in the database:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"- {table[0]}: {count} rows")

# Directly specify the main package and event tables
package_tables = ['trip_package']
event_tables = ['local_event']

print("\nTargeting package tables:", package_tables)
print("Targeting event tables:", event_tables)

# Let's examine the structure of these tables
for table in package_tables + event_tables:
    print(f"\nStructure of {table}:")
    cursor.execute(f"PRAGMA table_info({table});")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]}){' PRIMARY KEY' if col[5] == 1 else ''}")

# Function to get primary key for a table
def get_primary_key(table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for col in columns:
        if col[5] == 1:  # Primary key
            return col[1]
    return None

# Remove some packages and events
packages_to_keep = 30  # Adjust this number as needed
events_to_keep = 30    # Adjust this number as needed

for table in package_tables:
    pk = get_primary_key(table)
    if not pk:
        print(f"Warning: Could not identify primary key for {table}")
        continue
        
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    total = cursor.fetchone()[0]
    
    if total > packages_to_keep:
        print(f"\nReducing {table} from {total} to {packages_to_keep} entries")
        # Keep only the newest entries (assuming ID increases with newer entries)
        cursor.execute(f"DELETE FROM {table} WHERE {pk} NOT IN (SELECT {pk} FROM {table} ORDER BY {pk} DESC LIMIT {packages_to_keep})")
        conn.commit()
        print(f"Deleted {total - packages_to_keep} entries")

for table in event_tables:
    pk = get_primary_key(table)
    if not pk:
        print(f"Warning: Could not identify primary key for {table}")
        continue
        
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    total = cursor.fetchone()[0]
    
    if total > events_to_keep:
        print(f"\nReducing {table} from {total} to {events_to_keep} entries")
        # Keep only the newest entries (assuming ID increases with newer entries)
        cursor.execute(f"DELETE FROM {table} WHERE {pk} NOT IN (SELECT {pk} FROM {table} ORDER BY {pk} DESC LIMIT {events_to_keep})")
        conn.commit()
        print(f"Deleted {total - events_to_keep} entries")

# Vacuum the database to reclaim space
print("\nVacuuming database to reclaim space...")
conn.execute("VACUUM")
conn.commit()

# Check final size
print(f"Final size: {os.path.getsize(db_path) / (1024 * 1024):.2f} MB")

# Close connection
conn.close()
print("\nDatabase reduction complete.")
