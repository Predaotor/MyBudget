import os 
from datetime import datetime, timedelta
from wtforms import StringField, SubmitField, DecimalField, DateField, SelectField, PasswordField 
from wtforms.validators import DataRequired,   EqualTo, ValidationError 
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate 
from wtforms.validators import DataRequired, NumberRange, EqualTo, ValidationError, Email, Length, Regexp
from datetime import datetime, timedelta, date
from sqlalchemy.exc import IntegrityError
from wtforms.validators import DataRequired, NumberRange, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_limiter import Limiter


# The above Python code is creating a SQLite database file path by first getting the directory of the
# current file (__file__), then joining it with the filename "mydatabase.db". The resulting path is
# formatted as a SQLite connection string and stored in the variable database_file.
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "mydatabase.db"))


# Setting up a Flask application with a SQLAlchemy database connection.
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SECRET_KEY"] = "3f329cf93a945946a121b9bd119fa482"
db = SQLAlchemy(app)
migrate=Migrate(app,db)


# The bellow code is setting up a login manager for a Flask application in Python. It initializes the
# login manager and sets the login view to 'login', which means that when a user tries to access a
# protected route without being authenticated, they will be redirected to the 'login' route to log in.
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='manager'

limiter=Limiter(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))



def strong_password(form, field):
    password = field.data
    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password):
        raise ValidationError('Password must be at least 8 characters long, contain at least one digit and one uppercase letter.')


# This class represents an Expense entity with attributes such as id, date, expensename, amount,
# category, and user_id.
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    expensename = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 

# The User class represents a user entity with attributes such as email, username, password, and
# expenses, along with methods for authentication and identification.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True)
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


# The Expensemodel class defines a form for capturing expense details including date, expense name,
# amount, category, and a submit button.
class Expensemodel(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    expensename = StringField('Expense Name', validators=[DataRequired()])
    amount = DecimalField(
        'Amount', validators=[DataRequired(), NumberRange(min=0, message="Amount must be positive")]
    )
    category = SelectField(
        'Category',
        choices=[
            ('Business', 'Business'),
            ('Food', 'Food'),
            ('Other', 'Other'),
            ('Rent', 'Rent'),
            ('Entertainment', 'Entertainment'),
            ('Transport', 'Transport')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Submit')
    
    
# The RegistrationForm class defines fields for email, username, password, and confirm password with
# specific validation criteria for each field.
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20), Regexp('^[A-Za-z][A-Za-z0-9.]*$', message="Usernames must contain only letters, numbers, dots, or underscores.")])
    password = PasswordField('Password', validators=[DataRequired(), strong_password])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up') 
    
# The LoginForm class defines a form with fields for email, password, and a submit button for user
# login.
class LoginForm(FlaskForm):
    email=StringField('Email', validators=[DataRequired()])
    password=PasswordField('Password', validators=[DataRequired()])
    submit=SubmitField('Login')





with app.app_context():
    db.create_all()

# Sign Up Form 
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password=generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user=User(username=form.username.data, email=form.email.data, password=hashed_password)
        try:
          db.session.add(new_user)
          db.session.commit()
          flash("You have successfully signed up!", "success")
          return redirect(url_for('login')) 
        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists. Please choose different ones.", "danger")

    return render_template('sign_up.html', form=form)

# Login Form
@limiter.limit("5 per minute")
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        
        return redirect(url_for('manager'))  # Redirect if already logged in
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("You have been logged in!", "success")
            return redirect(url_for('manager'))
        else:
            flash("Invalid email or password", "danger")
    return render_template('login.html', form=form)

# Log out Form 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('manager'))


    """
    This Python function adds a new expense to a database when a form is submitted and redirects to the
    expenses page.
    :return: The code is returning a redirect to the '/expenses' route if the form is successfully
    validated and the expense is added to the database. If the form is not validated, the code will
    render the 'add.html' template with the form for adding expenses.
    """
@app.route('/', methods=['GET', 'POST'])
@login_required
def add():
    
    form = Expensemodel()
    
    if form.validate_on_submit():
        date = form.date.data
        expensename = form.expensename.data
        amount = form.amount.data
        category = form.category.data

        expense = Expense(
            date=date,
            expensename=expensename,
            amount=amount,
            category=category,
            user_id=current_user.id,
              # Associate expense with logged-in user
        )
        db.session.add(expense)
        db.session.commit()

        return redirect('/expenses')

    return render_template('add.html', form=form)

