# Karya Siddhi Project - Reviewer Setup Guide

Welcome to the **Karya Siddhi** project! This guide will help you set up the project locally on your machine for testing and reviewing.

## 📋 Prerequisites
Before you begin, ensure you have the following installed on your system:
- **Python** (version 3.10 or higher)
- **PostgreSQL** (version 12 or higher)
- **Git** (optional, but recommended)

## 🚀 Setup Instructions

### Step 1: Extract the Project
Extract the provided ZIP file to your preferred directory.

### Step 2: Set up the Database (PostgreSQL)
Open your PostgreSQL terminal (psql) or pgAdmin and create the database needed for the project:
```sql
CREATE DATABASE karya_siddhi_db;
CREATE USER postgres WITH PASSWORD 'Nani@2003';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE karya_siddhi_db TO postgres;
```
*(Note: If your local PostgreSQL username/password is different, you will need to update `myproject/settings.py` -> `DATABASES` section to match your credentials).*

### Step 3: Create a Virtual Environment
Navigate to the project directory in your terminal and create a Python virtual environment:

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4: Install Dependencies
With the virtual environment activated, install the required Python packages:
```bash
pip install -r requirements.txt
```

### Step 5: Run Database Migrations
Apply the initial schema and models to your PostgreSQL database:
```bash
python manage.py migrate
```

### Step 6: Load Demo Data (Optional but Recommended)
If a `demo_data.json` file was provided or if you have access to a custom setup script, use it to populate the database with dummy services and users:
```bash
python manage.py loaddata demo_data.json
```
Alternatively, you can create a Superuser to access the admin portal:
```bash
python manage.py createsuperuser
```

### Step 7: Run the Development Server
Start the local Django server:
```bash
python manage.py runserver 8001
```

### Step 8: Access the Application
Open your web browser and go to:
- **Main Site:** http://127.0.0.1:8001/
- **Admin Portal (requires superuser access):** http://127.0.0.1:8001/admin-portal/
- **Django Default Admin:** http://127.0.0.1:8001/admin/

Enjoy reviewing the Karya Siddhi project!
