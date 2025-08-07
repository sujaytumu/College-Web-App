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

try:
    with connection.cursor() as cursor:
        # Check Users table structure
        cursor.execute('DESCRIBE Users')
        columns = cursor.fetchall()
        print('Users table columns:')
        for col in columns:
            print(f'  {col["Field"]}: {col["Type"]}')
        
        print()
        
        # Check student counts
        cursor.execute("SELECT COUNT(*) as count FROM Users WHERE Role = 'Student'")
        student_users = cursor.fetchone()
        print(f'Student users in Users table: {student_users["count"]}')
        
        cursor.execute("SELECT COUNT(*) as count FROM Students")
        students = cursor.fetchone()
        print(f'Students in Students table: {students["count"]}')
        
        # Check orphaned students
        cursor.execute("""
            SELECT COUNT(*) as count FROM Students s 
            LEFT JOIN Users u ON s.Student_ID = u.Student_ID 
            WHERE u.Student_ID IS NULL
        """)
        orphaned = cursor.fetchone()
        print(f'Orphaned students (no Users entry): {orphaned["count"]}')
        
        # Show sample data
        print()
        print('Sample Users data:')
        cursor.execute("SELECT * FROM Users LIMIT 5")
        users = cursor.fetchall()
        for user in users:
            print(f'  {user}')
        
        print()
        print('Sample Students data:')
        cursor.execute("SELECT * FROM Students LIMIT 5")
        students = cursor.fetchall()
        for student in students:
            print(f'  {student}')

finally:
    connection.close()
