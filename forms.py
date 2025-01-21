from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    confirm_password = PasswordField('Passwort bestätigen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember = BooleanField('User merken') # Funktion wird nächsten Patch hinzugefügt
    submit = SubmitField('Login')

class AddGameForm(FlaskForm):
    name = StringField('Name des Spiels:', validators=[DataRequired(), Length(max=30, message="Der Name darf maximal 30 Zeichen lang sein.")])
    cover = FileField('Cover des Spiels:', validators=[FileAllowed(['jpg', 'png'], 'Nur Bilder sind erlaubt!')])
    submit = SubmitField('Spiel hinzufügen')
