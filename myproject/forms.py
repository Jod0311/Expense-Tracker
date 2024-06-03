from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired
from models import User 

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=150)])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=150)])
    submit = SubmitField('Register')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first() # checks if username already ther in databasr RAHHH
        if user:
            raise ValidationError('Username already exists')

class ExpenseForm(FlaskForm):
    description = StringField('Description', validators=[InputRequired(), Length(min=1, max=200)])
    amount = FloatField('Amount', validators=[InputRequired()])
    category = SelectField('Category', choices=[('Food', 'Food'), ('Transport', 'Transport'), ('Rent', 'Rent'), ('Other', 'Other')], validators=[DataRequired()])
    submit = SubmitField('Add Expense')