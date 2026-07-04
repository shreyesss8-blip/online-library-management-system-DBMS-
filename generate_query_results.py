import os
from pathlib import Path

import mysql.connector


OUT = Path(__file__).resolve().parent / "docs" / "query_results.md"

QUERY_DATA = [
    ("Q1. Display all books with author and category", "Shows the catalog with related author and category information.",
     "SELECT b.title, a.author_name, c.category_name, b.available_copies FROM books b INNER JOIN authors a ON b.author_id = a.author_id INNER JOIN categories c ON b.category_id = c.category_id ORDER BY b.title LIMIT 8;"),
    ("Q2. Search books by title", "Finds books whose title contains the word Database.",
     "SELECT title, isbn, available_copies FROM books WHERE title LIKE '%Database%';"),
    ("Q3. List all active students", "Displays students currently marked as active members.",
     "SELECT usn, student_name, semester, email FROM students WHERE status = 'ACTIVE' ORDER BY student_name;"),
    ("Q4. Books currently issued", "Displays active issue transactions.",
     "SELECT bb.borrow_id, s.student_name, b.title, bb.issue_date, bb.due_date FROM borrowed_books bb INNER JOIN students s ON bb.student_id = s.student_id INNER JOIN books b ON bb.book_id = b.book_id WHERE bb.status = 'ISSUED';"),
    ("Q5. Overdue books using view", "Uses the overdue_books view to display delayed returns.",
     "SELECT * FROM overdue_books;"),
    ("Q6. Available books using view", "Lists books that currently have stock available.",
     "SELECT * FROM available_books ORDER BY title LIMIT 10;"),
    ("Q7. Most borrowed books", "Displays the top borrowed books in the sample data.",
     "SELECT b.title, COUNT(*) AS borrow_count FROM borrowed_books bb INNER JOIN books b ON bb.book_id = b.book_id GROUP BY b.book_id, b.title ORDER BY borrow_count DESC, b.title ASC LIMIT 5;"),
    ("Q8. Borrowing history of a particular student", "Shows all borrowing records for one student.",
     "SELECT s.usn, s.student_name, b.title, bb.issue_date, bb.return_date, bb.status FROM borrowed_books bb INNER JOIN students s ON bb.student_id = s.student_id INNER JOIN books b ON bb.book_id = b.book_id WHERE s.usn = '1VT22CS001';"),
    ("Q9. Total fine collected", "Calculates the total fine from returned books.",
     "SELECT SUM(fine_amount) AS total_fine_collected FROM borrowed_books WHERE status = 'RETURNED';"),
    ("Q10. Books by category", "Counts how many books belong to each category.",
     "SELECT c.category_name, COUNT(*) AS total_books FROM books b INNER JOIN categories c ON b.category_id = c.category_id GROUP BY c.category_id, c.category_name ORDER BY total_books DESC;"),
    ("Q11. Authors and total books in catalog", "Counts how many titles each author has in the system.",
     "SELECT a.author_name, COUNT(*) AS total_titles FROM books b INNER JOIN authors a ON b.author_id = a.author_id GROUP BY a.author_id, a.author_name ORDER BY total_titles DESC, a.author_name;"),
    ("Q12. Monthly borrowing statistics", "Shows the number of issues month-wise.",
     "SELECT DATE_FORMAT(issue_date, '%Y-%m') AS issue_month, COUNT(*) AS total_issues FROM borrowed_books GROUP BY DATE_FORMAT(issue_date, '%Y-%m') ORDER BY issue_month;"),
    ("Q13. Students with more than one borrowing record", "Finds frequent borrowers in the current dataset.",
     "SELECT s.usn, s.student_name, COUNT(*) AS borrow_count FROM borrowed_books bb INNER JOIN students s ON bb.student_id = s.student_id GROUP BY s.student_id, s.usn, s.student_name HAVING COUNT(*) > 1;"),
    ("Q14. Fine collected month-wise", "Aggregates collected fine amount by return month.",
     "SELECT DATE_FORMAT(return_date, '%Y-%m') AS return_month, SUM(fine_amount) AS fine_collected FROM borrowed_books WHERE status = 'RETURNED' GROUP BY DATE_FORMAT(return_date, '%Y-%m') ORDER BY return_month;"),
    ("Q15. Category-wise borrowing", "Shows how often books from each category were issued.",
     "SELECT c.category_name, COUNT(*) AS borrow_count FROM borrowed_books bb INNER JOIN books b ON bb.book_id = b.book_id INNER JOIN categories c ON b.category_id = c.category_id GROUP BY c.category_id, c.category_name ORDER BY borrow_count DESC;"),
]


def to_markdown_table(rows):
    if not rows:
        return "| Result |\n|---|\n| No rows returned |"
    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows[:8]:
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(lines)


def main():
    conn = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "online_library_db"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
    )
    cursor = conn.cursor(dictionary=True)

    blocks = ["# SQL Query Results\n", "The following outputs were generated from the live `online_library_db` sample dataset.\n"]
    for title, explanation, sql in QUERY_DATA:
        cursor.execute(sql)
        rows = cursor.fetchall()
        blocks.append(f"## {title}\n")
        blocks.append(f"**Explanation:** {explanation}\n")
        blocks.append("```sql")
        blocks.append(sql)
        blocks.append("```\n")
        blocks.append("**Sample Output:**\n")
        blocks.append(to_markdown_table(rows))
        blocks.append("")

    OUT.write_text("\n".join(blocks), encoding="utf-8")
    cursor.close()
    conn.close()
    print(f"Generated {OUT}")


if __name__ == "__main__":
    main()
