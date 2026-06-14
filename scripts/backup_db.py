"""
Script untuk backup database ke SQL file
Run: python scripts/backup_db.py
"""
import sys
import os
from datetime import datetime
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import get_settings

settings = get_settings()


def backup_database():
    """Backup database using pg_dump"""
    print("\n💾 Creating database backup...\n")
    
    # Parse database URL
    # Format: postgresql://user:password@host:port/database
    url_parts = settings.DATABASE_URL.replace("postgresql://", "").split("@")
    user_pass = url_parts[0].split(":")
    host_db = url_parts[1].split("/")
    host_port = host_db[0].split(":")
    
    db_user = user_pass[0]
    db_password = user_pass[1]
    db_host = host_port[0]
    db_port = host_port[1] if len(host_port) > 1 else "5432"
    db_name = host_db[1]
    
    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/hotel_db_backup_{timestamp}.sql"
    
    # Create backups directory
    os.makedirs("backups", exist_ok=True)
    
    # Set environment variable for password
    env = os.environ.copy()
    env["PGPASSWORD"] = db_password
    
    try:
        # Run pg_dump
        cmd = [
            "pg_dump",
            "-h", db_host,
            "-p", db_port,
            "-U", db_user,
            "-d", db_name,
            "-f", backup_file
        ]
        
        subprocess.run(cmd, env=env, check=True)
        
        file_size = os.path.getsize(backup_file)
        print(f"✅ Backup created successfully!")
        print(f"   File: {backup_file}")
        print(f"   Size: {file_size / 1024:.2f} KB\n")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup failed: {e}")
    except FileNotFoundError:
        print("❌ pg_dump not found. Please install PostgreSQL client tools.")


if __name__ == "__main__":
    backup_database()