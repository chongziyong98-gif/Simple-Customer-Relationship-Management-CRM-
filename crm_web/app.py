from db import (
    get_quotations_by_date_range,
    get_current_month_quotations,
    insert_quotation,
    get_quotation_by_no,
    update_quotation_full,
    auto_close_expired_quotations,
)

from flask import Flask, render_template, request, redirect, url_for
import mysql
from mysql.connector import errors
from datetime import date

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Czy0331!",
        database="crm"
    )

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    auto_close_expired_quotations()

    status = request.args.get("status")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # 1️⃣ 决定数据集
    if start_date and end_date:
        quotations = get_quotations_by_date_range(start_date, end_date)
        view_label = f"Filtered: {start_date} → {end_date}"
    else:
        quotations = get_current_month_quotations()
        view_label = "This Month"

    if status:
        quotations = [q for q in quotations if q["status"] == status]
        view_label = f"Status: {status.capitalize()}"


    # 2️⃣ KPI —— 永远计算（不放在 if 里）
    total_count = len(quotations)

    total_value = sum(q["quoted_price"] for q in quotations)

    won_count = sum(
        1 for q in quotations if q["status"] == "won"
    )

    won_value = sum(
        q["quoted_price"]
        for q in quotations
        if q["status"] == "won"
    )

    win_rate = (
        (won_count / total_count) * 100
        if total_count else 0
    )

    closing_days = [
        (q["close_date"] - q["open_date"]).days
        for q in quotations
        if q["status"] in ("won", "lose")
        and q["close_date"] is not None
    ]

    avg_closing_days = (
        sum(closing_days) / len(closing_days)
        if closing_days else 0
    )

    today = date.today()
    aging_count = sum(
        1
        for q in quotations
        if q["status"] not in ("won", "lose")
        and q["close_date"] < today
    )

    kpis = {
        "total_count": total_count,
        "won_count": won_count,
        "win_rate": win_rate,
        "total_value": total_value,
        "won_value": won_value,
        "aging_count": aging_count,
        "avg_closing_days": avg_closing_days
    }

    return render_template(
        "dashboard.html",
        quotations=quotations,
        kpis=kpis,
        view_label=view_label
    )


@app.route("/add", methods=["GET", "POST"])
def add_quotation():
    if request.method == "POST":
        success, quotation = insert_quotation(request.form)

        if success:
            return redirect(url_for("dashboard"))
        else:
            return render_template(
                "quotation_exists.html",
                quotation=quotation
            )

    return render_template("add_quotation.html")


@app.route("/update/<path:quotation_no>", methods=["GET", "POST"])
def update_quotation(quotation_no):
    quotation = get_quotation_by_no(quotation_no)

    if not quotation:
        return "Quotation not found", 404

    if request.method == "POST":
        update_quotation_full(
            quotation_no,
            request.form["company_name"],
            request.form["project"],
            request.form["quoted_price"],
            request.form["status"]
        )
        return redirect("/dashboard")

    return render_template(
        "update_quotation.html",
        quotation=quotation
    )

print(app.url_map)
if __name__ == "__main__":
    app.run(debug=True)

