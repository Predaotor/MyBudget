Expense Manager App
This is a web-based Expense Manager application built with Flask, SQLAlchemy, Flask-WTF, Flask-Migrate, and Flask-Login. It allows users to register, log in, add, update, and delete expenses. The app also categorizes expenses and provides filters based on daily, weekly, and monthly expense records.

Features
User Authentication (Sign-up, Login, Logout)
Secure password storage using Werkzeug's password hashing
Add, Update, and Delete Expenses
Categorization of Expenses (e.g., Business, Food, Rent, Entertainment)
Expense filtering based on time period (Daily, Weekly, Monthly)
Rate limiting for login attempts
Data stored in a SQLite database
Technologies
Python 3.x
Flask
SQLAlchemy (ORM)
Flask-Migrate (for database migrations)
Flask-Login (for user authentication)
Flask-WTF (for form handling)
SQLite (Database)
Prerequisites
Before you begin, ensure you have the following installed:

Python 3.x


Clone the repository:

bash
Copy code
git clone https://github.com/your-repo/expense-manager-app.git
cd expense-manager-app
Create a virtual environment and install dependencies:

bash
Copy code
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
Run the application:
python app.py 
bash
Copy code
flask run
Access the app:

Open http://localhost:5000 in your browser.


Access the app:

Open http://localhost:5000 in your browser.

Usage
1. Sign Up and Login
Users can register a new account via the Sign-Up page and log in with their credentials.

2. Add Expenses
After logging in, you can add expenses by filling out the form. You can input the expense name, amount, date, and category.

3. Manage Expenses
The app allows you to:

View all your expenses
Filter expenses by time period (Daily, Weekly, Monthly)
Update and delete expenses
Environment Variables
The app uses a few environment variables for configuration, particularly:

SECRET_KEY: A secret key for securely signing session cookies.
SQLALCHEMY_DATABASE_URI: The URI for the database connection (SQLite or other databases).
Database Migrations
For making any changes to the database schema, use Flask-Migrate commands:

Create a migration:

bash
Copy code
flask db migrate -m "Migration message"
Apply the migration:

bash
Copy code
flask db upgrade
Security
Passwords are stored securely using Werkzeug's password hashing functions. The application also limits login attempts using Flask-Limiter to prevent brute-force attacks.

License
This project is licensed under the MIT License. See the LICENSE file for more information.

Contributing
Contributions are welcome! If you have suggestions for improvements, feel free to fork the repository and submit a pull request.

This README provides a detailed overview of the project, instructions for setup, usage, and contributing guidelines. Feel free to adjust or expand it based on your needs!









