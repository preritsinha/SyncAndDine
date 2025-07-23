#!/usr/bin/env python3
"""
Database Creation Script for SyncAndDine

This script creates all database tables based on the SQLAlchemy models.
Run this if you delete the database file to recreate it.

Usage: python create_db.py
"""

from syncanddine import create_app, db

def create_database():
    """Create all database tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Print table info
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")

if __name__ == '__main__':
    create_database()