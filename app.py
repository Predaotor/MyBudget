import os
from datetime import datetime, timedelta
from wtforms import StringField, SubmitField, DecimalField, DateField, SelectField 
from wtforms.validators import DataRequired,   EqualTo, ValidationError 
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import (
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
    LoginManager
)
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import (
    StringField,
    SubmitField,
    DecimalField,
    DateField,
    SelectField,
    PasswordField
)
from wtforms.validators import DataRequired, NumberRange, EqualTo, ValidationError





project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "mydatabase.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SECRET_KEY"] = "3f329cf93a945946a121b9bd119fa482"
db = SQLAlchemy(app)



class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    expensename = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    


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


with app.app_context():
    db.create_all()



@app.route('/', methods=['GET', 'POST'])

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
            
        )
        db.session.add(expense)
        db.session.commit()

        return redirect('/expenses')

    return render_template('add.html', form=form)


@app.route('/delete/<int:id>')

def delete(id):
    expense = Expense.query.get_or_404(id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
    return redirect('/expenses')


@app.route('/updateexpense/<int:id>', methods=['GET', 'POST'])

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


@app.route('/edit/<int:id>', methods=['GET', 'POST'])

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


@app.route('/expenses', methods=['GET', 'POST'])

def expenses():
    selected_date = request.args.get('selected_date')
    time_period = request.args.get('time_period', 'all')

    if time_period == 'daily' and selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        expenses = Expense.query.filter_by(
            date=selected_date,
        ).all()
    elif time_period == 'weekly':
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        expenses = Expense.query.filter(
            Expense.date.between(start_of_week, end_of_week),
            
        ).all()
    elif time_period == 'monthly':
        current_month = datetime.today().month
        current_year = datetime.today().year
        expenses = Expense.query.filter(
            db.extract('month', Expense.date) == current_month,
            db.extract('year', Expense.date) == current_year,
            
        ).all()
    else:
        expenses =Expense.query.order_by(Expense.date.desc()).all()



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


@app.route("/manager", methods=["GET", "POST"])
def manager():
    
    time_period = request.args.get('time_period', 'all')
    selected_date = request.args.get('selected_date')


    
   
    if time_period == 'daily' and selected_date:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            expenses = Expense.query.filter_by(date=selected_date).all()
    elif time_period == 'weekly':
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            expenses = Expense.query.filter(
                Expense.date.between(start_of_week, end_of_week),
                
            ).all()
    elif time_period == 'monthly':
            current_month = datetime.today().month
            current_year = datetime.today().year
            expenses = Expense.query.filter(
                db.extract('month', Expense.date) == current_month,
                db.extract('year', Expense.date) == current_year,
                
            ).all()
    else:
            expenses = Expense.query.order_by(Expense.date.desc()).all()

    expense_data = calculate_expense_totals(expenses)

    return render_template('manager.html',
            time_period=time_period,
            selected_date=selected_date,
            expenses=expenses,
            total=expense_data['total'],
            t_entertainment=expense_data['t_entertainment'],
            t_business=expense_data['t_business'],
            t_food=f"{expense_data['t_food']:.2f}",
            t_other=expense_data['t_other'],
            t_rent=expense_data['t_rent'],
            t_transport=f"{expense_data['t_transport']:.2f}")





if __name__ == "__main__":
    app.run(debug=True)
