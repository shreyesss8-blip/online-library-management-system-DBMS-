# 📚 Online Library Management System

A web-based Library Management System developed as a collaborative Database Management Systems (DBMS) project.

The system provides functionality for managing books, members, book issue and return operations, fines, availability, and library records through a Flask-based web application connected to a MySQL/MariaDB database.

## 🚀 Features

- Book management
- Member/student management
- Book issue and return
- Due-date tracking
- Fine calculation
- Book search and availability tracking
- Dashboard statistics and reports
- Session-based authentication
- Form validation
- Pagination
- Stored procedures
- Database triggers
- SQL views
- Automated testing and verification

## 🛠️ Tech Stack

### Backend
- Python
- Flask
- Jinja2

### Frontend
- HTML
- CSS
- JavaScript

### Database
- MySQL / MariaDB
- SQL
- Stored Procedures
- Triggers
- Views

### Database Connectivity
- mysql-connector-python

### Testing & Automation
- Python smoke tests
- Playwright
- Browser automation

### Configuration
- Environment variables
- .env configuration
- Python virtual environment

## 🗄️ DBMS Concepts Implemented

- Relational database design
- Database schema design
- Primary and foreign keys
- SQL queries and aggregations
- CRUD operations
- Stored procedures
- Database triggers
- SQL views
- Database relationships
- Backend-database connectivity

### Stored Procedures

- IssueBook
- ReturnBook

## ⚙️ Setup

### 1. Clone the repository

git clone https://github.com/shreyesss8-blip/online-library-management-system-DBMS-.git

cd online-library-management-system-DBMS-

### 2. Create a virtual environment

python -m venv venv

### 3. Activate the virtual environment

Windows:

venv\Scripts\activate

### 4. Install dependencies

pip install -r requirements.txt

### 5. Configure environment variables

Create a .env file using .env.example.

Example configuration:

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
SECRET_KEY=your_secret_key

Do not commit the .env file or real credentials to GitHub.

### 6. Initialize the database

python init_db.py

### 7. Run the application

python app.py

The application will normally be available at:

http://127.0.0.1:5000

## 🧪 Testing

The project includes smoke tests, SQL verification scripts, and browser automation.

Smoke Test:

python smoke_test.py

Generate Query Results:

python generate_query_results.py

Generate SQL Report:

python generate_sql_report.py

Playwright is used for automated browser flows, smoke testing, and screenshot capture.

## 👥 Team Project

This project was developed collaboratively as a DBMS academic project.

### Team

- Shreyes S.S.
- Tarun SU
- Shreyas SM

## 👨‍💻 My Contribution

- Database design and SQL implementation
- Flask backend development
- Database connectivity
- Stored procedures, triggers, and views
- Testing and debugging

Update this section to contain only the work personally contributed.

## 📌 Project Goal

The goal of this project was to apply DBMS concepts to a practical web application and gain hands-on experience with relational database design, SQL, backend development, and database-driven application workflows.

## 📄 Academic Project

Developed as part of a Database Management Systems (DBMS) academic project.
