from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from database import engine
from sqlalchemy import text
from database import insert_user_data,verify_user_data,insert_course,Instructor,fetch_courses,fetch_courses_student,fetch_enrolled_courses,new_enroll,fetch_courses_for_instructor,submit_attendance

app = Flask(__name__)
app.secret_key = 'your_secret_key'  




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
            
            return redirect(url_for('dashboard', username=username))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/dashboard/<username>', methods=['GET', 'POST'])
def dashboard(username):
    if 'username' in session and session['username'] == username:
        with engine.connect() as connection:
            role = connection.execute(text("SELECT Role FROM Users WHERE Username = :username"), {'username': username}).scalar()
        if role is None:
            return "Role not found in session", 403
        
        
        
        with engine.connect() as connection:
            instructors = connection.execute(text("SELECT * FROM Instructors")).fetchall()
            courses=fetch_courses()
        if request.method == 'POST':
            if role == 'Admin':
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
            elif role=='Student':
                course_id = request.form['course_id']
                with engine.connect() as connection:
                    student=connection.execute(text("SELECT * FROM Students WHERE Student_ID= (SELECT Student_ID from Users where Username=:username)"),{'username':username}).first()
                    student_id=student.Student_ID
                    new_enroll(student_id,course_id)
                    
                    
                    return redirect(url_for('dashboard', username=username))
        if role == 'Admin':
            return render_template('admin_dashboard.html', username=username, instructors=instructors,courses=courses)
        elif role == 'Instructor':
            with engine.connect() as connection:
                instructor=connection.execute(text("select Instructor_ID from Users where Username=:username"),{'username':username}).first()
                instructor_id=instructor.Instructor_ID
                courses=fetch_courses_for_instructor(instructor_id)
                return render_template('instructor_dashboard.html', username=username,courses=courses)
        elif role == 'Student':
            with engine.connect() as connection:
                student=connection.execute(text("SELECT * FROM Students WHERE Student_ID= (SELECT Student_ID from Users where Username=:username)"),{'username':username}).first()
                student_id=student.Student_ID
                enrolled_courses=fetch_enrolled_courses(student_id)
                courses=fetch_courses_student()

            return render_template('student_dashboard.html', username=username,courses=courses,enrolled_courses=enrolled_courses)
        else:
            return "Invalid role", 403
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)  
    return redirect(url_for('login'))

@app.route('/students_in_course/<course_id>')
def students_in_course(course_id):
    with engine.connect() as connection:
        
        students = connection.execute(text("""
    SELECT 
        Students.Student_ID, 
        Students.Student_Name, 
        Enrollments.Mid_Sem_Score, 
        Enrollments.End_Sem_Score,
        -- Calculate attendance percentage
        COALESCE(ROUND(
            100.0 * SUM(CASE WHEN Attendance.Status = 'Present' THEN 1 ELSE 0 END) / NULLIF(COUNT(Attendance.Attendance_ID), 0), 2
        ), 0) AS Attendance_Percentage
    FROM 
        Enrollments
    JOIN 
        Students ON Enrollments.Student_ID = Students.Student_ID
    LEFT JOIN 
        Attendance ON Attendance.Student_ID = Students.Student_ID AND Attendance.Course_ID = Enrollments.Course_ID
    WHERE 
        Enrollments.Course_ID = :course_id
    GROUP BY 
        Students.Student_ID, Students.Student_Name, Enrollments.Mid_Sem_Score, Enrollments.End_Sem_Score
"""), {'course_id': course_id}).fetchall()

        
    return render_template('students_in_course.html', course_id=course_id, students=students)


@app.route('/mark_attendance_page/<course_id>')
def mark_attendance_page(course_id):
    with engine.connect() as connection:
        students = connection.execute(text("""
            SELECT Students.Student_ID, Students.Student_Name, Enrollments.Mid_Sem_Score, Enrollments.End_Sem_Score
            FROM Enrollments
            JOIN Students ON Enrollments.Student_ID = Students.Student_ID
            WHERE Enrollments.Course_ID = :course_id
        """), {'course_id': course_id}).fetchall()
    return render_template('mark_attendance.html', course_id=course_id, students=students)

@app.route('/mark_attendance/<int:course_id>', methods=['POST'])
def mark_attendance(course_id):
    date = request.form.get('date')
    attendance_data = request.form.getlist('attendance')
    student_ids = request.form.getlist('student_ids[]')

    with engine.connect() as connection:
        for student_id in student_ids:
            status = 'Present' if str(student_id) in attendance_data else 'Absent'
            submit_attendance(student_id,course_id,date,status)
    return redirect(url_for('students_in_course', course_id=course_id))


@app.route('/update_marks/<int:course_id>/<int:student_id>', methods=['POST'])
def update_marks(course_id, student_id):
    mid_sem_score = request.form.get('mid_sem_score')
    end_sem_score = request.form.get('end_sem_score')

    try:
        with engine.begin() as connection: 
            result = connection.execute(
                text("UPDATE Enrollments SET Mid_Sem_Score = :mid_sem_score, End_Sem_Score = :end_sem_score "
                     "WHERE Course_ID = :course_id AND Student_ID = :student_id"),
                {
                    'mid_sem_score': mid_sem_score,
                    'end_sem_score': end_sem_score,
                    'course_id': course_id,
                    'student_id': student_id
                }
            )

            
            print(f"Rows affected: {result.rowcount}")

    except Exception as e:
        print(f"Error occurred: {e}")
        return "An error occurred while updating marks.", 500

    return redirect(url_for('students_in_course', course_id=course_id))

if __name__ == '__main__':
    app.run(debug=True ,host='0.0.0.0')
