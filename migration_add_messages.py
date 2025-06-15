import sqlite3

def add_messages_table():
    # Connect to the SQLite database
    conn = sqlite3.connect('instance/syncanddine.db')
    cursor = conn.cursor()
    
    try:
        # Check if the table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='message'")
        if not cursor.fetchone():
            # Create the message table
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
            
            # Commit the changes
            conn.commit()
            print("Migration completed successfully")
        else:
            print("Message table already exists")
    
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    add_messages_table()