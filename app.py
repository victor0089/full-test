from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_images import Images
from flask_rq2 import RQ
from flask_socketio import SocketIO, Namespace, emit
from flask_geoip2 import GeoIP2
from flask_babelex import Babel
from flask_dance.contrib.google import make_google_blueprint, google
from flask_restful_swagger_2 import Api as SwaggerApi, swagger
from flask_jsglue import JSGlue
from flask_dance.contrib.oauthlib import make_oauthlib_blueprint, oauth
from flask_principals import Principal, Permission, RoleNeed

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'your_upload_folder'

# Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
limiter = Limiter(app, key_func=get_remote_address)
images = Images(app)
rq = RQ(app)
socketio = SocketIO(app)
geoip = GeoIP2(app)
babel = Babel(app)
jsglue = JSGlue(app)
principals = Principal(app)

# CORS
CORS(app)

# Define User and Role models for Flask-Security
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary='user_roles')

# Define the many-to-many relationship for Flask-Security
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Flask-Restful API
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/api/hello')

# Flask-Restful-Swagger API documentation
swagger_api = SwaggerApi(app)
swagger_api.add_resource(HelloWorld, '/api/hello')

# Flask-SocketIO Namespace
class ChatNamespace(Namespace):
    def on_connect(self):
        print('Client connected to chat namespace')

    def on_disconnect(self):
        print('Client disconnected from chat namespace')

    def on_message(self, data):
        print('Received message:', data)
        emit('message', {'data': data}, broadcast=True)

socketio.on_namespace('/chat', ChatNamespace)

# Flask-Limiter rate-limited route
@app.route('/api/limited')
@limiter.limit("5 per minute")
def limited_route():
    return jsonify({'message': 'This route is rate-limited'})

# Flask-Images image resizing route
@app.route('/resize_image/<path:filename>')
def resize_image(filename):
    return images.send_from_directory(app.config['UPLOAD_FOLDER'], filename, resize=(100, 100))

# Flask-JWT-Extended JWT authentication routes
@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if username and password:
        # Validate user credentials (replace with your authentication logic)
        if valid_user_credentials(username, password):
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Flask-GeoIP2 user location route
@app.route('/user_location')
def user_location():
    user_ip = request.remote_addr
    user_location = geoip.city(user_ip)
    return jsonify({'location': user_location})

# Flask-Dance-OAuthlib OAuthlib login route
@app.route('/oauthlib_login')
def oauthlib_login():
    if not oauth.oauthlib.authorized:
        return redirect(url_for('oauthlib.login'))

    resp = oauth.oauthlib.get('user')
    assert resp.ok, resp.text
    return 'Logged in as: ' + resp.json()['username']

if __name__ == '__main__':
    socketio.run(app)
