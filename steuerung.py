from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import current_user
from werkzeug.utils import secure_filename
import os
import io
from setup import get_db
from forms import AddGameForm
from flask_restx import Resource
from user import Userregistrierung, Userlogin

def home():
    if current_user.is_authenticated:
        return redirect(url_for('startseite'))
    return Userlogin()  # Allgemeine Startseite für nicht eingeloggte Benutzer

#Zeigt die Spiele an die man besitzt auf seiner Startseite
def startseite():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT game_id, name, cover FROM user_bibliothek WHERE user_id = ?", (current_user.id,))
    games = cur.fetchall()

    if games:
        return render_template('startseite.html', games=games)
    else:
        return render_template("startseite.html", games=None)

#Anzeige der Shop Spiele
def shop():
    search_query = request.args.get('q', default='', type=str)
    conn = get_db()
    cur = conn.cursor()
    if search_query:
        cur.execute("SELECT * FROM games WHERE name LIKE ? AND imBesitz IS NOT 1", ('%' + search_query + '%',))
    else:
        cur.execute("SELECT id, name, cover, preis, imBesitz FROM games WHERE imBesitz IS NOT 1")
    
    games = cur.fetchall()

    return render_template('shop.html', store_games=games, search_query=search_query)

def games_suchen_shop():
    query = request.args.get('query')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE name LIKE ? AND imBesitz IS NOT 1", ('%' + query + '%',))
    search_results = cur.fetchall()
    return render_template('Shop_suche.html', search_results=search_results, query=query)

def games_suchen_shop_bibliothek():
    query = request.args.get('query')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_bibliothek WHERE name LIKE ?", ('%' + query + '%',))
    search_results = cur.fetchall()
    return render_template('bibliothek_suche.html', search_results=search_results, query=query)

#Spiele die im shop gekauft werden hier zur Persönlichen Bibliothek hinzugefügt.
def spiel_hinzufügen(game_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, cover FROM games WHERE id = ? AND imBesitz = 0", (game_id,))
    game = cur.fetchone()
    if game:
        cur.execute("INSERT INTO user_bibliothek (user_id, game_id, name, cover) VALUES (?, ?, ?, ?)",
                    (current_user.id, game['id'], game['name'], game['cover']))
        cur.execute("UPDATE games SET imBesitz = 1 WHERE id = ?", (game["id"],))
        conn.commit()
        flash(f' Spiel {game["name"]} wurde erfolgreich gekauft!', 'success')
    else:
        flash('Game nicht gefunden.', 'danger')
    return redirect(url_for('shop'))


#erlaubt es dem User seinen eigenen Spiele in die Bibliothek hinzuzufügen
def persönliches_spiel_hinzufügen():
    form = AddGameForm()
    if form.validate_on_submit():
        game_name = form.name.data
        cover = form.cover.data

        if cover:
            filename = secure_filename(cover.filename)
            cover_path = os.path.join('static', 'uploads', filename)
            cover.save(cover_path)

            with open(cover_path, 'rb') as f:
                cover_blob = f.read()

            conn = get_db()
            cur = conn.cursor()
            cur.execute('INSERT INTO games (name, cover, preis, imBesitz, uploaded_by_user) VALUES (?, ?, ?, ?, ?)',
                        (game_name, cover_blob, 0, 1, 1))
            game_id = cur.lastrowid
            cur.execute('INSERT INTO user_bibliothek (user_id, game_id, name, cover) VALUES (?, ?, ?, ?)',
                        (current_user.id, game_id, game_name, cover_blob))
            conn.commit()
            cur.execute("SELECT name FROM games WHERE name = ? ", (game_name,))
            gamename = cur.fetchone()
            flash('Spiel erfolgreich zur persönlichen Bibliothek hinzugefügt!', 'success')
        else:
            flash('Ein Cover ist erforderlich!', 'danger')

        return redirect(url_for('startseite'))
    return render_template('persönliches_spiel_hinzufügen.html', form=form)

def cover(game_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT cover FROM games WHERE id = ?", (game_id,))
    game = cur.fetchone()
    if game:
        return send_file(io.BytesIO(game['cover']), mimetype='image/jpeg')
    return 'Cover nicht gefunden', 404

# Funktion für das entfernen der Spiele aus der eigenen Bibliothek
def game_löschen(game_id):
    conn = get_db()
    cur = conn.cursor()

    # Überprüfen, ob das Spiel in der Benutzerbibliothek existiert
    cur.execute("SELECT game_id, name FROM user_bibliothek WHERE user_id = ? AND game_id = ?", (current_user.id, game_id))
    game = cur.fetchone()

    if game:
        # Das Spiel aus der Benutzerbibliothek löschen
        cur.execute("DELETE FROM user_bibliothek WHERE user_id = ? AND game_id = ?", (current_user.id, game_id))
        # persönlich hochgeladene Spiele aus der Datenbank löschen
        cur.execute("DELETE FROM games WHERE id = ? AND uploaded_by_user = 1", (game_id,))
        cur.execute("UPDATE games SET imBesitz = 0 WHERE id = ? and uploaded_by_user IS NOT 1", (game_id,))
        conn.commit()
        flash(f' Spiel: {game["name"]} wurde gelöscht', 'success')
    else:
        flash('Kein Spiel hier!', 'danger')
    return redirect(url_for('startseite'))

# REST API Resources
class Register(Resource):
    def get(self):
        return Userregistrierung()
    def post(self):
        return Userregistrierung()

class Login(Resource):
    def get(self):
        return Userlogin()
    def post(self):
        return Userlogin()