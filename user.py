from flask import flash, redirect, url_for, render_template, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from setup import get_db
from forms import RegistrationForm, LoginForm
from models import User

def load_user(user_id):
    """Lade einen Benutzer basierend auf seiner ID aus der Datenbank."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE id = ?", (user_id,))
    user = cur.fetchone()
    if user:
        return User(id=user['id'], username=user['username'], email=user['email'])
    return None

def Userregistrierung():
    """Verarbeite die Registrierung eines neuen Benutzers."""
    form = RegistrationForm()
    if form.validate_on_submit():
        # Passwort hashen
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=16)
        
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                        (form.username.data, form.email.data, hashed_password))
            conn.commit()
            flash('Account erfolgreich erstellt, du kannst dich jetzt einloggen!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash(f'Datenbankfehler: {e}', 'danger')

    # Fehler bei der Validierung behandeln
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Fehler im Feld {field}: {error}', 'danger')

    return render_template('register.html', form=form)

def Userlogin():
    """Verarbeite den Benutzerlogin."""
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE email = ?", (form.email.data,))
        user = cur.fetchone()
        if user and check_password_hash(user['password'], form.password.data):
            user_obj = User(id=user['id'], username=user['username'], email=user['email'])
            login_user(user_obj, remember=form.remember.data)
            flash('Erfolgreich eingeloggt!', 'success')
            return redirect(url_for('startseite'))
        else:
            flash('Fehlerhafter Login, bitte Mail oder Passwort prüfen.', 'danger')

    return render_template('login.html', form=form)

def Userausloggen():
    """Logge den aktuellen Benutzer aus."""
    logout_user()
    flash('Du wurdest erfolgreich ausgeloggt.', 'success')
    return redirect(url_for('login'))