import os
from pathlib import Path

import mysql.connector


ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "database" / "schema.sql"


def split_sql_script(sql_text):
    statements = []
    delimiter = ";"
    buffer = []

    for raw_line in sql_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("--"):
            continue

        if stripped.upper().startswith("DELIMITER "):
            if buffer:
                statements.append("\n".join(buffer).strip())
                buffer = []
            delimiter = stripped.split(maxsplit=1)[1]
            continue

        buffer.append(line)
        joined = "\n".join(buffer)
        if joined.endswith(delimiter):
            statements.append(joined[: -len(delimiter)].strip())
            buffer = []

    if buffer:
        statements.append("\n".join(buffer).strip())

    return [statement for statement in statements if statement]


def main():
    host = os.environ.get("MYSQL_HOST", "127.0.0.1")
    user = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    port = int(os.environ.get("MYSQL_PORT", "3306"))

    conn = mysql.connector.connect(host=host, user=user, password=password, port=port)
    cursor = conn.cursor()

    script = SCHEMA_PATH.read_text(encoding="utf-8")
    statements = split_sql_script(script)

    for statement in statements:
        cursor.execute(statement)
        conn.commit()

    cursor.close()
    conn.close()
    print(f"Executed {len(statements)} SQL statements successfully.")


if __name__ == "__main__":
    main()
