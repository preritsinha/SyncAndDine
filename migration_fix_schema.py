import sqlite3

def fix_schema():
    # Connect to the SQLite database
    conn = sqlite3.connect('instance/syncanddine.db')
    cursor = conn.cursor()
    
    try:
        # Check restaurant table structure
        cursor.execute("PRAGMA table_info(restaurant)")
        restaurant_columns = {column[1]: column[2] for column in cursor.fetchall()}
        
        # Define all expected columns for restaurant table
        expected_columns = {
            'id': 'INTEGER',
            'name': 'VARCHAR(100)',
            'location': 'VARCHAR(100)',
            'latitude': 'FLOAT',
            'longitude': 'FLOAT',
            'rating': 'FLOAT',
            'cuisine_type': 'VARCHAR(50)',
            'price_range': 'VARCHAR(20)',
            'is_vegetarian': 'BOOLEAN',
            'distance': 'FLOAT',
            'image_url': 'VARCHAR(200)',
            'created_at': 'DATETIME'
        }
        
        # Add any missing columns to restaurant table
        for column, data_type in expected_columns.items():
            if column not in restaurant_columns:
                default_value = ""
                if data_type == 'FLOAT':
                    default_value = " DEFAULT 0"
                elif data_type == 'BOOLEAN':
                    default_value = " DEFAULT 0"
                elif data_type == 'DATETIME':
                    default_value = " DEFAULT CURRENT_TIMESTAMP"
                
                cursor.execute(f"ALTER TABLE restaurant ADD COLUMN {column} {data_type}{default_value}")
                print(f"Added {column} column to restaurant table")
        
        # Check if message table exists and has is_read column
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='message'")
        if not cursor.fetchone():
            # Create message table if it doesn't exist
            cursor.execute('''
                CREATE TABLE message (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    recipient_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT 0,
                    FOREIGN KEY (sender_id) REFERENCES user (id),
                    FOREIGN KEY (recipient_id) REFERENCES user (id)
                )
            ''')
            print("Created message table")
        else:
            # Check if is_read column exists in message table
            cursor.execute("PRAGMA table_info(message)")
            message_columns = [column[1] for column in cursor.fetchall()]
            
            if 'is_read' not in message_columns:
                cursor.execute("ALTER TABLE message ADD COLUMN is_read BOOLEAN DEFAULT 0")
                print("Added is_read column to message table")
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully")
    
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()