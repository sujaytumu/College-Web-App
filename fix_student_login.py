#!/usr/bin/env python3
"""
Script to fix student login issues by creating missing User entries
for students who exist in Students table but not in Users table.
"""

import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

connection = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", 3306)),
    cursorclass=pymysql.cursors.DictCursor
)

def fix_orphaned_students():
    """Create User entries for students who exist in Students but not in Users."""
    with connection.cursor() as cursor:
        # Find orphaned students
        cursor.execute("""
            SELECT s.Student_ID, s.Student_Name, s.Email 
            FROM Students s 
            LEFT JOIN Users u ON s.Student_ID = u.Student_ID 
            WHERE u.Student_ID IS NULL
        """)
        orphaned_students = cursor.fetchall()
        
        if not orphaned_students:
            print("No orphaned students found.")
            return
        
        print(f"Found {len(orphaned_students)} orphaned students. Creating User entries...")
        
        for student in orphaned_students:
            # Generate username from email or name
            username = student['Email'].split('@')[0] if student['Email'] else f"student{student['Student_ID']}"
            
            # Check if username already exists
            cursor.execute("SELECT COUNT(*) as count FROM Users WHERE Username = %s", (username,))
            if cursor.fetchone()['count'] > 0:
                username = f"{username}{student['Student_ID']}"
            
            # Create User entry
            cursor.execute("""
                INSERT INTO Users (Username, Password, Role, Student_ID) 
                VALUES (%s, %s, %s, %s)
            """, (username, 'temp_password', 'Student', student['Student_ID']))
            
            print(f"Created User entry for {student['Student_Name']} (Username: {username})")
        
        connection.commit()
        print("Successfully fixed all orphaned students!")

if __name__ == "__main__":
    try:
        fix_orphaned_students()
    finally:
        connection.close()
