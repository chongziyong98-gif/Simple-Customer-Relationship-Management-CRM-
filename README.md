# Simple Quotation CRM Dashboard

An internal quotation management system built with Flask and MySQL,
designed to track quotation lifecycle, win rate, and sales performance.

This project focuses on data visibility and decision support rather than
full-scale CRM features such as authentication or role management.

---

## Features
- Create and update quotations
- Automatic open / close date management
- Win / lose lifecycle tracking
- KPI dashboard:
  - Win rate
  - Won value
  - Average closing days
  - Aging quotations
- Date range and status filtering
- Default monthly performance view

---

## Tech Stack
- Python (Flask)
- MySQL
- Jinja2
- HTML / CSS

---

## Use Case
Designed for internal sales teams to:
- Monitor quotation performance
- Identify aging quotations
- Review monthly results for appraisal and planning

---

## Setup Instructions

### 1. Clone repository
git clone <repo_url>
cd Simple-Customer-Relationship-Management-CRM

### 2. Create MySQL database
CREATE DATABASE crm;

### 3. Initialize database schema
Run the SQL script located at:
crm_web/db/schema.sql

### 4. Configure environment variables
Create a .env file inside crm_web/:
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=crm
.env is ignored by Git and should not be committed.

### 5. Install dependencies
pip install flask mysql-connector-python python-dotenv

### 6. Run Application
python app.py

### 7. Access the dashboard at: 
http://127.0.0.1:5000/dashboard

## Notes
- This project is intended for internal use and demonstration purposes.
- Authentication and permission control are not implemented.