import socket
import threading
import json
import hashlib
import sqlite3
import base64
import os
from datetime import datetime
from cryptography.fernet import Fernet
import uuid

class ChatServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.clients = {}
        self.rooms = {'general': []}
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for users and messages"""
        self.conn = sqlite3.connect('chat_app.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create messages table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create rooms table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        password_hash = self.hash_password(password)
        self.cursor.execute(
            "SELECT username FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        return self.cursor.fetchone() is not None
        
    def register_user(self, username, password, email=""):
        """Register a new user"""
        try:
            password_hash = self.hash_password(password)
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
            
    def save_message(self, room, username, message, message_type='text'):
        """Save message to database"""
        self.cursor.execute(
            "INSERT INTO messages (room, username, message, message_type) VALUES (?, ?, ?, ?)",
            (room, username, message, message_type)
        )
        self.conn.commit()
        
    def get_message_history(self, room, limit=50):
        """Get message history for a room"""
        self.cursor.execute(
            "SELECT username, message, message_type, timestamp FROM messages WHERE room = ? ORDER BY timestamp DESC LIMIT ?",
            (room, limit)
        )
        messages = self.cursor.fetchall()
        return list(reversed(messages))
        
    def create_room(self, room_name, created_by):
        """Create a new chat room"""
        try:
            self.cursor.execute(
                "INSERT INTO rooms (name, created_by) VALUES (?, ?)",
                (room_name, created_by)
            )
            self.conn.commit()
            self.rooms[room_name] = []
            return True
        except sqlite3.IntegrityError:
            return False
            
    def get_rooms(self):
        """Get list of available rooms"""
        self.cursor.execute("SELECT name FROM rooms")
        rooms = [row[0] for row in self.cursor.fetchall()]
        if 'general' not in rooms:
            rooms.insert(0, 'general')
        return rooms
        
    def encrypt_message(self, message):
        """Encrypt message"""
        return base64.b64encode(self.cipher.encrypt(message.encode())).decode()
        
    def decrypt_message(self, encrypted_message):
        """Decrypt message"""
        try:
            return self.cipher.decrypt(base64.b64decode(encrypted_message.encode())).decode()
        except:
            return encrypted_message
            
    def broadcast_to_room(self, room, message, sender_client=None):
        """Broadcast message to all clients in a room"""
        if room in self.rooms:
            encrypted_msg = self.encrypt_message(json.dumps(message))
            for client in self.rooms[room]:
                if client != sender_client:
                    try:
                        client.send(encrypted_msg.encode())
                    except:
                        self.rooms[room].remove(client)
                        
    def handle_client(self, client_socket, address):
        """Handle individual client connection"""
        username = None
        current_room = None
        
        try:
            while True:
                encrypted_data = client_socket.recv(1024).decode()
                if not encrypted_data:
                    break
                    
                try:
                    data = json.loads(self.decrypt_message(encrypted_data))
                except:
                    continue
                    
                if data['type'] == 'auth':
                    if data['action'] == 'login':
                        if self.authenticate_user(data['username'], data['password']):
                            username = data['username']
                            self.clients[client_socket] = username
                            response = {'type': 'auth_result', 'success': True, 'username': username}
                            encrypted_response = self.encrypt_message(json.dumps(response))
                            client_socket.send(encrypted_response.encode())
                        else:
                            response = {'type': 'auth_result', 'success': False, 'error': 'Invalid credentials'}
                            encrypted_response = self.encrypt_message(json.dumps(response))
                            client_socket.send(encrypted_response.encode())
                            
                    elif data['action'] == 'register':
                        if self.register_user(data['username'], data['password'], data.get('email', '')):
                            response = {'type': 'register_result', 'success': True}
                            encrypted_response = self.encrypt_message(json.dumps(response))
                            client_socket.send(encrypted_response.encode())
                        else:
                            response = {'type': 'register_result', 'success': False, 'error': 'Username already exists'}
                            encrypted_response = self.encrypt_message(json.dumps(response))
                            client_socket.send(encrypted_response.encode())
                            
                elif data['type'] == 'join_room' and username:
                    room = data['room']
                    if current_room and current_room in self.rooms:
                        self.rooms[current_room].remove(client_socket)
                    
                    if room not in self.rooms:
                        self.rooms[room] = []
                    
                    self.rooms[room].append(client_socket)
                    current_room = room
                    
                    # Send room info and history
                    history = self.get_message_history(room)
                    response = {
                        'type': 'room_joined',
                        'room': room,
                        'history': history,
                        'users': [self.clients.get(c, 'Unknown') for c in self.rooms[room]]
                    }
                    encrypted_response = self.encrypt_message(json.dumps(response))
                    client_socket.send(encrypted_response.encode())
                    
                    # Notify others
                    join_msg = {
                        'type': 'user_joined',
                        'username': username,
                        'room': room,
                        'timestamp': datetime.now().isoformat()
                    }
                    self.broadcast_to_room(room, join_msg, client_socket)
                    
                elif data['type'] == 'message' and username and current_room:
                    message_data = {
                        'type': 'message',
                        'username': username,
                        'message': data['message'],
                        'message_type': data.get('message_type', 'text'),
                        'room': current_room,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Save to database
                    self.save_message(current_room, username, data['message'], data.get('message_type', 'text'))
                    
                    # Broadcast to room
                    self.broadcast_to_room(current_room, message_data, client_socket)
                    
                elif data['type'] == 'get_rooms' and username:
                    rooms = self.get_rooms()
                    response = {'type': 'rooms_list', 'rooms': rooms}
                    encrypted_response = self.encrypt_message(json.dumps(response))
                    client_socket.send(encrypted_response.encode())
                    
                elif data['type'] == 'create_room' and username:
                    room_name = data['room_name']
                    if self.create_room(room_name, username):
                        response = {'type': 'room_created', 'success': True, 'room': room_name}
                    else:
                        response = {'type': 'room_created', 'success': False, 'error': 'Room already exists'}
                    encrypted_response = self.encrypt_message(json.dumps(response))
                    client_socket.send(encrypted_response.encode())
                    
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            if client_socket in self.clients:
                del self.clients[client_socket]
            if current_room and current_room in self.rooms and client_socket in self.rooms[current_room]:
                self.rooms[current_room].remove(client_socket)
                # Notify others about user leaving
                if username:
                    leave_msg = {
                        'type': 'user_left',
                        'username': username,
                        'room': current_room,
                        'timestamp': datetime.now().isoformat()
                    }
                    self.broadcast_to_room(current_room, leave_msg)
            client_socket.close()
            
    def start_server(self):
        """Start the chat server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"Chat server started on {self.host}:{self.port}")
        print(f"Encryption key: {self.encryption_key.decode()}")
        
        try:
            while True:
                client_socket, address = server_socket.accept()
                print(f"New connection from {address}")
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            server_socket.close()
            self.conn.close()

if __name__ == "__main__":
    server = ChatServer()
    server.start_server()