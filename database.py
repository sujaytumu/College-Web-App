# Rewritten `database.py` without SQLAlchemy for Python 3.13
import pymysql
from flask import render_template
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

# MySQL connection
# ✅ CHANGED: Removed hardcoded credentials — now loaded only from environment variables
# Make sure .env contains DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
connection = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),  # Default fallback is safe for GitHub
    user=os.getenv("DB_USER", "user_placeholder"),
    password=os.getenv("DB_PASSWORD", "password_placeholder"),
    database=os.getenv("DB_NAME", "dbname_placeholder"),
    port=int(os.getenv("DB_PORT", 3306)),
    cursorclass=pymysql.cursors.DictCursor
)

# ------------------------------------------------------------
# ✅ Everything below is unchanged functional logic
# ------------------------------------------------------------

def insert_user_data(user_data):
    with connection.cursor() as cursor:
        role = user_data['role']
        name = user_data['name']
        email = user_data['email']
        username = user_data['username']
        password = user_data['password']

        if role == 'Admin':
            cursor.execute("INSERT INTO Admins (Name, Email) VALUES (%s, %s)", (name, email))
            connection.commit()
            cursor.execute("SELECT LAST_INSERT_ID() AS id")
            admin_id = cursor.fetchone()['id']
            cursor.execute("INSERT INTO Users (Username, Password, Role, Admin_ID) VALUES (%s, %s, %s, %s)", (username, password, role, admin_id))

        elif role == 'Instructor':
            cursor.execute("INSERT INTO Instructors (Instructor_Name, Email) VALUES (%s, %s)", (name, email))
            connection.commit()
            cursor.execute("SELECT LAST_INSERT_ID() AS id")
            instructor_id = cursor.fetchone()['id']
            cursor.execute("INSERT INTO Users (Username, Password, Role, Instructor_ID) VALUES (%s, %s, %s, %s)", (username, password, role, instructor_id))

        elif role == 'Student':
            cursor.execute("INSERT INTO Students (Student_Name, Email) VALUES (%s, %s)", (name, email))
            connection.commit()
            cursor.execute("SELECT LAST_INSERT_ID() AS id")
            student_id = cursor.fetchone()['id']
            cursor.execute("INSERT INTO Users (Username, Password, Role, Student_ID) VALUES (%s, %s, %s, %s)", (username, password, role, student_id))

        connection.commit()

def verify_user_data(user_data):
    with connection.cursor() as cursor:
        username = user_data['username']
        password = user_data['password']
        cursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
        result = cursor.fetchone()
        if result and result['Password'] == password:
            return True, result['Username'], result['Role']
        return False, None, None

def submit_attendance(student_id, course_id, date, status):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO Attendance (Student_ID, Course_ID, Date, Status) VALUES (%s, %s, %s, %s)",
                       (student_id, course_id, date, status))
        connection.commit()

# ... (rest of your functions stay the same with no credential exposure)


def insert_course(course_data):
    with connection.cursor() as cursor:
        # Validate department_id
        department_id = course_data['department_id']
        if not department_id or str(department_id).strip() == '':
            raise ValueError("Department ID is required")
        
        try:
            department_id = int(department_id)
        except (ValueError, TypeError):
            raise ValueError("Department ID must be a valid integer")
        
        # Check if department exists
        cursor.execute("SELECT Department_ID FROM Departments WHERE Department_ID = %s", (department_id,))
        if not cursor.fetchone():
            raise ValueError(f"Department ID {department_id} does not exist")
        
        cursor.execute("""
            INSERT INTO Courses (Course_Name, Instructor_ID, Credits, Department_ID, Max_Marks, Mid_Sem_Date, End_Sem_Date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            course_data['course_name'],
            course_data['instructor_id'],
            course_data['credits'],
            department_id,
            course_data['max_marks'],
            course_data['mid_sem_date'],
            course_data['end_sem_date']
        ))
        connection.commit()

def fetch_courses():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Courses")
        courses = cursor.fetchall()
        course_instructor_data = {}
        for course in courses:
            cursor.execute("SELECT * FROM Instructors WHERE Instructor_ID = %s", (course['Instructor_ID'],))
            instructor = cursor.fetchone()
            course_instructor_data[course['Course_ID']] = {
                'course_name': course['Course_Name'],
                'credits': course['Credits'],
                'instructor_name': instructor['Instructor_Name'] if instructor else 'N/A',
                'instructor_email': instructor['Email'] if instructor else 'N/A'
            }
        return course_instructor_data

def new_enroll(student_id, course_id):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO Enrollments (Student_ID, Course_ID) VALUES (%s, %s)", (student_id, course_id))
        connection.commit()

def fetch_courses_for_instructor(instructor_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM Courses
            WHERE Instructor_ID = %s
        """, (instructor_id,))
        return cursor.fetchall()

