import sqlite3
import os

def migrate_database():
    # Path to your SQLite database
    db_path = os.path.join('instance', 'app.db')
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add photo_path column to travel_diary_photo if it doesn't exist
        cursor.execute('''
            ALTER TABLE travel_diary_photo 
            ADD COLUMN photo_path VARCHAR(200) NOT NULL DEFAULT ''
        ''')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' not in str(e):
            print(f"Error adding photo_path column: {e}")
    
    try:
        # Create travel_diary_video table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS travel_diary_video (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                diary_id INTEGER NOT NULL,
                video_path VARCHAR(200) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (diary_id) REFERENCES travel_diary (id)
            )
        ''')
    except sqlite3.OperationalError as e:
        print(f"Error creating travel_diary_video table: {e}")
    
    # Commit the changes
    conn.commit()
    conn.close()
    
    print("Database migration completed successfully!")

if __name__ == '__main__':
    migrate_database() 