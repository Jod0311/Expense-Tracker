from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import init_db, get_user_by_id, get_user_by_username, insert_user, insert_expense, get_expenses_by_user
from user import User
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

init_db()

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# Define the forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class ExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    amount = StringField('Amount', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Add Expense')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = get_user_by_username(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        if insert_user(username, password):
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
        flash('Username already exists.')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = ExpenseForm()
    if form.validate_on_submit():
        description = form.description.data
        amount = float(form.amount.data)
        category = form.category.data
        date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        user_id = current_user.id
        insert_expense(description, amount, date, user_id, category)
        flash('Expense added successfully')
        return redirect(url_for('index'))
    
    expenses = get_expenses_by_user(current_user.id)
    total_expenses = sum(expense['amount'] for expense in expenses)  # Calculate the sum of expenses
    
    # Group expenses by month
    grouped_expenses = defaultdict(list)
    for expense in expenses:
        month = datetime.strptime(expense['date'], '%Y-%m-%d %H:%M:%S').strftime('%B %Y')
        grouped_expenses[month].append(expense)
    
    # Create DataFrame from the grouped expenses
    df = pd.DataFrame([(month, sum(expense['amount'] for expense in expenses_in_month)) for month, expenses_in_month in grouped_expenses.items()], columns=['Month', 'Total Expenses'])
    
    # Plot the graph
    plt.figure(figsize=(10, 6))
    plt.bar(df['Month'], df['Total Expenses'])
    plt.xlabel('Month')
    plt.ylabel('Total Expenses (₹)')
    plt.title('Monthly Expenses')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    plt.savefig('static/monthly_expenses.png')  # Save the plot as a PNG file
    plt.close()  # Close the plot to free up memory
    
    return render_template('index.html', grouped_expenses=grouped_expenses, total_expenses=total_expenses, form=form)

if __name__ == '__main__':
    app.run(debug=True)
