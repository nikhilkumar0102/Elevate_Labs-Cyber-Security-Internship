import os
import logging
from datetime import datetime
from typing import Dict

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Logging configuration (remains the same)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Config class (remains the same)
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    DEBUG = os.environ.get('FLASK_DEBUG', "false").lower() in ('true', '1', 't')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chat.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CHAT_ROOMS = ["General", "Technology", "Random", "Sports", "Music"]

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
socketio = SocketIO(
    app,
    cors_allowed_origins=app.config['CORS_ORIGINS'],
    logger=True,
    engineio_logger=True,
)

# User Model (remains the same)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    def __repr__(self):
        return f'<User {self.username}>'

active_users: Dict[str, dict] = {}

# Registration Route (remains the same)
@app.route("/register", methods=['GET', 'POST'])
def register():
    logger.info("Entering register route")
    with app.app_context():
        logger.info("Creating database tables")
        db.create_all()
    if request.method == 'POST':
        logger.info("Processing POST request")
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Username and password are required.')
            return redirect(url_for('register'))
        if len(username) > 80:
            flash('Username must be 80 characters or less.')
            return redirect(url_for('register'))
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username is already taken. Please choose another.')
            return redirect(url_for('register'))
        logger.info("Creating new user")
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            logger.info("User created successfully")
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash(f'Registration failed: {str(e)}')
            return redirect(url_for('register'))
    logger.info("Rendering register.html")
    return render_template("register.html")

# === UPDATED: Login Route ===
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please enter username and password.')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            # Store the permanent account username in the session
            session['account_username'] = user.username
            logger.info(f"Account {username} logged in.")
            # Redirect to the nickname selection page instead of the chat
            return redirect(url_for('choose_nickname'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))
    return render_template("login.html")

# === NEW: Routes for Nickname Selection ===
@app.route("/choose-nickname", methods=['GET'])
def choose_nickname():
    # Make sure user has logged into their account first
    if "account_username" not in session:
        return redirect(url_for('login'))
    return render_template("choose_nickname.html", account_username=session['account_username'])

@app.route("/set-nickname", methods=['POST'])
def set_nickname():
    # Make sure user has logged into their account first
    if "account_username" not in session:
        return redirect(url_for('login'))
    
    nickname = request.form.get('nickname')
    if nickname and nickname.strip():
        # Store the chosen display name for the session
        session['display_name'] = nickname.strip()
        return redirect(url_for('index'))
    else:
        # If they submit an empty nickname, send them back
        return redirect(url_for('choose_nickname'))

# === UPDATED: Home/Index Route ===
@app.route("/")
def index():
    # A user must have a display_name to enter the chat.
    # This implicitly checks they've logged in and chosen a name.
    if "display_name" not in session:
        return redirect(url_for('login'))

    return render_template(
        "index.html",
        # Pass the display_name to the template
        username=session['display_name'],
        rooms=app.config['CHAT_ROOMS']
    )

@socketio.on('connect')
def handle_connect():
    if 'display_name' not in session:
        return False # Reject connection

    username = session['display_name']
    active_users[request.sid] = {
        'username': username,
        'connected_at': datetime.now().isoformat(),
        'room': None
    }
    emit('active_users', {
        'users': [user['username'] for user in active_users.values()]
    }, broadcast=True)
    logger.info(f"User connected: {username} with SID: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_users:
        username = active_users[request.sid]['username']
        
        room = active_users[request.sid].get('room')
        del active_users[request.sid]
        emit('active_users', {
            'users': [user['username'] for user in active_users.values()]
        }, broadcast=True)
        if room:
            emit('status', {
                'msg': f"{username} has disconnected.",
                'type': "leave",
                'timestamp': datetime.now().isoformat()
            }, room=room)
        logger.info(f"User disconnected: {username} with SID: {request.sid}")


@socketio.on('join')
def on_join(data: dict):
  
    username = session['display_name']
 
    room = data.get('room')
    if not room or room not in app.config['CHAT_ROOMS']:
        return
    join_room(room)
    active_users[request.sid]['room'] = room
    emit('status', {
        'msg': f"{username} has entered the room.",
        'type': "join",
        'timestamp': datetime.now().isoformat()
    }, room=room)
    logger.info(f"User {username} joined room: {room}")


@socketio.on('leave')
def on_leave(data: dict):
  
    username = session['display_name']
    room = data.get('room')
    if not room or room not in app.config['CHAT_ROOMS']:
        return
    leave_room(room)
    if request.sid in active_users:
        active_users[request.sid]['room'] = None
    emit('status', {
        'msg': f"{username} has left the room.",
        'type': "leave",
        'timestamp': datetime.now().isoformat()
    }, room=room)
    logger.info(f"User {username} left room: {room}")

@socketio.on('message')
def handle_message(data: dict):
    
    username = session['display_name']
    msg_type = data.get('type')
    message = data.get('msg', "").strip()
    if not message:
        return
    timestamp = datetime.now().isoformat()
    if msg_type == 'private':
        target_user = data.get('target')
        target_sid = None
        for sid, user_data in active_users.items():
            if user_data['username'] == target_user:
                target_sid = sid
                break
        if target_sid:
            emit('private_message', {'msg': message, 'from': username, 'timestamp': timestamp}, to=target_sid)
            emit('private_message', {'msg': f"To {target_user}: {message}", 'from': 'Me', 'timestamp': timestamp}, to=request.sid)
        else:
             emit('status', {'msg': f"User '{target_user}' not found or is offline.", 'type': "error"}, to=request.sid)
    else:
        room = data.get('room', 'General')
        if room not in app.config['CHAT_ROOMS']:
            return
        emit('message', {'msg': message, 'username': username, 'room': room, 'timestamp': timestamp}, room=room)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=app.config['DEBUG'],
        use_reloader=app.config['DEBUG']
    )
