from flask import Flask, render_template, request, redirect, url_for, session
from database import (
    insert_user_data,
    verify_user_data,
    insert_course,
    fetch_courses,
    submit_attendance,
    fetch_courses_student,
    fetch_enrolled_courses,
    new_enroll,
    fetch_courses_for_instructor,
    fetch_student_details,
    fetch_instructor_details,
    fetch_admin_details,        
    fetch_all_instructors,
    update_student_marks,
    get_all_departments,
    get_students_in_course,
    get_students_for_attendance,
    
)
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_secret')


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'username': request.form.get('username'),
            'password': request.form.get('password'),
            'role': request.form.get('role')
        }
        insert_user_data(user_data)
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_data = {
            'username': request.form.get('username'),
            'password': request.form.get('password')
        }
        success, username, role = verify_user_data(user_data)
        if success:
            session['username'] = username
            session['role'] = role
            return redirect(url_for('dashboard', username=username))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/dashboard/<username>', methods=['GET', 'POST'])
def dashboard(username):
    if 'username' in session and session['username'] == username:
        role = session.get('role')

        if role == 'Admin':
            instructors = fetch_all_instructors()
            courses = fetch_courses()
            departments = get_all_departments()
            error = None
            if request.method == 'POST':
                try:
                    course_data = {
                        'course_name': request.form.get('course_name'),
                        'instructor_id': request.form.get('instructor_id'),
                        'credits': request.form.get('credits'),
                        'department_id': request.form.get('department_id'),
                        'max_marks': request.form.get('max_marks'),
                        'mid_sem_date': request.form.get('mid_sem_date'),
                        'end_sem_date': request.form.get('end_sem_date')
                    }
                    insert_course(course_data)
                    return redirect(url_for('dashboard', username=username))
                except ValueError as e:
                    error = str(e)
                except Exception as e:
                    error = f"Error creating course: {str(e)}"
            return render_template('admin_dashboard.html', username=username, instructors=instructors, courses=courses, departments=departments, error=error)

        elif role == 'Instructor':
            instructor_id = username
            courses = fetch_courses_for_instructor(instructor_id)
            return render_template('instructor_dashboard.html', username=username, courses=courses)

        elif role == 'Student':
            student = fetch_student_details(username)
            if student is None:
                # Handle case where student is not found
                return "Student not found", 404
            
            student_id = student['Student_ID']
            enrolled_courses = fetch_enrolled_courses(student_id)
            courses = fetch_courses_student()
            if request.method == 'POST':
                course_id = request.form['course_id']
                new_enroll(student_id, course_id)
                return redirect(url_for('dashboard', username=username))
            return render_template('student_dashboard.html', username=username, courses=courses, enrolled_courses=enrolled_courses)
        else:
            return "Invalid role", 403
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/students_in_course/<course_id>')
def students_in_course(course_id):
    students = get_students_in_course(course_id)
    return render_template('students_in_course.html', course_id=course_id, students=students)

@app.route('/mark_attendance_page/<course_id>')
def mark_attendance_page(course_id):
    students = get_students_for_attendance(course_id)
    return render_template('mark_attendance.html', course_id=course_id, students=students)

@app.route('/mark_attendance/<int:course_id>', methods=['POST'])
def mark_attendance(course_id):
    date = request.form.get('date')
    attendance_data = request.form.getlist('attendance')
    student_ids = request.form.getlist('student_ids[]')
    for student_id in student_ids:
        status = 'Present' if str(student_id) in attendance_data else 'Absent'
        submit_attendance(student_id, course_id, date, status)
    return redirect(url_for('students_in_course', course_id=course_id))

@app.route('/update_marks/<int:course_id>/<int:student_id>', methods=['POST'])
def update_marks(course_id, student_id):
    mid_sem_score = request.form.get('mid_sem_score')
    end_sem_score = request.form.get('end_sem_score')
    update_student_marks(course_id, student_id, mid_sem_score, end_sem_score)
    return redirect(url_for('students_in_course', course_id=course_id))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
