<h1 align="center">
Student Management System</h1>
<p align="center">A role-based web application for managing students, instructors, and administrators, built with Flask and MySQL.</p>
<p align="center">
  <img src="https://img.shields.io/badge/Flask-Backend-lightgrey?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/MySQL-Relational%20Database-blue?style=for-the-badge&logo=mysql" />
  <img src="https://img.shields.io/badge/HTML%2FCSS-Frontend-orange?style=for-the-badge&logo=html5" />
  <img src="https://img.shields.io/badge/Render-Deployed-green?style=for-the-badge&logo=render" />
</p>

---

### 🚀 Features

- 👨‍🎓 Student login, enrollment, attendance tracking, and score viewing
- 👩‍🏫 Instructor dashboard for course and student performance management
- 🧑‍💼 Admin control panel for managing courses, departments, and users
- 🔐 Secure session-based authentication with role validation
- 🗂 Data persistence using MySQL with proper relational mapping

---

### 🛠 Tech Stack

| Frontend | Backend | Database | Deployment |
|----------|---------|----------|------------|
| HTML/CSS | Flask (Python) | MySQL (Aiven) | Render |

---

### 📦 Local Setup

#### 1. Clone the repo

```bash
git clone https://github.com/your-username/student-management-system.git
cd student-management-system
```

#### 2. Set up Python environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Configure environment variables

Create a `.env` file in the root directory with the following keys:

```env
DB_HOST=your-db-host
DB_PORT=your-db-port
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=your-db-name
FLASK_SECRET_KEY=your-secret-key
```

#### 4. Start the Flask server

```bash
python app.py
```

---

### 📁 Folder Structure

```bash
student-management-system/
├── templates/                # HTML templates
├── static/                   # Static files (CSS, images)
├── app.py                    # Flask entry point
├── database.py               # Database functions (CRUD)
├── .env                      # Environment variables
├── requirements.txt          # Python packages
└── README.md                 # Project overview
```

---

### 🔄 Authentication Flow

1. Signup form creates a user based on role (Admin, Instructor, Student)
2. User credentials are stored in the `Users` table, linked to role-specific tables
3. On login, users are routed to their respective dashboards
4. Sessions manage access and restrict routes

---

### 🧠 Dashboard Logic

- **Student:** View and enroll in courses, see grades and attendance
- **Instructor:** View and manage students in assigned courses
- **Admin:** Add instructors, departments, and create new courses

---

### ✨ Future Enhancements

1. 🔐 Password hashing (e.g., bcrypt)
2. 📊 Visual charts for performance tracking
3. 🧾 Exportable attendance and marksheets (PDF/Excel)
4. 💬 Messaging system between students and instructors

---

### 🤝 Contributing

```bash
git checkout -b feature/your-feature
git commit -m "Add: your feature"
git push origin feature/your-feature
```

## 🌍 Contact

**💻 Author: Ashwa**<br>
📧 Email: aryankaushik207@gmail.com<br>
🐙 GitHub: [@aryan1921](https://github.com/aryan1921)<br>

<p align="center">
  <b>Built with clarity for classrooms. 🎓</b>
</p>
