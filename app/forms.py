from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Użytkownik', validators=[DataRequired(message="Podaj login")]) #walidator - trzeba cos wpisac
    password = PasswordField('Hasło', validators=[DataRequired(message="Podaj hasło")]) #walidator - trzeba cos wpisac
    submit = SubmitField('Zaloguj się')