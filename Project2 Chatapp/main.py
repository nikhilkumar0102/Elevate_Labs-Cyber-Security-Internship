import os
import random
import logging
from datetime import datetime
from typing import Dict

from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    DEBUG = os.environ.get('FLASK_DEBUG', "false").lower() in ('true', '1', 't')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')  # Which domains can connect to us

    # Chat rooms
    CHAT_ROOMS = [
        "General",
        "Technology",
        "Random",
        "Sports",
        "Music"
    ]

app = Flask(__name__)
app.config.from_object(Config)

# Handle reverse proxy setups
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

# Setup socketio
socketio = SocketIO(
    app,
    cors_allowed_origins=app.config['CORS_ORIGINS'],
    logger=True,
    engineio_logger=True,
)

# Database/Dictionary to store users in memory
active_users: Dict[str, dict] = {}  # sid -> user info

# Username generator
def generate_guest_username() -> str:
    timestamp = datetime.now().strftime("%H%M%S")
    return f"Guest{timestamp}{random.randint(100, 999)}"

# Home route
@app.route("/")
def index():
    if "username" not in session:
        session['username'] = generate_guest_username()
        logger.info(f"Generated new username: {session['username']}")

    return render_template(
        "index.html",
        username=session['username'],
        chat_rooms=app.config['CHAT_ROOMS']
    )

# Handle connection
@socketio.on('connect')
def handle_connect():
    try:
        if 'username' not in session:
            session['username'] = generate_guest_username()

        active_users[request.sid] = {
            'username': session['username'],
            'connected_at': datetime.now().isoformat(),
            'room': None
        }

        # Broadcast the new users
        emit('active_users', {
            'users': [user['username'] for user in active_users.values()]
        }, broadcast=True)

        logger.info(f"User connected: {session['username']} with SID: {request.sid}")

    except Exception as e:
        logger.error(f"Error during connection: {e}")
        return False

# Handle disconnection
@socketio.on('disconnect')
def handle_disconnect():
    try:
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

    except Exception as e:
        logger.error(f"Error during disconnection: {e}")

# Join room
@socketio.on('join_room')
def on_join(data: dict):
    try:
        username = session['username']
        room = data.get('room')

        if room not in app.config['CHAT_ROOMS']:
            logger.warning(f"Room {room} does not exist.")
            return

        join_room(room)
        active_users[request.sid]['room'] = room

        emit('status', {
            'msg': f"{username} has entered the room {room}.",
            'type': "join",
            'timestamp': datetime.now().isoformat()
        }, room=room)

        logger.info(f"User {username} has joined room: {room}")

    except Exception as e:
        logger.error(f"Error during joining room: {e}")

# Leave room
@socketio.on('leave_room')
def on_leave(data: dict):
    try:
        username = session['username']
        room = data.get('room')

        if room not in app.config['CHAT_ROOMS']:
            logger.warning(f"Room {room} does not exist.")
            return

        leave_room(room)
        if request.sid in active_users:
            active_users[request.sid]['room'] = None

        emit('status', {
            'msg': f"{username} has left the room {room}.",
            'type': "leave",
            'timestamp': datetime.now().isoformat()
        }, room=room)

        logger.info(f"User {username} has left room: {room}")

    except Exception as e:
        logger.error(f"Error during leaving room: {e}")

# Handle messages
@socketio.on('message')
def handle_message(data: dict):
    try:
        username = session['username']
        room = data.get('room', 'General')
        msg_type = data.get('type', 'message')
        message = data.get('msg', "").strip()

        if not message:
            logger.warning("Empty message received.")
            return

        if room not in app.config['CHAT_ROOMS']:
            logger.warning(f"Room {room} does not exist.")
            return

        timestamp = datetime.now().isoformat()

        if msg_type == 'private':
            target_user = data.get('target')
            if not target_user:
                logger.warning("Private message without target user.")
                return

            for sid, user_data in active_users.items():
                if user_data['username'] == target_user:
                    emit('message', {
                        'msg': message,
                        'from': username,
                        'to': target_user,
                        'timestamp': timestamp
                    }, to=sid)
                    # Also send to the sender for confirmation
                    emit('message', {
                        'msg': message,
                        'from': username,
                        'to': target_user,
                        'timestamp': timestamp
                    }, to=request.sid)
                    return
            logger.warning(f"Target user {target_user} not found for private message.")
        else:
            emit('message', {
                'msg': message,
                'username': username,
                'room': room,
                'timestamp': timestamp
            }, room=room)

    except Exception as e:
        logger.error(f"Error during handling message: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=app.config['DEBUG'],
        use_reloader=app.config['DEBUG']
    )