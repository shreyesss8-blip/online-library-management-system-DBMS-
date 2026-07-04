from datetime import date, datetime
from functools import wraps
import math
import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
import mysql.connector
from mysql.connector import Error, IntegrityError


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "library-mini-project-secret")

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "online_library_db"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
}

BOOKS_PER_PAGE = 8


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def query_all(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def query_one(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def execute_sql(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    conn.commit()
    cursor.close()
    conn.close()


def call_procedure(name, args):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    result = None
    try:
        cursor.callproc(name, args)
        for proc_result in cursor.stored_results():
            rows = proc_result.fetchall()
            if rows:
                result = rows[0]
                break
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return result


def validate_book_form(form, is_edit=False):
    errors = []
    title = form.get("title", "").strip()
    isbn = form.get("isbn", "").strip()
    publisher = form.get("publisher", "").strip()
    shelf_no = form.get("shelf_no", "").strip()
    total_copies = form.get("total_copies", "0").strip()
    available_copies = form.get("available_copies", total_copies).strip() if is_edit else total_copies

    if len(title) < 3:
        errors.append("Book title should have at least 3 characters.")
    if len(isbn) < 10:
        errors.append("ISBN should be at least 10 characters long.")
    if not publisher:
        errors.append("Publisher is required.")
    if not shelf_no:
        errors.append("Shelf number is required.")
    if not total_copies.isdigit() or int(total_copies) < 1:
        errors.append("Total copies must be at least 1.")
    if not available_copies.isdigit() or int(available_copies) < 0:
        errors.append("Available copies cannot be negative.")
    if total_copies.isdigit() and available_copies.isdigit() and int(available_copies) > int(total_copies):
        errors.append("Available copies cannot exceed total copies.")

    return errors


def validate_student_form(form):
    errors = []
    usn = form.get("usn", "").strip()
    student_name = form.get("student_name", "").strip()
    phone = form.get("phone", "").strip()
    semester = form.get("semester", "").strip()

    if len(usn) < 8:
        errors.append("Enter a valid USN.")
    if len(student_name) < 3:
        errors.append("Student name should have at least 3 characters.")
    if not semester.isdigit() or not 1 <= int(semester) <= 8:
        errors.append("Semester must be between 1 and 8.")
    if not phone.isdigit() or len(phone) != 10:
        errors.append("Phone number should contain exactly 10 digits.")

    return errors


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.errorhandler(Error)
def handle_db_error(error):
    message = getattr(error, "msg", str(error))
    return render_template("error.html", title="Database Error", message=message), 500


@app.errorhandler(Exception)
def handle_general_error(error):
    if hasattr(error, "code") and getattr(error, "name", None):
        return error
    return render_template("error.html", title="Application Error", message=str(error)), 500


@app.context_processor
def inject_globals():
    return {"current_year": date.today().year}


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        admin = query_one(
            "SELECT admin_id, full_name, username FROM admins WHERE username = %s AND password = %s AND status = 'ACTIVE'",
            (username, password),
        )
        if admin:
            session["admin_id"] = admin["admin_id"]
            session["admin_name"] = admin["full_name"]
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    stats = query_one(
        """
        SELECT
            (SELECT COUNT(*) FROM books) AS total_books,
            (SELECT COUNT(*) FROM students WHERE status = 'ACTIVE') AS active_students,
            (SELECT COUNT(*) FROM borrowed_books WHERE status = 'ISSUED') AS issued_books,
            (SELECT IFNULL(SUM(fine_amount), 0) FROM borrowed_books WHERE status = 'RETURNED') AS total_fine
        """
    )
    recent_issues = query_all(
        """
        SELECT bb.borrow_id, s.usn, s.student_name, b.title, bb.issue_date, bb.due_date, bb.status
        FROM borrowed_books bb
        INNER JOIN students s ON bb.student_id = s.student_id
        INNER JOIN books b ON bb.book_id = b.book_id
        ORDER BY bb.borrow_id DESC
        LIMIT 5
        """
    )
    top_books = query_all(
        """
        SELECT b.title, COUNT(*) AS borrow_count
        FROM borrowed_books bb
        INNER JOIN books b ON bb.book_id = b.book_id
        GROUP BY b.book_id, b.title
        ORDER BY borrow_count DESC, b.title ASC
        LIMIT 5
        """
    )
    overdue_books = query_all("SELECT * FROM overdue_books LIMIT 5")
    return render_template(
        "dashboard.html",
        stats=stats,
        recent_issues=recent_issues,
        top_books=top_books,
        overdue_books=overdue_books,
    )


@app.route("/books")
@login_required
def books():
    search = request.args.get("search", "").strip()
    page = max(int(request.args.get("page", 1)), 1)
    offset = (page - 1) * BOOKS_PER_PAGE
    like_term = f"%{search}%"

    count_row = query_one(
        """
        SELECT COUNT(*) AS total
        FROM books b
        INNER JOIN authors a ON b.author_id = a.author_id
        INNER JOIN categories c ON b.category_id = c.category_id
        WHERE b.title LIKE %s OR b.isbn LIKE %s OR a.author_name LIKE %s OR c.category_name LIKE %s
        """,
        (like_term, like_term, like_term, like_term),
    )
    total = count_row["total"]
    total_pages = max(math.ceil(total / BOOKS_PER_PAGE), 1)

    rows = query_all(
        """
        SELECT b.book_id, b.title, b.isbn, b.publisher, b.published_year, b.total_copies, b.available_copies, b.shelf_no,
               a.author_name, c.category_name
        FROM books b
        INNER JOIN authors a ON b.author_id = a.author_id
        INNER JOIN categories c ON b.category_id = c.category_id
        WHERE b.title LIKE %s OR b.isbn LIKE %s OR a.author_name LIKE %s OR c.category_name LIKE %s
        ORDER BY b.title ASC
        LIMIT %s OFFSET %s
        """,
        (like_term, like_term, like_term, like_term, BOOKS_PER_PAGE, offset),
    )
    return render_template(
        "books.html",
        books=rows,
        search=search,
        page=page,
        total_pages=total_pages,
    )


@app.route("/books/add", methods=["GET", "POST"])
@login_required
def add_book():
    authors = query_all("SELECT author_id, author_name FROM authors ORDER BY author_name")
    categories = query_all("SELECT category_id, category_name FROM categories ORDER BY category_name")
    if request.method == "POST":
        form = request.form
        errors = validate_book_form(form)
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            try:
                execute_sql(
                    """
                    INSERT INTO books (title, isbn, author_id, category_id, publisher, published_year, total_copies, available_copies, shelf_no, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        form.get("title", "").strip(),
                        form.get("isbn", "").strip(),
                        form.get("author_id"),
                        form.get("category_id"),
                        form.get("publisher", "").strip(),
                        form.get("published_year"),
                        form.get("total_copies"),
                        form.get("total_copies"),
                        form.get("shelf_no", "").strip(),
                        form.get("description", "").strip(),
                    ),
                )
                flash("Book added successfully.", "success")
                return redirect(url_for("books"))
            except IntegrityError:
                flash("Book could not be saved because ISBN must be unique.", "danger")
    return render_template("book_form.html", authors=authors, categories=categories, book=None)


@app.route("/books/edit/<int:book_id>", methods=["GET", "POST"])
@login_required
def edit_book(book_id):
    book = query_one("SELECT * FROM books WHERE book_id = %s", (book_id,))
    authors = query_all("SELECT author_id, author_name FROM authors ORDER BY author_name")
    categories = query_all("SELECT category_id, category_name FROM categories ORDER BY category_name")
    if not book:
        flash("Book record not found.", "danger")
        return redirect(url_for("books"))

    if request.method == "POST":
        form = request.form
        errors = validate_book_form(form, is_edit=True)
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            available_copies = min(int(form.get("available_copies", 0)), int(form.get("total_copies", 0)))
            try:
                execute_sql(
                    """
                    UPDATE books
                    SET title = %s, isbn = %s, author_id = %s, category_id = %s, publisher = %s,
                        published_year = %s, total_copies = %s, available_copies = %s, shelf_no = %s, description = %s
                    WHERE book_id = %s
                    """,
                    (
                        form.get("title", "").strip(),
                        form.get("isbn", "").strip(),
                        form.get("author_id"),
                        form.get("category_id"),
                        form.get("publisher", "").strip(),
                        form.get("published_year"),
                        form.get("total_copies"),
                        available_copies,
                        form.get("shelf_no", "").strip(),
                        form.get("description", "").strip(),
                        book_id,
                    ),
                )
                flash("Book details updated.", "success")
                return redirect(url_for("books"))
            except IntegrityError:
                flash("Book could not be updated because ISBN must be unique.", "danger")
    return render_template("book_form.html", authors=authors, categories=categories, book=book)


@app.route("/books/delete/<int:book_id>", methods=["POST"])
@login_required
def delete_book(book_id):
    active_issue = query_one(
        "SELECT COUNT(*) AS count_open FROM borrowed_books WHERE book_id = %s AND status = 'ISSUED'",
        (book_id,),
    )
    if active_issue["count_open"] > 0:
        flash("Book cannot be deleted while it is issued to a student.", "warning")
    else:
        execute_sql("DELETE FROM books WHERE book_id = %s", (book_id,))
        flash("Book deleted successfully.", "info")
    return redirect(url_for("books"))


@app.route("/students", methods=["GET", "POST"])
@login_required
def students():
    if request.method == "POST":
        form = request.form
        errors = validate_student_form(form)
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            try:
                execute_sql(
                    """
                    INSERT INTO students (usn, student_name, gender, department, semester, email, phone, join_date, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        form.get("usn", "").strip(),
                        form.get("student_name", "").strip(),
                        form.get("gender"),
                        form.get("department", "").strip(),
                        form.get("semester"),
                        form.get("email", "").strip(),
                        form.get("phone", "").strip(),
                        form.get("join_date"),
                        form.get("status"),
                    ),
                )
                flash("Student added successfully.", "success")
                return redirect(url_for("students"))
            except IntegrityError:
                flash("Student could not be saved because USN, email, or phone already exists.", "danger")

    rows = query_all("SELECT * FROM students ORDER BY student_name ASC")
    return render_template("students.html", students=rows, edit_student=None)


@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    student = query_one("SELECT * FROM students WHERE student_id = %s", (student_id,))
    if not student:
        flash("Student record not found.", "danger")
        return redirect(url_for("students"))

    if request.method == "POST":
        form = request.form
        errors = validate_student_form(form)
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            try:
                execute_sql(
                    """
                    UPDATE students
                    SET usn = %s, student_name = %s, gender = %s, department = %s, semester = %s,
                        email = %s, phone = %s, join_date = %s, status = %s
                    WHERE student_id = %s
                    """,
                    (
                        form.get("usn", "").strip(),
                        form.get("student_name", "").strip(),
                        form.get("gender"),
                        form.get("department", "").strip(),
                        form.get("semester"),
                        form.get("email", "").strip(),
                        form.get("phone", "").strip(),
                        form.get("join_date"),
                        form.get("status"),
                        student_id,
                    ),
                )
                flash("Student details updated.", "success")
                return redirect(url_for("students"))
            except IntegrityError:
                flash("Student could not be updated because USN, email, or phone already exists.", "danger")

    rows = query_all("SELECT * FROM students ORDER BY student_name ASC")
    return render_template("students.html", students=rows, edit_student=student)


@app.route("/students/delete/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):
    active_issue = query_one(
        "SELECT COUNT(*) AS count_open FROM borrowed_books WHERE student_id = %s AND status = 'ISSUED'",
        (student_id,),
    )
    if active_issue["count_open"] > 0:
        flash("Student cannot be removed because one or more books are still issued.", "warning")
    else:
        execute_sql("DELETE FROM students WHERE student_id = %s", (student_id,))
        flash("Student removed from the system.", "info")
    return redirect(url_for("students"))


@app.route("/authors", methods=["GET", "POST"])
@login_required
def authors():
    if request.method == "POST":
        form = request.form
        try:
            execute_sql(
                "INSERT INTO authors (author_name, country, birth_year) VALUES (%s, %s, %s)",
                (form.get("author_name", "").strip(), form.get("country", "").strip(), form.get("birth_year") or None),
            )
            flash("Author added successfully.", "success")
            return redirect(url_for("authors"))
        except IntegrityError:
            flash("Author name already exists.", "danger")
    rows = query_all("SELECT * FROM authors ORDER BY author_name ASC")
    return render_template("authors.html", authors=rows)


@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    if request.method == "POST":
        form = request.form
        try:
            execute_sql(
                "INSERT INTO categories (category_name, rack_label) VALUES (%s, %s)",
                (form.get("category_name", "").strip(), form.get("rack_label", "").strip()),
            )
            flash("Category added successfully.", "success")
            return redirect(url_for("categories"))
        except IntegrityError:
            flash("Category name or rack label already exists.", "danger")
    rows = query_all("SELECT * FROM categories ORDER BY category_name ASC")
    return render_template("categories.html", categories=rows)


@app.route("/issue", methods=["GET", "POST"])
@login_required
def issue_book():
    students_list = query_all("SELECT student_id, usn, student_name FROM students WHERE status = 'ACTIVE' ORDER BY student_name")
    books_list = query_all("SELECT book_id, title, available_copies FROM books WHERE available_copies > 0 ORDER BY title")
    if request.method == "POST":
        form = request.form
        result = call_procedure("IssueBook", (form.get("student_id"), form.get("book_id"), form.get("issue_date"), form.get("due_date")))
        if result and result.get("status_code") == "SUCCESS":
            flash(result.get("status_message"), "success")
            return redirect(url_for("history"))
        flash(result.get("status_message", "Unable to issue the book."), "danger")
    return render_template("issue_book.html", students=students_list, books=books_list)


@app.route("/return", methods=["GET", "POST"])
@login_required
def return_book():
    active_loans = query_all(
        """
        SELECT bb.borrow_id, s.student_name, s.usn, b.title, bb.issue_date, bb.due_date
        FROM borrowed_books bb
        INNER JOIN students s ON bb.student_id = s.student_id
        INNER JOIN books b ON bb.book_id = b.book_id
        WHERE bb.status = 'ISSUED'
        ORDER BY bb.due_date ASC
        """
    )
    if request.method == "POST":
        borrow_id = request.form.get("borrow_id")
        return_date = request.form.get("return_date")
        result = call_procedure("ReturnBook", (borrow_id, return_date))
        if result and result.get("status_code") == "SUCCESS":
            flash(
                f"{result.get('status_message')} Fine collected: Rs. {float(result.get('fine_amount', 0)):.2f}",
                "success",
            )
            return redirect(url_for("history"))
        flash(result.get("status_message", "Unable to return the book."), "danger")
    return render_template("return_book.html", active_loans=active_loans)


@app.route("/history")
@login_required
def history():
    rows = query_all(
        """
        SELECT bb.borrow_id, s.usn, s.student_name, b.title, bb.issue_date, bb.due_date, bb.return_date, bb.status, bb.fine_amount
        FROM borrowed_books bb
        INNER JOIN students s ON bb.student_id = s.student_id
        INNER JOIN books b ON bb.book_id = b.book_id
        ORDER BY bb.borrow_id DESC
        """
    )
    return render_template("history.html", history=rows)


@app.route("/reports")
@login_required
def reports():
    data = {
        "available_books": query_all("SELECT * FROM available_books LIMIT 10"),
        "overdue_books": query_all("SELECT * FROM overdue_books"),
        "borrow_by_category": query_all(
            """
            SELECT c.category_name, COUNT(*) AS borrow_count
            FROM borrowed_books bb
            INNER JOIN books b ON bb.book_id = b.book_id
            INNER JOIN categories c ON b.category_id = c.category_id
            GROUP BY c.category_id, c.category_name
            ORDER BY borrow_count DESC, c.category_name ASC
            """
        ),
        "monthly_stats": query_all(
            """
            SELECT DATE_FORMAT(issue_date, '%Y-%m') AS issue_month, COUNT(*) AS total_issues
            FROM borrowed_books
            GROUP BY DATE_FORMAT(issue_date, '%Y-%m')
            ORDER BY issue_month DESC
            """
        ),
    }
    return render_template("reports.html", **data)


@app.template_filter("datefmt")
def datefmt(value):
    if not value:
        return "-"
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y")
    return value.strftime("%d-%m-%Y")


if __name__ == "__main__":
    app.run(debug=True)
