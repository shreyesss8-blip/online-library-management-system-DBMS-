import os

import mysql.connector

from app import app


def query_one(sql):
    conn = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "online_library_db"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def main():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200

    invalid = client.post("/", data={"username": "wrong", "password": "wrong"}, follow_redirects=True)
    assert b"Invalid username or password." in invalid.data

    valid = client.post("/", data={"username": "admin", "password": "admin123"}, follow_redirects=True)
    assert b"Dashboard" in valid.data

    books = client.get("/books?search=Database")
    assert books.status_code == 200
    assert b"Database" in books.data

    add_student = client.post(
        "/students",
        data={
            "usn": "1VT22CS099",
            "student_name": "Kiran Test",
            "gender": "Male",
            "department": "CSE",
            "semester": "4",
            "email": "kirantest99@vtu.edu",
            "phone": "9876500999",
            "join_date": "2026-05-16",
            "status": "ACTIVE",
        },
        follow_redirects=True,
    )
    assert b"Student added successfully." in add_student.data

    issue = client.post(
        "/issue",
        data={
            "student_id": "11",
            "book_id": "10",
            "issue_date": "2026-05-16",
            "due_date": "2026-05-26",
        },
        follow_redirects=True,
    )
    assert b"Book issued successfully." in issue.data

    unavailable = client.post(
        "/issue",
        data={
            "student_id": "11",
            "book_id": "10",
            "issue_date": "2026-05-16",
            "due_date": "2026-05-26",
        },
        follow_redirects=True,
    )
    assert b"Same student already has this book issued." in unavailable.data

    borrow_row = query_one("SELECT MAX(borrow_id) AS borrow_id FROM borrowed_books WHERE student_id = 11")
    borrow_id = str(borrow_row["borrow_id"])

    returned = client.post(
        "/return",
        data={"borrow_id": borrow_id, "return_date": "2026-05-29"},
        follow_redirects=True,
    )
    assert b"Fine collected: Rs. 15.00" in returned.data

    report = client.get("/reports")
    assert report.status_code == 200
    assert b"Monthly Borrowing Statistics" in report.data

    print("Smoke tests completed successfully.")


if __name__ == "__main__":
    main()
