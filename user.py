from flask import flash, redirect, url_for, render_template, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from setup import get_db
from forms import RegistrationForm, LoginForm
from models import User

def load_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE id = ?", (user_id,))
    user = cur.fetchone()
    if user:
        return User(id=user['id'], username=user['username'], email=user['email'])
    return None

def Userregistrierung():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                    (form.username.data, form.email.data, hashed_password))
        conn.commit()
        flash('Account erfolgreich erstellt, du kannst dich jetzt einloggen!', 'success')
        return redirect(url_for('login'))
    
    else:
        
        if 'password' in form.errors or 'confirm_password' in form.errors:
            flash('Die Passwörter stimmen nicht überein.', 'danger')

    return render_template('register.html', form=form)


def Userlogin():
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE email = ?", (form.email.data,))
        user = cur.fetchone()
        if user and check_password_hash(user['password'], form.password.data):
            user_obj = User(id=user['id'], username=user['username'], email=user['email'])
            login_user(user_obj, remember=form.remember.data)
            return redirect(url_for('startseite'))
        else:
            flash('Fehlerhafter Login, bitte Mail oder Passwort prüfen', 'danger')
    return render_template('login.html', form=form)

def Userausloggen():
    logout_user()
    flash('Du wurdest ausgeloggt.', 'success')
    return redirect(url_for('login'))