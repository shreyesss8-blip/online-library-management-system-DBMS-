# 📚 Online Library Management System

A web-based **Library Management System** developed as a collaborative **Database Management Systems (DBMS)** project.

The system provides functionality for managing books, members, book issue/return operations, fines, availability, and library records through a Flask-based web application connected to a MySQL/MariaDB database.

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
- `.env` configuration
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

- `IssueBook`
- `ReturnBook`

## 📂 Project Structure

```text
online-library-management-system/
│
├── app.py
├── init_db.py
├── requirements.txt
├── .env.example
│
├── templates/
├── static/
├── database/
│
├── smoke_test.py
├── browser_capture.js
├── generate_query_results.py
├── generate_sql_report.py
│
└── README.md
