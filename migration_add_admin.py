import sqlite3

def add_is_admin_column():
    # Connect to the SQLite database
    conn = sqlite3.connect('instance/syncanddine.db')
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(group_members)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            # Add the is_admin column with default value of 0 (False)
            cursor.execute("ALTER TABLE group_members ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            print("Added is_admin column to group_members table")
            
            # Set group owners as admins
            cursor.execute("""
                UPDATE group_members
                SET is_admin = 1
                WHERE EXISTS (
                    SELECT 1 FROM "group"
                    WHERE "group".id = group_members.group_id
                    AND "group".owner_id = group_members.user_id
                )
            """)
            print("Set group owners as admins")
            
            # Commit the changes
            conn.commit()
            print("Migration completed successfully")
        else:
            print("is_admin column already exists")
    
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    add_is_admin_column()