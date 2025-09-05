# Chat Application

A real-time chat application built with Flask, SocketIO, and JavaScript, featuring public and private messaging, room-based chat, and file uploads.

## Features

- Real-time public and private messaging.
- Multiple chat rooms (General, Technology, Random, Sports, Music).
- User registration and login with session management.
- File upload support (images, audio). (Work going on)
- Active user list with private message targeting. (E2E Encryption)
- Basic styling with color-coded usernames.

### Download

To download this project, follow these steps:

Via ZIP Download:
```
- Visit the repository page at https://github.com/yourusername/chat-application.
- Click the green "Code" button and select "Download ZIP".
- Extract the ZIP file to your desired location.
```

*Requirements*:
`Ensure you have Git installed if using the clone method (git --version to check)`.

### Prerequisites

```Python 3.8+
Flask
Flask-SocketIO
Flask-SQLAlchemy
Flask-Limiter
Werkzeug
Bleach
Node.js (for client-side JavaScript)
```
---

### Installation

```
1. Create a virtual environment and activate it:
2. python -m venv venv
3. source venv/bin/activate  # On Windows: venv\Scripts\activate
4. Install the required Python packages:
5. pip install -r requirements.txt

(Note: Create a requirements.txt file with the necessary dependencies like flask, flask-socketio, etc., based on the imports in main.py.)
```

### Set up the database:

- Ensure a chat.db file is created automatically when the app runs with the initial context.
- Run the application (see Usage section).

### Usage

*Start the server*:
```python main.py```

#### Open a web browser and navigate to http://localhost:5000.
```
- Register a new user or log in with existing credentials.
- Choose a nickname to start chatting.
```

#### Use the interface to:
```
- Join different chat rooms.
- Send public messages or private messages (e.g., @username message).
- Upload files using the file input.
```
---

### Screenshots

1. Login Page

Description: Shows the login form with username and password fields, including the error message area.

2. Registration Page

Description: Displays the registration form with username, password, and confirm password fields, plus a success or error message.

3. Chat Interface

Description: Depicts the main chat window with the room list, active users, message input, and a sample public message.

4. Private Messaging

Description: Shows a private message exchange, e.g., one user sending @otheruser hello with the sender seeing [Private to otheruser] hello and the recipient seeing [otheruser: [Private] hello].
