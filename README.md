# tailorNow

A Django project configured to use MySQL as the database backend.

## Setup Instructions

1. **Create and activate a virtual environment:**
   ```
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Configure MySQL database:**
   - Update `tailorNow/settings.py` with your MySQL database credentials under the `DATABASES` section.

4. **Run migrations:**
   ```
   python manage.py migrate
   ```

5. **Start the development server:**
   ```
   python manage.py runserver
   ```

## Notes
- Ensure MySQL server is running and accessible.
- Install MySQL server and client if not already installed on your system.


