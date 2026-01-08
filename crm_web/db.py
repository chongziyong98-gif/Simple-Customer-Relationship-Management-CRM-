import mysql.connector
from mysql.connector import errors
from datetime import date, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def get_quotation_by_no(quotation_no):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT quotation_no, company_name, project, quoted_price, status "
        "FROM crm_data WHERE quotation_no = %s",
        (quotation_no,)
    )
    row = cursor.fetchone()

    cursor.close()
    conn.close()
    return row

def update_quotation_full(quotation_no, company, project, price, status):
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()

    # 🔑 核心规则
    if status in ("won", "lose"):
        close_date = today
    else:
        close_date = today + timedelta(days=30)

    cursor.execute("""
        UPDATE crm_data
        SET
            company_name = %s,
            project = %s,
            quoted_price = %s,
            status = %s,
            close_date = %s
        WHERE quotation_no = %s
    """, (
        company,
        project,
        price,
        status,
        close_date,
        quotation_no
    ))

    conn.commit()
    cursor.close()
    conn.close()

def insert_quotation(form):
    quotation_no = form["quotation_no"]
    company = form["company_name"]
    project = form["project"]
    price = form["quoted_price"]
    status = form["status"]

    open_date = date.today()
    close_date = open_date + timedelta(days=30)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO crm_data
            (
                quotation_no,
                company_name,
                project,
                quoted_price,
                status,
                open_date,
                close_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            quotation_no,
            company,
            project,
            price,
            status,
            open_date,
            close_date
        ))

        conn.commit()
        success = True
        quotation = None

    except errors.IntegrityError as e:
        if e.errno == 1062:
            success = False
            quotation = get_quotation_by_no(quotation_no)
        else:
            raise

    finally:
        cursor.close()
        conn.close()

    return success, quotation


def get_all_quotations(status=None, start_date=None, end_date=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            quotation_no,
            company_name,
            project,
            quoted_price,
            status,
            open_date,
            close_date
        FROM crm_data
        WHERE 1=1
    """
    params = []

    if status:
        query += " AND status = %s"
        params.append(status)

    if start_date:
        query += " AND open_date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND open_date <= %s"
        params.append(end_date)

    query += " ORDER BY open_date DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows

def get_quotations_by_status(status):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT quotation_no, company_name, project, quoted_price, status
        FROM crm_data
        WHERE status = %s
         AND open_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
        ORDER BY quotation_no DESC
    """, (status,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_total_quotation_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM crm_data")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return total

def get_won_quotation_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM crm_data
        WHERE status = 'won'
    """)
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return total

def get_total_quotation_value():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(quoted_price) FROM crm_data")
    total = cursor.fetchone()[0] or 0

    cursor.close()
    conn.close()
    return total


def get_won_value():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(quoted_price)
        FROM crm_data
        WHERE status = 'won'
    """)
    total = cursor.fetchone()[0] or 0

    cursor.close()
    conn.close()
    return total

def auto_close_expired_quotations():
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()

    cursor.execute("""
        UPDATE crm_data
        SET
            status = 'lose',
            close_date = %s
        WHERE
            status NOT IN ('won', 'lose')
            AND close_date < %s
    """, (today, today))

    affected = cursor.rowcount

    conn.commit()
    cursor.close()
    conn.close()

    return affected

def get_win_rate():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) AS win_count,
            SUM(CASE WHEN status = 'lose' THEN 1 ELSE 0 END) AS lose_count
        FROM crm_data
        WHERE open_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    """)

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    win = row["win_count"] or 0
    lose = row["lose_count"] or 0

    if win + lose == 0:
        return 0

    return round(win / (win + lose) * 100, 2)

def get_avg_closing_days():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT AVG(DATEDIFF(close_date, open_date)) AS avg_days
        FROM crm_data
        WHERE status IN ('win', 'lose')
          AND open_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
    """)

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return round(row["avg_days"], 1) if row["avg_days"] else 0

def get_aging_quotations(days=14):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS aging_count
        FROM crm_data
        WHERE status NOT IN ('win', 'lose')
          AND DATEDIFF(CURDATE(), open_date) > %s
    """, (days,))

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return row["aging_count"]

def get_current_month_quotations():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            quotation_no,
            company_name,
            project,
            quoted_price,
            status,
            open_date,
            close_date
        FROM crm_data
        WHERE
            YEAR(open_date) = YEAR(CURDATE())
            AND MONTH(open_date) = MONTH(CURDATE())
        ORDER BY open_date DESC
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_quotations_by_date_range(start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            quotation_no,
            company_name,
            project,
            quoted_price,
            status,
            open_date,
            close_date
        FROM crm_data
        WHERE open_date BETWEEN %s AND %s
        ORDER BY open_date DESC
    """, (start_date, end_date))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
