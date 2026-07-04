import os
from pathlib import Path

import mysql.connector


OUT = Path(__file__).resolve().parent / "docs" / "sql-output.html"

QUERIES = [
    (
        "Most Borrowed Books",
        """
        SELECT b.title AS Title, COUNT(*) AS Times_Issued
        FROM borrowed_books bb
        INNER JOIN books b ON bb.book_id = b.book_id
        GROUP BY b.book_id, b.title
        ORDER BY Times_Issued DESC, Title ASC
        LIMIT 5
        """,
    ),
    (
        "Overdue Books",
        """
        SELECT student_name AS Student, title AS Book, days_overdue AS Days_Overdue, current_fine AS Current_Fine
        FROM overdue_books
        ORDER BY Days_Overdue DESC
        """,
    ),
    (
        "Monthly Borrowing Statistics",
        """
        SELECT DATE_FORMAT(issue_date, '%Y-%m') AS Issue_Month, COUNT(*) AS Total_Issues
        FROM borrowed_books
        GROUP BY DATE_FORMAT(issue_date, '%Y-%m')
        ORDER BY Issue_Month DESC
        """,
    ),
]


def main():
    conn = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "online_library_db"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
    )
    cursor = conn.cursor(dictionary=True)

    sections = []
    for title, sql in QUERIES:
        cursor.execute(sql)
        rows = cursor.fetchall()
        headers = rows[0].keys() if rows else []
        table_rows = "".join(
            "<tr>" + "".join(f"<td>{value}</td>" for value in row.values()) + "</tr>"
            for row in rows
        )
        header_html = "".join(f"<th>{header}</th>" for header in headers)
        sections.append(
            f"""
            <section class='panel'>
                <h2>{title}</h2>
                <pre>{sql.strip()}</pre>
                <table>
                    <thead><tr>{header_html}</tr></thead>
                    <tbody>{table_rows}</tbody>
                </table>
            </section>
            """
        )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'>
        <title>SQL Output</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #eef3fb; color: #20324f; padding: 24px; }}
            .panel {{ background: #fff; border: 1px solid #d6e0ee; border-radius: 14px; padding: 20px; margin-bottom: 18px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px 8px; border-bottom: 1px solid #e6edf7; text-align: left; }}
            pre {{ background: #f7f9fd; padding: 14px; border-radius: 10px; overflow-x: auto; }}
            h1, h2 {{ margin-top: 0; }}
        </style>
    </head>
    <body>
        <h1>Online Library Management System - SQL Outputs</h1>
        {''.join(sections)}
    </body>
    </html>
    """

    OUT.write_text(html, encoding="utf-8")
    cursor.close()
    conn.close()
    print(f"Generated {OUT}")


if __name__ == "__main__":
    main()
