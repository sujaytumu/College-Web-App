import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL connection
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
        # Check if Departments table exists
        cursor.execute("SHOW TABLES LIKE 'Departments'")
        result = cursor.fetchone()
        
        if not result:
            # Create Departments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Departments (
                    Department_ID INT AUTO_INCREMENT PRIMARY KEY,
                    Department_Name VARCHAR(100) NOT NULL
                )
            ''')
            print('Created Departments table')
        
        # Check if any departments exist
        cursor.execute('SELECT COUNT(*) as count FROM Departments')
        result = cursor.fetchone()
        print(f'Departments table exists with {result["count"]} records')
        
        if result['count'] == 0:
            # Insert default departments
            departments = [
                'Computer Science',
                'Mathematics', 
                'Physics',
                'Chemistry',
                'Biology',
                'Engineering',
                'Business',
                'Arts'
            ]
            for dept_name in departments:
                cursor.execute('INSERT INTO Departments (Department_Name) VALUES (%s)', (dept_name,))
            connection.commit()
            print('Added default departments')
        else:
            # Show existing departments
            cursor.execute('SELECT * FROM Departments')
            depts = cursor.fetchall()
            print('Existing departments:')
            for dept in depts:
                print(f'  {dept["Department_ID"]}: {dept["Department_Name"]}')
                
finally:
    connection.close()
