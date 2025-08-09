import os
from flask import Flask, redirect, url_for, request, render_template, current_app
from flask_login import LoginManager, login_required, current_user
from flask_bootstrap import Bootstrap
from setup import initialize_db
from user import load_user, Userausloggen, Userregistrierung, Userlogin
import steuerung
from flask_restx import Api, Resource, fields, Namespace

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
bootstrap = Bootstrap(app)

api = Api(app, version='1.0', title='Spielbibliothek API', description='Spielbibliothek API', doc='/api', prefix='/api')

# Authentication Namespace
auth_ns = Namespace('auth', description='Authentication operations')

@login_manager.user_loader
def load_user_wrapper(user_id):
    return load_user(user_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    return Userregistrierung()


@app.route('/login', methods=['GET', 'POST'])
def login():
    return Userlogin()

@app.route('/')
def index():
    return steuerung.home()

@app.route('/startseite')
@login_required
def startseite():
    return steuerung.startseite()

@app.route('/shop', methods=['GET', 'POST'])
@login_required
def shop():
    return steuerung.shop()

@app.route('/games_suchen_shop', methods=['GET'])
@login_required
def games_suchen_shop():
    return steuerung.games_suchen_shop()

@app.route('/games_suchen_bibliothek', methods=['GET'])
@login_required
def games_suchen_bibliothek():
    return steuerung.games_suchen_shop_bibliothek()

@app.route('/spiel_hinzufügen/<int:game_id>')
@login_required
def spiel_hinzufügen(game_id):
    return steuerung.spiel_hinzufügen(game_id)

@app.route('/persönliches_spiel_hinzufügen', methods=['GET', 'POST'])
@login_required
def persönliches_spiel_hinzufügen():
    return steuerung.persönliches_spiel_hinzufügen()

@app.route('/cover/<int:game_id>')
def cover(game_id):
    return steuerung.cover(game_id)

@app.route('/logout')
@login_required
def logout():
    return Userausloggen()

@app.route('/game_löschen/<int:game_id>', methods=['POST'])
@login_required
def game_löschen(game_id):
    return steuerung.game_löschen(game_id)

# Auth Resource
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

auth_ns.add_resource(Register, '/register')
auth_ns.add_resource(Login, '/login')

api.add_namespace(auth_ns)

# Additional Namespaces and Resources
user_ns = Namespace('user', description='User operations')
game_ns = Namespace('game', description='Game operations')

# Models for serialization
user_model = api.model('User', {
    'id': fields.Integer(description='The user unique identifier'),
    'username': fields.String(required=True, description='The user username'),
    'email': fields.String(required=True, description='The user email address')
})

game_model = api.model('Game', {
    'id': fields.Integer(description='The game unique identifier'),
    'name': fields.String(required=True, description='The game name'),
    'preis': fields.Float(required=True, description='The game price')
})

# User Info Resource
@user_ns.route('/<int:user_id>')
class UserInfo(Resource):
    @api.marshal_with(user_model)
    def get(self, user_id):
        user = load_user(user_id)
        if user:
            return {'id': user.id, 'username': user.username, 'email': user.email}
        api.abort(404, "User not found")

# Game Info Resource
@game_ns.route('/<int:game_id>')
class GameInfo(Resource):
    @api.marshal_with(game_model)
    def get(self, game_id):
        game = steuerung.get_game(game_id)
        if game:
            return {'id': game.id, 'name': game.name, 'preis': game.preis}
        api.abort(404, "Game not found")

api.add_namespace(user_ns, path='/user')
api.add_namespace(game_ns, path='/game')

if __name__ == '__main__':
    initialize_db()
    app.run(host='0.0.0.0', port=5000, debug=True)