# Delete Function 
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    expense = Expense.query.get_or_404(id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
    return redirect('/expenses')



    """
    This Python function updates an expense record in a web application using Flask and SQLAlchemy.
    
    :param id: The id parameter in the updateexpense route function is used to identify the specific
    expense that needs to be updated. It is passed as part of the route URL and is used to query the
    Expense object from the database that corresponds to the provided id. This allows the user to
    update
    :return: The code is returning a rendered template 'updateexpense.html' along with the form and
    expense data to be displayed on the webpage. If the form is validated and submitted successfully, it
    will update the expense details in the database and redirect the user to the '/expenses' route.
    """
@app.route('/updateexpense/<int:id>', methods=['GET', 'POST'])
@login_required
def updateexpense(id):
    expense = Expense.query.get_or_404(id)
    form = Expensemodel(obj=expense)

    if form.validate_on_submit():
        expense.date = form.date.data
        expense.expensename = form.expensename.data
        expense.amount = form.amount.data
        expense.category = form.category.data

        db.session.commit()
        return redirect('/expenses')

    return render_template('updateexpense.html', form=form, expense=expense)


    """
    This function handles the editing of an expense record in a Flask application.
    
    :param id: The id parameter in the route /edit/<int:id> is used to specify the unique identifier
    of the expense that the user wants to edit. This identifier is passed as an integer to the route
    when the user navigates to the edit page for a specific expense
    :return: The code is returning a rendered template 'edit.html' along with the form and expense data
    to be displayed on the webpage for editing an expense entry. If the form is successfully validated
    and submitted, the expense details are updated in the database, and the user is redirected to the
    '/expenses' route.
    """
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    expense = Expense.query.get_or_404(id)
    form = Expensemodel(obj=expense)

    if form.validate_on_submit():
        expense.date = form.date.data
        expense.expensename = form.expensename.data
        expense.amount = form.amount.data
        expense.category = form.category.data
        db.session.commit()

        return redirect('/expenses')

    return render_template('edit.html', form=form, expense=expense)



    """
    This function retrieves and categorizes expenses based on the selected time period and date,
    calculates total expenses, and renders the expenses data in a template.
    :return: The expenses data along with the total expenses and categorized totals for entertainment,
    business, food, other, rent, and transport are being returned in the expenses.html template.
    """
@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    selected_date = request.args.get('selected_date')
    time_period = request.args.get('time_period', 'all')

    if time_period == 'daily' and selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        expenses = Expense.query.filter_by(
            date=selected_date,
            user_id=current_user.id  # Filter by logged-in user
        ).all()
    elif time_period == 'weekly':
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        expenses = Expense.query.filter(
            Expense.date.between(start_of_week, end_of_week),
            user_id=current_user.id 
        ).all()
    elif time_period == 'monthly':
        current_month = datetime.today().month
        current_year = datetime.today().year
        expenses = Expense.query.filter(
            db.extract('month', Expense.date) == current_month,
            db.extract('year', Expense.date) == current_year,
            user_id=current_user.id
        ).all()
    else:
        expenses = Expense.query.filter_by(
            user_id=current_user.id  # Filter by logged-in user
        ).order_by(Expense.date.desc()).all()

   
    expense_data = calculate_expense_totals(expenses)

    return render_template(
        'expenses.html',
        expenses=expenses,
        total=expense_data['total'],
        t_entertainment=expense_data['t_entertainment'],
        t_business=expense_data['t_business'],
        t_food=f"{expense_data['t_food']:.2f}",
        t_other=expense_data['t_other'],
        t_rent=expense_data['t_rent'],
        t_transport=f"{expense_data['t_transport']:.2f}"
    )


def calculate_expense_totals(expenses):
   # This function  is calculating the total expenses and categorizing them into different
   # categories such as Business, Food, Other, Rent, Entertainment, and Transport. It iterates through
   # a list of expenses, sums up the total amount, and calculates the total amount for each category
   # based on the expense category. Finally, it returns a dictionary containing the total expenses and
   # the expenses for each category.
    
    total = 0
    t_business = 0
    t_food = 0
    t_other = 0
    t_rent = 0
    t_entertainment = 0
    t_transport = 0

    for expense in expenses:
        total += float(expense.amount)
        if expense.category == "Business":
            t_business += float(expense.amount)
        elif expense.category == "Food":
            t_food += float(expense.amount)
        elif expense.category == "Other":
            t_other += float(expense.amount)
        elif expense.category == "Rent":
            t_rent += float(expense.amount)
        elif expense.category == "Entertainment":
            t_entertainment += float(expense.amount)
        elif expense.category == "Transport":
            t_transport += float(expense.amount)

    return {
        'total': total,
        't_business': t_business,
        't_food': t_food,
        't_other': t_other,
        't_rent': t_rent,
        't_entertainment': t_entertainment,
        't_transport': t_transport
    }



    """
    This Python function in a Flask application retrieves and filters expenses based on a specified time
    period and date, calculates total expenses and category totals, and renders the data in a template
    for display.
    :return: The manager() function returns a rendered template 'manager.html' with the following
    variables passed to the template context:
    - time_period: The selected time period for filtering expenses.
    - selected_date: The selected date for filtering expenses.
    - expenses: The list of expenses based on the selected time period or date.
    - total: The total sum of all expenses.
    - t_ent
    """

@app.route("/manager", methods=["GET"])

def manager():
    selected_date = request.args.get('selected_date')
    time_period = request.args.get('time_period', 'all')

    # Ensure user_id is always filtered for the current user
    if time_period == 'daily' and selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        expenses = Expense.query.filter_by(
            date=selected_date ).all()
    elif time_period == 'weekly':
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        expenses = Expense.query.filter(
            Expense.date.between(start_of_week, end_of_week),
              # Filter by the authenticated user
        ).all()
    elif time_period == 'monthly':
        current_month = datetime.today().month
        current_year = datetime.today().year
        expenses = Expense.query.filter(
            db.extract('month', Expense.date) == current_month,
            db.extract('year', Expense.date) == current_year,
             # Filter by the authenticated user
        ).all()
    else:
        expenses = Expense.query.order_by(Expense.date.desc()).all()

    expense_data = calculate_expense_totals(expenses)

    return render_template(
        'manager.html',
        expenses=expenses,
        time_period=time_period,
        selected_date=selected_date,
        total=expense_data['total'],
        t_entertainment=expense_data['t_entertainment'],
        t_business=expense_data['t_business'],
        t_food=f"{expense_data['t_food']:.2f}",
        t_other=expense_data['t_other'],
        t_rent=expense_data['t_rent'],
        t_transport=f"{expense_data['t_transport']:.2f}"
    )



if __name__ == "__main__":
    if app.config['DEBUG']: 
        app.run(debug=True)
    else:
        app.run()