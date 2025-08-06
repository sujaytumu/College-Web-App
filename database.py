from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, DECIMAL, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask import render_template

Base = declarative_base()

# ===================== MODELS =====================
class User(Base):
    __tablename__ = 'Users'
    Username = Column(String(50), primary_key=True)
    Password = Column(String(255), nullable=False)
    Role = Column(String(50), nullable=False)
    Student_ID = Column(Integer, ForeignKey('Students.Student_ID'))
    Instructor_ID = Column(Integer, ForeignKey('Instructors.Instructor_ID'))
    Admin_ID = Column(Integer, ForeignKey('Admins.Admin_ID'))

    student = relationship("Student", back_populates="user", uselist=False)
    instructor = relationship("Instructor", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User(Username='{self.Username}', Role='{self.Role}')>"

class Admin(Base):
    __tablename__ = 'Admins'
    Admin_ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100), nullable=False)
    Email = Column(String(100), unique=True, nullable=False)

    user = relationship("User", back_populates="admin", uselist=False)

    def __repr__(self):
        return f"<Admin(Admin_ID={self.Admin_ID}, Name='{self.Name}', Email='{self.Email}')>"

class Instructor(Base):
    __tablename__ = 'Instructors'
    Instructor_ID = Column(Integer, primary_key=True, autoincrement=True)
    Instructor_Name = Column(String(100), nullable=False)
    Email = Column(String(100), unique=True, nullable=False)

    user = relationship("User", back_populates="instructor", uselist=False)
    department = relationship("Department", back_populates="head_instructor", uselist=False)
    courses = relationship("Course", back_populates="instructor")

    def __repr__(self):
        return f"<Instructor(Instructor_ID={self.Instructor_ID}, Name='{self.Instructor_Name}', Email='{self.Email}')>"

class Student(Base):
    __tablename__ = 'Students'
    Student_ID = Column(Integer, primary_key=True, autoincrement=True)
    Student_Name = Column(String(100), nullable=False)
    Email = Column(String(100), unique=True, nullable=False)

    user = relationship("User", back_populates="student", uselist=False)
    enrollments = relationship("Enrollment", back_populates="student")

    def __repr__(self):
        return f"<Student(Student_ID={self.Student_ID}, Student_Name='{self.Student_Name}', Email='{self.Email}')>"

class Department(Base):
    __tablename__ = 'Departments'
    Department_ID = Column(Integer, primary_key=True, autoincrement=True)
    Department_Name = Column(String(100), nullable=False)
    Head_Instructor_ID = Column(Integer, ForeignKey('Instructors.Instructor_ID'))

    head_instructor = relationship("Instructor", back_populates="department")
    courses = relationship("Course", back_populates="department")

    def __repr__(self):
        return f"<Department(Department_ID={self.Department_ID}, Department_Name='{self.Department_Name}', Head_Instructor_ID={self.Head_Instructor_ID})>"