def fetch_courses_student():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.*, i.Instructor_Name, i.Email AS Instructor_Email, d.Department_Name
            FROM Courses c
            JOIN Instructors i ON c.Instructor_ID = i.Instructor_ID
            JOIN Departments d ON c.Department_ID = d.Department_ID
        """)
        return cursor.fetchall()

def fetch_enrolled_courses(student_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.*, e.Mid_Sem_Score, e.End_Sem_Score
            FROM Enrollments e
            JOIN Courses c ON e.Course_ID = c.Course_ID
            WHERE e.Student_ID = %s
        """, (student_id,))
        return cursor.fetchall()
def fetch_student_details(student_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM Students
            WHERE Student_ID = %s
        """, (student_id,))
        return cursor.fetchone()
def fetch_instructor_details(instructor_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM Instructors
            WHERE Instructor_ID = %s
        """, (instructor_id,))
        return cursor.fetchone()
def fetch_admin_details(admin_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM Admins
            WHERE Admin_ID = %s
        """, (admin_id,))
        return cursor.fetchone()
def fetch_user_details(user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM Users
            WHERE User_ID = %s
        """, (user_id,))
        return cursor.fetchone()
def fetch_all_users():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Users")
        return cursor.fetchall()
def fetch_all_departments():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Departments")
        return cursor.fetchall()
def fetch_all_instructors():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Instructors")
        return cursor.fetchall()
def fetch_all_students():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Students")
        return cursor.fetchall()
def fetch_all_courses():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Courses")
        return cursor.fetchall()
def fetch_attendance(student_id, course_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM Attendance
            WHERE Student_ID = %s AND Course_ID = %s
        """, (student_id, course_id))
        return cursor.fetchall()
def fetch_attendance_for_course(course_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.*, s.Student_Name
            FROM Attendance a
            JOIN Students s ON a.Student_ID = s.Student_ID
            WHERE a.Course_ID = %s
        """, (course_id,))
        return cursor.fetchall()
def fetch_attendance_for_student(student_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.*, c.Course_Name
            FROM Attendance a
            JOIN Courses c ON a.Course_ID = c.Course_ID
            WHERE a.Student_ID = %s
        """, (student_id,))
        return cursor.fetchall()
def get_students_in_course(course_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.Student_ID, s.Student_Name, s.Email
            FROM Enrollments e
            JOIN Students s ON e.Student_ID = s.Student_ID
            WHERE e.Course_ID = %s
        """, (course_id,))
        return cursor.fetchall()
def get_students_for_attendance(course_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.Student_ID, s.Student_Name, s.Email
            FROM Enrollments e
            JOIN Students s ON e.Student_ID = s.Student_ID
            WHERE e.Course_ID = %s
        """, (course_id,))
        return cursor.fetchall()
def get_all_departments():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Departments")
        return cursor.fetchall()

def update_student_marks(course_id, student_id, mid_sem_score, end_sem_score):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE Enrollments 
            SET Mid_Sem_Score = %s, End_Sem_Score = %s 
            WHERE Course_ID = %s AND Student_ID = %s
        """, (mid_sem_score, end_sem_score, course_id, student_id))
        connection.commit()
