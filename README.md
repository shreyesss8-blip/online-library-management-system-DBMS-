# Online Library Management System

`Online Library Management System` is a VTU-style DBMS mini project built using `Flask`, `MySQL`, `HTML`, `CSS`, and `JavaScript`. It covers the common library workflows used in a college environment such as book management, student management, issue and return processing, due-date tracking, fine calculation, and dashboard reporting.

## Main Features

- Admin login with session handling
- Book, author, and category management
- Student/member management
- Search, issue, and return book workflows
- Stored procedures for issue and return operations
- Triggers for availability update and fine calculation
- Views for available books and overdue books
- Dashboard statistics and reports

## Project Structure

```text
online-library-management-system/
├── app.py
├── requirements.txt
├── .env.example
├── database/
│   ├── schema.sql
│   └── queries.sql
├── docs/
│   ├── report.md
│   ├── viva.md
│   ├── poster.html
│   └── screenshots/
├── static/
│   ├── css/style.css
│   └── js/app.js
└── templates/
```

## Setup Steps

1. Install Python 3.11 or later on Windows.
2. Install MySQL or MariaDB Server.
3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Set environment variables if your MySQL username or password is different from the default.

```powershell
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD=""
$env:MYSQL_DATABASE="online_library_db"
$env:SECRET_KEY="library-mini-project-secret"
```

5. Initialize the database:

```powershell
python init_db.py
```

6. Run the application:

```powershell
python app.py
```

7. Open `http://127.0.0.1:5000`

## Local MariaDB Setup Used During Verification

The project was verified locally using:

- MariaDB 12.2
- Local data directory: `mariadb-data/`
- Local config: [mariadb-local.ini](C:\Users\SHREYES\Documents\Codex\2026-05-16\online-library-management-system\mariadb-local.ini)

If you want to use the same local setup:

```powershell
& "C:\Program Files\MariaDB 12.2\bin\mysql_install_db.exe" --datadir="C:\Users\SHREYES\Documents\Codex\2026-05-16\online-library-management-system\mariadb-data" --port=3306 --default-user
Start-Process -FilePath "C:\Program Files\MariaDB 12.2\bin\mariadbd.exe" -ArgumentList "--defaults-file=C:\Users\SHREYES\Documents\Codex\2026-05-16\online-library-management-system\mariadb-data\my.ini" -WindowStyle Hidden
```

## Default Login

- Username: `admin`
- Password: `admin123`

## Notes

- The project is intentionally kept simple and readable so that it fits a `4th semester DBMS mini project` level.
- Passwords are stored as plain text only because this is an academic demo project. In a real system, passwords should be hashed.
- Verification scripts included:
  - `init_db.py`
  - `smoke_test.py`
  - `browser_capture.js`
  - `generate_sql_report.py`
  - `generate_query_results.py`
