# Deployment Guide: Campus Events Discovery App

This guide provides step-by-step instructions for setting up and deploying the **Campus Events Discovery App** on a local development environment or a production server.

## Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8+**
- **pip** (Python package manager)
- **SQLite** (Included with Python)

## Local Setup Instructions

1. **Clone or Extract the Project**
   Extract the project files into your desired directory.

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   Install the required Django packages:
   ```bash
   pip install django pillow
   ```
   *(Note: Pillow is required for handling event images)*

4. **Apply Database Migrations**
   Initialize the SQLite database and create the schema:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Seed the Database (Optional but Recommended)**
   Populate the app with sample events, categories, and images:
   ```bash
   python manage.py seed_events
   ```

6. **Create a Superuser (Admin)**
   To access the Admin Dashboard, create an administrator account:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**
   ```bash
   python manage.py run_server
   ```
   The app will be accessible at `http://127.0.0.1:8000/`.

## Production Deployment Tips

### 1. Security Settings
In `campus_events/settings.py`, ensure:
- `DEBUG = False`
- `ALLOWED_HOSTS = ['yourdomain.com', 'localhost']`
- `SECRET_KEY` is moved to an environment variable.

### 2. Static and Media Files
Run the following command to collect all static assets for the web server:
```bash
python manage.py collectstatic
```
Ensure your web server (Nginx/Apache) is configured to serve the `static/` and `media/` directories.

### 3. Database
For high-traffic production environments, consider switching from **SQLite** to **PostgreSQL** or **MySQL** by updating the `DATABASES` setting in `settings.py`.

---
*Created for the Campus Events Discovery Project Deliverables.*
