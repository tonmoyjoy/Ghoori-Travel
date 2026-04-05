import sqlite3
import os

# Connect to the database
print("Connecting to database...")
db_path = os.path.join('instance', 'app.db')
print(f"Database path: {os.path.abspath(db_path)}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get list of tables
print("\nList of tables in the database:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

# For each table, show schema and sample data
for table in tables:
    table_name = table[0]
    print(f"\n=== Table: {table_name} ===")
    
    # Get schema
    print("\nSchema:")
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]}){' PRIMARY KEY' if col[5] == 1 else ''}")
    
    # Get sample data (first 5 rows)
    print("\nSample data (up to 5 rows):")
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"  {row}")
        else:
            print("  No data")
    except Exception as e:
        print(f"  Error getting data: {e}")

# Close connection
conn.close()
print("\nDatabase inspection complete.")
