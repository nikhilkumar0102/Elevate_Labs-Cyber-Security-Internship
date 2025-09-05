import os
import logging
from datetime import datetime, timedelta
from typing import Dict
import bleach
import socket
from flask import Flask, render_template, request, session, redirect, url_for, flash, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf, CSRFError

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Config class
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    DEBUG = os.environ.get('FLASK_DEBUG', "false").lower() in ('true', '1', 't')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chat.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CHAT_ROOMS = ["General", "Technology", "Random", "Sports", "Music"]
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'ogg'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB file size limit
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # Session timeout
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'

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
csrf = CSRFProtect(app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
limiter.init_app(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    def __repr__(self):
        return f'<User {self.username}>'

active_users: Dict[str, dict] = {}
user_public_keys: Dict[str, str] = {}  # Store public keys {username: publicKeyBase64}

# Helper function to check allowed files
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Find an available port
def find_available_port(host, start_port, max_attempts=10):
    port = start_port
    for _ in range(max_attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((host, port))
            sock.close()
            logger.info(f"Port {port} is available")
            return port
        except OSError:
            logger.warning(f"Port {port} is in use, trying next port")
            port += 1
        finally:
            sock.close()
    raise OSError(f"No available ports found between {start_port} and {start_port + max_attempts - 1}")

# Registration Route
@app.route("/register", methods=['GET', 'POST'])
@limiter.limit("10 per hour")  # Limit registration attempts
def register():
    logger.info("Entering register route")
    if request.method == 'POST':
        logger.info("Processing POST request")
        logger.debug(f"Register form data: {request.form}")
        try:
            validate_csrf(request.form.get('csrf_token'))
        except CSRFError:
            logger.error("CSRF token validation failed for register")
            flash('Invalid CSRF token.')
            return redirect(url_for('register'))
        
        username = bleach.clean(request.form.get('username', ''), tags=[], strip=True)
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not password or not confirm_password:
            flash('All fields are required.')
            return redirect(url_for('register'))
        
        if len(username) < 3 or len(username) > 80:
            flash('Username must be 3-80 characters.')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.')
            return redirect(url_for('register'))
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username is already taken. Please choose another.')
            return redirect(url_for('register'))
        
        logger.info("Creating new user")
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256')
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
            flash('Registration failed. Please try again.')
            return redirect(url_for('register'))
    
    return render_template('register.html', csrf_token=generate_csrf())

# Login Route
@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Limit login attempts to 5 per minute per IP
def login():
    error_message = None
    if request.method == 'POST':
        logger.info("Processing login POST request")
        logger.debug(f"Login form data: {request.form}")
        
        try:
            validate_csrf(request.form.get('csrf_token'))
        except CSRFError:
            logger.error("CSRF token validation failed for login")
            error_message = 'Invalid CSRF token. Please try again.'
            return render_template("login.html", csrf_token=generate_csrf(), error_message=error_message)

        username = bleach.clean(request.form.get('username', ''), tags=[], strip=True)
        password = request.form.get('password', '')
        if not username or not password:
            error_message = 'Please enter username and password.'
        else:
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['account_username'] = user.username
                session.permanent = True  # Enable session timeout
                logger.info(f"Account {username} logged in.")
                return redirect(url_for('choose_nickname'))
            else:
                error_message = 'Invalid username or password.'
    logger.info("Rendering login.html")
    return render_template("login.html", csrf_token=generate_csrf(), error_message=error_message)

# Routes for Nickname Selection
@app.route("/choose-nickname", methods=['GET'])
def choose_nickname():
    if "account_username" not in session:
        return redirect(url_for('login'))
    return render_template("choose_nickname.html", account_username=session['account_username'], csrf_token=generate_csrf())

@app.route("/set-nickname", methods=['POST'])
@limiter.limit("10 per hour")
def set_nickname():
    if "account_username" not in session:
        return redirect(url_for('login'))
    logger.debug(f"Set-nickname form data: {request.form}")
    try:
        validate_csrf(request.form.get('csrf_token'))
    except CSRFError:
        logger.error("CSRF token validation failed for set-nickname")
        flash('Invalid CSRF token.')
        return redirect(url_for('choose_nickname'))
    
    nickname = bleach.clean(request.form.get('nickname', ''), tags=[], strip=True)
    if nickname and len(nickname.strip()) >= 3:
        session['display_name'] = nickname.strip()
        return redirect(url_for('index'))
    else:
        flash('Nickname must be at least 3 characters.')
        return redirect(url_for('choose_nickname'))

# Home/Index Route
@app.route("/")
def index():
    if "display_name" not in session:
        return redirect(url_for('login'))
    return render_template(
        "index.html",
        username=session['display_name'],
        rooms=app.config['CHAT_ROOMS'],
        csrf_token=generate_csrf()
    )

# Upload Route
@app.route('/upload', methods=['POST'])
@limiter.limit("5 per minute")  # Limit file uploads
def upload_file():
    if 'display_name' not in session:
        return {'error': 'Unauthorized'}, 401
    logger.debug(f"Upload form data: {request.form}")
    try:
        validate_csrf(request.form.get('csrf_token'))
    except CSRFError:
        logger.error("CSRF token validation failed for upload")
        return {'error': 'Invalid CSRF token'}, 400
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        url = url_for('uploaded_file', filename=filename, _external=True)
        return {'url': url}
    else:
        return {'error': 'File type not allowed'}, 400

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filename = secure_filename(filename)  # Prevent path traversal
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on('connect')
def handle_connect():
    if 'display_name' not in session:
        return False
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
        if username in user_public_keys:
            del user_public_keys[username]  # Clean up public key on disconnect
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
@limiter.limit("10 per minute")  # Limit messages per user
def handle_message(data: dict):
    username = session['display_name']
    msg_type = data.get('type')
    message = bleach.clean(data.get('msg', "").strip(), tags=['p', 'strong', 'em'], attributes={})
    if not message:
        return
    timestamp = datetime.now().isoformat()
    if msg_type == 'private':
        target_user = bleach.clean(data.get('target', ''), tags=[], strip=True)
        target_sid = None
        for sid, user_data in active_users.items():
            if user_data['username'] == target_user:
                target_sid = sid
                break
        if target_sid:
            emit('private_message', {
                'msg': message,
                'from': username,
                'timestamp': timestamp,
                'is_sender': False
            }, to=target_sid)
            emit('private_message', {
                'msg': message,
                'from': 'Me',
                'target': target_user,
                'timestamp': timestamp,
                'is_sender': True
            }, to=request.sid)
        else:
            emit('status', {'msg': f"User '{target_user}' not found or is offline.", 'type': 'error'}, to=request.sid)
    else:
        room = data.get('room', 'General')
        if room not in app.config['CHAT_ROOMS']:
            return
        emit('message', {'msg': message, 'username': username, 'room': room, 'timestamp': timestamp}, room=room)

@socketio.on('share_public_key')
def handle_share_public_key(data):
    username = session['display_name']
    public_key = data.get('publicKey')
    if public_key:
        user_public_keys[username] = public_key
        emit('public_key', {'username': username, 'publicKey': public_key}, broadcast=True)
        logger.info(f"Public key shared for user: {username}")

@socketio.on('request_public_key')
def handle_request_public_key(data):
    target = data.get('target')
    if target and target in user_public_keys:
        emit('public_key', {'username': target, 'publicKey': user_public_keys[target]}, broadcast=True)
        logger.info(f"Public key requested and sent for user: {target}")

@socketio.on('active_users_request')
def handle_active_users_request():
    username = session['display_name']
    emit('active_users', {
        'users': [user['username'] for user in active_users.values()]
    }, broadcast=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    host = "0.0.0.0"
    start_port = int(os.environ.get("PORT", 5000))
    try:
        port = find_available_port(host, start_port)
        logger.info(f"Starting server on port {port}")
        socketio.run(
            app,
            host=host,
            port=port,
            debug=app.config['DEBUG'],
            use_reloader=app.config['DEBUG']
        )
    except OSError as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise
