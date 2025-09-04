let socket = io();
let currentRoom = 'General';
let username = document.querySelector('h2')?.textContent.replace('Welcome, ', '').replace('!', '').trim() || 
               sessionStorage.getItem('display_name');
let roomMessages = {};
let isConnected = false;
let userColors = {}; // Store random colors for each user

// Generate a random visible color
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color;
    do {
        color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
    } while (calculateContrast(color, '#000000') < 4.5); // Ensure sufficient contrast
    return color;
}

// Calculate contrast ratio for text visibility
function calculateContrast(color1, color2) {
    const lum1 = getLuminance(color1);
    const lum2 = getLuminance(color2);
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);
    return (brightest + 0.05) / (darkest + 0.05);
}

function getLuminance(color) {
    const rgb = parseInt(color.slice(1), 16);
    const r = (rgb >> 16) & 255;
    const g = (rgb >> 8) & 255;
    const b = rgb & 255;
    const a = [r, g, b].map(c => c / 255).map(c => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)));
    return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
}

// ==================== SOCKET EVENT LISTENERS ====================

// Handle successful connection to server
socket.on('connect', () => {
    console.log('Connected to server');
    isConnected = true;
    updateConnectionStatus('Connected', false);

    // Assign a random color to the current user
    if (!userColors[username]) {
        userColors[username] = getRandomColor();
    }

    // Join the default room
    joinRoom('General');
    highlightActiveRoom('General');

    // Request initial user list
    socket.emit('active_users_request');
});

// Handle disconnection from server
socket.on('disconnect', () => {
    console.log('Disconnected from server');
    isConnected = false;
    updateConnectionStatus('Disconnected', true);
});

// Handle connection errors
socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    updateConnectionStatus('Connection Error', true);
});

// Handle incoming messages
socket.on('message', (data) => {
    console.log('Received message:', data);

    // Only display if in current room or private message to current user
    if (data.room === currentRoom || (data.type === 'private' && data.target === username)) {
        // Assign a random color to the sender if not already set
        if (!userColors[data.username]) {
            userColors[data.username] = getRandomColor();
        }
        // Check if message contains an image URL
        if (data.msg.includes('File uploaded by')) {
            addMessageWithImage(data.username, data.msg, data.username === username ? 'sent' : 'received', userColors[data.username]);
        } else {
            addMessage(data.username, data.msg, data.username === username ? 'sent' : 'received', userColors[data.username]);
        }
    }
});

// Handle private messages
socket.on('private_message', (data) => {
    console.log('Received private message:', data);
    if (!userColors[data.from]) {
        userColors[data.from] = getRandomColor();
    }
    addMessage(data.from, `[Private] ${data.msg}`, 'private', userColors[data.from]);
});

// Handle system status messages
socket.on('status', (data) => {
    console.log('Status message:', data);
    addMessage('System', data.msg, 'system');

    // Notify when a user joins the room
    if (data.msg.includes('has entered the room') && 
        'Notification' in window && 
        Notification.permission === 'granted') {
        new Notification('User Joined', {
            body: data.msg,
            icon: '/static/favicon.ico'
        });
    }

    // Show popup for user joined (only for the General room default join)
    if (data.msg.includes('has entered the room') && currentRoom === 'General' && data.msg.includes(username)) {
        alert(`You have joined the ${currentRoom} room!`);
    }
});

// Handle active users list updates
socket.on('active_users', (data) => {
    console.log('Active users update:', data);
    const userList = document.getElementById('active-users');

    if (userList && data.users) {
        userList.innerHTML = data.users
            .map(user => {
                if (!userColors[user]) {
                    userColors[user] = getRandomColor();
                }
                return `
                    <div class="user-item" onclick="insertPrivateMessage('${sanitize(user)}')" style="color: ${userColors[user]}">
                        ${sanitize(user)} ${user === username ? '(you)' : ''}
                    </div>
                `;
            })
            .join('');
    }
});

// ==================== CONNECTION STATUS ====================

/**
 * Update connection status display
 * @param {string} status - Status text to display
 * @param {boolean} isError - Whether this is an error state
 */
function updateConnectionStatus(status, isError) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        statusElement.textContent = status;
        statusElement.className = 'connection-status' + (isError ? ' disconnected' : '');
    }
}

// ==================== UTILITY FUNCTIONS ====================

/**
 * Sanitize text to prevent XSS attacks
 * @param {string} text - Text to sanitize
 * @returns {string} Sanitized text
 */
function sanitize(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== MESSAGE HANDLING ====================

/**
 * Add a message to the chat display
 * @param {string} sender - Username of the sender
 * @param {string} message - Message content
 * @param {string} type - Message type ('sent', 'received', 'system', 'private')
 * @param {string} color - Color for the message (optional)
 */
function addMessage(sender, message, type, color = '#000000') {
    // Initialize room messages array if it doesn't exist
    if (!roomMessages[currentRoom]) {
        roomMessages[currentRoom] = [];
    }

    // Create message object with timestamp
    const messageObj = {
        sender,
        message,
        type,
        timestamp: new Date().toISOString(),
        color // Store color with message
    };

    // Store message for room history
    roomMessages[currentRoom].push(messageObj);

    const chat = document.getElementById('chat');
    if (!chat) return;

    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        <strong style="color: ${color}">${sanitize(sender)}:</strong> ${sanitize(message)}
        <br>
        <small>${new Date().toLocaleTimeString()}</small>
    `;

    // Add to chat and scroll to bottom
    chat.appendChild(messageDiv);
    chat.scrollTop = chat.scrollHeight;

    // Notify for private messages
    if (type === 'private' && 
        'Notification' in window && 
        Notification.permission === 'granted') {
        new Notification(`Private from ${sender}`, {
            body: message,
            icon: '/static/favicon.ico'
        });
    }
}

/**
 * Add a message with an image to the chat display
 * @param {string} sender - Username of the sender
 * @param {string} message - Message content including image URL
 * @param {string} type - Message type ('sent', 'received', 'system', 'private')
 * @param {string} color - Color for the message (optional)
 */
function addMessageWithImage(sender, message, type, color = '#000000') {
    if (!roomMessages[currentRoom]) {
        roomMessages[currentRoom] = [];
    }

    const messageObj = {
        sender,
        message,
        type,
        timestamp: new Date().toISOString(),
        color
    };

    roomMessages[currentRoom].push(messageObj);

    const chat = document.getElementById('chat');
    if (!chat) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    // Extract URL from message (assuming format "File uploaded by [username]: [url]")
    const urlMatch = message.match(/https?:\/\/[^\s]+/);
    const url = urlMatch ? urlMatch[0] : '';
    messageDiv.innerHTML = `
        <strong style="color: ${color}">${sanitize(sender)}:</strong>
        ${url ? 
            `<img src="${sanitize(url)}" alt="Uploaded image" style="max-width: 100%; max-height: 200px; border-radius: 0.5rem; margin-top: 0.5rem;">` : 
            sanitize(message)}
        <br>
        <small>${new Date().toLocaleTimeString()}</small>
    `;

    chat.appendChild(messageDiv);
    chat.scrollTop = chat.scrollHeight;

    if (type === 'private' && 'Notification' in window && Notification.permission === 'granted') {
        new Notification(`Private from ${sender}`, {
            body: message,
            icon: '/static/favicon.ico'
        });
    }
}

/**
 * Send a message to the server
 */
function sendMessage() {
    const input = document.getElementById('message');
    if (!input) return;

    const message = input.value.trim();
    if (!message) return;

    if (!isConnected) {
        addMessage('System', 'Not connected to server. Please refresh the page.', 'system');
        return;
    }

    if (message.startsWith('@')) {
        const [target, ...msgParts] = message.substring(1).split(' ');
        const privateMsg = msgParts.join(' ');

        if (target.trim() === username) {
            addMessage('System', 'You cannot send a private message to yourself.', 'system');
            input.value = '';
            input.focus();
            return;
        }

        if (privateMsg.trim()) {
            socket.emit('message', {
                msg: privateMsg,
                type: 'private',
                target: target,
                room: currentRoom
            });
            addMessage(username, `[Private to ${target}] ${privateMsg}`, 'private', userColors[username]);
        }
    } else {
        socket.emit('message', {
            msg: message,
            room: currentRoom
        });
    }

    input.value = '';
    input.focus();
}

/**
 * Upload a file to the server
 */
function uploadFile() {
    const fileInput = document.getElementById('file-upload');
    if (!fileInput || !fileInput.files[0]) return;

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
    if (csrfToken) {
        formData.append('csrf_token', csrfToken);
    }

    fetch('/upload', {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.url) {
            const fileMessage = `File uploaded by ${username}: ${data.url}`;
            socket.emit('message', {
                msg: fileMessage,
                room: currentRoom
            });
        } else {
            addMessage('System', data.error || 'Upload failed', 'system');
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        addMessage('System', 'Upload failed', 'system');
    });

    fileInput.value = '';
}

// ==================== ROOM MANAGEMENT ====================

/**
 * Join a chat room
 * @param {string} room - Room name to join
 */
function joinRoom(room) {
    if (!room || room === currentRoom) return;

    console.log(`Attempting to join room: ${room}`);

    if (currentRoom) {
        socket.emit('leave', { room: currentRoom });
    }

    const previousRoom = currentRoom;
    currentRoom = room;

    socket.emit('join', { room: currentRoom });

    highlightActiveRoom(currentRoom);

    const chat = document.getElementById('chat');
    if (chat) {
        chat.innerHTML = '';

        if (roomMessages[currentRoom]) {
            roomMessages[currentRoom].forEach((msg) => {
                if (msg.message.includes('File uploaded by')) {
                    addMessageWithImage(msg.sender, msg.message, msg.type, msg.color);
                } else {
                    addMessage(msg.sender, msg.message, msg.type, msg.color);
                }
            });
        }
    }

    console.log(`Joined room: ${room}`);
}

// ==================== USER INTERACTION ====================

/**
 * Insert a username into the message input for private messaging
 * @param {string} user - Username to message
 */
function insertPrivateMessage(user) {
    const messageInput = document.getElementById('message');
    if (messageInput) {
        messageInput.value = `@${sanitize(user)} `;
        messageInput.focus();
    }
}

/**
 * Handle Enter key press in message input
 * @param {Event} event - Key press event
 */
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    } else if (event.key === 'Enter' && event.shiftKey) {
        const input = document.getElementById('message');
        const start = input.selectionStart;
        const end = input.selectionEnd;
        input.value = input.value.substring(0, start) + '\n' + input.value.substring(end);
        input.selectionStart = input.selectionEnd = start + 1;
        event.preventDefault();
    }
}

/**
 * Highlight the active room in the room list
 * @param {string} room - Room name to highlight
 */
function highlightActiveRoom(room) {
    document.querySelectorAll('.room-item').forEach((item) => {
        item.classList.remove('active-room');
        if (item.textContent.trim() === room) {
            item.classList.add('active-room');
        }
    });
}

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing chat...');

    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }

    const fileUpload = document.getElementById('file-upload');
    if (fileUpload) {
        fileUpload.addEventListener('change', uploadFile);
    }

    const messageInput = document.getElementById('message');
    if (messageInput) {
        messageInput.focus();
    }

    console.log('Chat initialized');
});