class Course(Base):
    __tablename__ = 'Courses'
    Course_ID = Column(Integer, primary_key=True, autoincrement=True)
    Course_Name = Column(String(100), nullable=False)
    Credits = Column(Integer, nullable=False)
    Instructor_ID = Column(Integer, ForeignKey('Instructors.Instructor_ID'), nullable=False)
    Department_ID = Column(Integer, ForeignKey('Departments.Department_ID'))
    Max_Marks = Column(DECIMAL(5, 2), nullable=False)
    Mid_Sem_Date = Column(Date)
    End_Sem_Date = Column(Date)

    department = relationship("Department", back_populates="courses")
    instructor = relationship("Instructor", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")

    def __repr__(self):
        return f"<Course(Course_ID={self.Course_ID}, Course_Name='{self.Course_Name}', Credits={self.Credits}, Instructor_ID={self.Instructor_ID}, Department_ID={self.Department_ID}, Max_Marks={self.Max_Marks}, Mid_Sem_Date={self.Mid_Sem_Date}, End_Sem_Date={self.End_Sem_Date})>"

class Enrollment(Base):
    __tablename__ = 'Enrollments'
    Enrollment_ID = Column(Integer, primary_key=True, autoincrement=True)
    Student_ID = Column(Integer, ForeignKey('Students.Student_ID'), nullable=False)
    Course_ID = Column(Integer, ForeignKey('Courses.Course_ID'), nullable=False)
    Enrollment_Date = Column(Date)
    Mid_Sem_Score = Column(DECIMAL(5, 2))
    End_Sem_Score = Column(DECIMAL(5, 2))

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Attendance(Base):
    __tablename__ = 'Attendance'
    Attendance_ID = Column(Integer, primary_key=True, autoincrement=True)
    Student_ID = Column(Integer, ForeignKey('Students.Student_ID'), nullable=False)
    Course_ID = Column(Integer, ForeignKey('Courses.Course_ID'), nullable=False)
    Date = Column(Date, nullable=False)
    Status = Column(String(10), nullable=False)

    student = relationship("Student")
    course = relationship("Course")

# ===================== DB CONNECTION =====================
connection_string = (
    "mysql+pymysql://avnadmin:AVNS_WStutZLtt9qGw1sScgt@mysql-201a572f-flask-database.c.aivencloud.com:22801/defaultdb?ssl_mode=REQUIRED&ssl_check_hostname=false&ssl_verify_cert=false"
)
engine = create_engine(connection_string)

# ✅ Create all tables in the database


Session = sessionmaker(bind=engine)
session = Session()

# ===================== FUNCTIONS =====================
def insert_user_data(user_data):
    role = user_data['role']
    name = user_data['name']
    email = user_data['email']
    username = user_data['username']
    password = user_data['password']

    if role == 'Admin':
        new_entry = Admin(Name=name, Email=email)
    elif role == 'Instructor':
        new_entry = Instructor(Instructor_Name=name, Email=email)
    elif role == 'Student':
        new_entry = Student(Student_Name=name, Email=email)
    else:
        raise ValueError("Invalid role")

    session.add(new_entry)
    session.commit()

    if role == 'Admin':
        user_entry = User(Username=username, Password=password, Role=role, Admin_ID=new_entry.Admin_ID)
    elif role == 'Instructor':
        user_entry = User(Username=username, Password=password, Role=role, Instructor_ID=new_entry.Instructor_ID)
    elif role == 'Student':
        user_entry = User(Username=username, Password=password, Role=role, Student_ID=new_entry.Student_ID)

    session.add(user_entry)
    session.commit()

def submit_attendance(student_id, course_id, date, status):
    new_attendance = Attendance(
        Student_ID=student_id,
        Course_ID=course_id,
        Date=date,
        Status=status
    )
    session.add(new_attendance)
    session.commit()

def verify_user_data(user_data):
    username = user_data['username']
    password = user_data['password']
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM Users WHERE Username = :username"), {'username': username}).first()
        if result is not None:
            role = result.Role
            if result.Password == password:
                return True, username, role
    return False, None, None

def insert_course(course_data):
    new_course = Course(
        Course_Name=course_data['course_name'],
        Instructor_ID=course_data['instructor_id'],
        Credits=course_data['credits'],
        Department_ID=course_data['department_id'],
        Max_Marks=course_data['max_marks'],
        Mid_Sem_Date=course_data['mid_sem_date'],
        End_Sem_Date=course_data['end_sem_date']
    )
    session.add(new_course)
    session.commit()

def fetch_courses():
    with engine.connect() as connection:
        courses = connection.execute(text("SELECT * FROM Courses")).fetchall()
        course_instructor_data = {}
        for course in courses:
            instructor = connection.execute(
                text("SELECT * FROM Instructors WHERE Instructor_ID = :instructor_id"),
                {'instructor_id': course.Instructor_ID}
            ).first()
            course_instructor_data[course.Course_ID] = {
                'course_name': course.Course_Name,
                'credits': course.Credits,
                'instructor_name': instructor.Instructor_Name,
                'instructor_email': instructor.Email
            }
    return course_instructor_data

def fetch_courses_student():
    courses = (
        session.query(Course, Instructor, Department)
        .join(Instructor, Course.Instructor_ID == Instructor.Instructor_ID)
        .join(Department, Course.Department_ID == Department.Department_ID)
        .all()
    )
    return courses

def fetch_enrolled_courses(student_id):
    enrolled_courses = (
        session.query(Course, Enrollment)
        .join(Enrollment, Enrollment.Course_ID == Course.Course_ID)
        .filter(Enrollment.Student_ID == student_id)
        .all()
    )
    return enrolled_courses

def new_enroll(student_id, course_id):
    new_enrollment = Enrollment(Student_ID=student_id, Course_ID=course_id)
    session.add(new_enrollment)
    session.commit()

def fetch_courses_for_instructor(instructor_id):
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT * FROM Courses
            WHERE Instructor_ID = :instructor_id
        """), {'instructor_id': instructor_id}).fetchall()
    return result
