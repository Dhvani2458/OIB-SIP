import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import socket
import threading
import json
import base64
from datetime import datetime
from cryptography.fernet import Fernet
import os
import mimetypes
from PIL import Image, ImageTk
import pygame
import io

class ChatClient:
    def __init__(self):
        self.socket = None
        self.username = None
        self.current_room = None
        self.connected = False
        self.encryption_key = None
        self.cipher = None
        
        # Initialize pygame for sound notifications
        pygame.mixer.init()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Advanced Chat Application")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Initialize GUI
        self.create_login_window()
        
    def configure_styles(self):
        """Configure custom styles for the application"""
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='white', background='#2c3e50')
        self.style.configure('Custom.TButton', font=('Arial', 10), padding=5)
        self.style.configure('Custom.TEntry', font=('Arial', 10), padding=5)
        self.style.configure('Room.TButton', font=('Arial', 9), padding=3)
        
    def create_login_window(self):
        """Create the login/registration window"""
        self.login_frame = tk.Frame(self.root, bg='#34495e', padx=20, pady=20)
        self.login_frame.pack(expand=True, fill='both')
        
        # Title
        title_label = tk.Label(self.login_frame, text="Advanced Chat Application", 
                             font=('Arial', 24, 'bold'), fg='#ecf0f1', bg='#34495e')
        title_label.pack(pady=(0, 30))
        
        # Connection settings
        conn_frame = tk.Frame(self.login_frame, bg='#34495e')
        conn_frame.pack(pady=10)
        
        tk.Label(conn_frame, text="Server:", font=('Arial', 12), fg='#ecf0f1', bg='#34495e').grid(row=0, column=0, sticky='w', padx=5)
        self.server_entry = tk.Entry(conn_frame, font=('Arial', 12), width=20)
        self.server_entry.insert(0, "localhost")
        self.server_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(conn_frame, text="Port:", font=('Arial', 12), fg='#ecf0f1', bg='#34495e').grid(row=0, column=2, sticky='w', padx=5)
        self.port_entry = tk.Entry(conn_frame, font=('Arial', 12), width=8)
        self.port_entry.insert(0, "12345")
        self.port_entry.grid(row=0, column=3, padx=5)
        
        # Encryption key
        tk.Label(conn_frame, text="Encryption Key:", font=('Arial', 12), fg='#ecf0f1', bg='#34495e').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.key_entry = tk.Entry(conn_frame, font=('Arial', 12), width=40, show='*')
        self.key_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        
        # Login form
        login_form = tk.Frame(self.login_frame, bg='#34495e')
        login_form.pack(pady=20)
        
        tk.Label(login_form, text="Username:", font=('Arial', 12), fg='#ecf0f1', bg='#34495e').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.username_entry = tk.Entry(login_form, font=('Arial', 12), width=25)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(login_form, text="Password:", font=('Arial', 12), fg='#ecf0f1', bg='#34495e').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.password_entry = tk.Entry(login_form, font=('Arial', 12), width=25, show='*')
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(login_form, text="Email (optional):", font=('Arial', 12), fg='#ecf0f1', bg='#34495e').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.email_entry = tk.Entry(login_form, font=('Arial', 12), width=25)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.login_frame, bg='#34495e')
        button_frame.pack(pady=20)
        
        self.login_btn = tk.Button(button_frame, text="Login", font=('Arial', 12), 
                                  bg='#3498db', fg='white', padx=20, pady=5, 
                                  command=self.login)
        self.login_btn.pack(side='left', padx=10)
        
        self.register_btn = tk.Button(button_frame, text="Register", font=('Arial', 12), 
                                     bg='#2ecc71', fg='white', padx=20, pady=5, 
                                     command=self.register)
        self.register_btn.pack(side='left', padx=10)
        
        # Status label
        self.status_label = tk.Label(self.login_frame, text="", font=('Arial', 10), 
                                   fg='#e74c3c', bg='#34495e')
        self.status_label.pack(pady=10)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())
        
    def create_chat_window(self):
        """Create the main chat window"""
        # Clear login frame
        self.login_frame.destroy()
        
        # Create main chat interface
        self.chat_frame = tk.Frame(self.root, bg='#2c3e50')
        self.chat_frame.pack(fill='both', expand=True)
        
        # Top frame for user info and controls
        top_frame = tk.Frame(self.chat_frame, bg='#34495e', height=50)
        top_frame.pack(fill='x', padx=5, pady=5)
        top_frame.pack_propagate(False)
        
        # User info
        user_info = tk.Label(top_frame, text=f"Welcome, {self.username}!", 
                           font=('Arial', 14, 'bold'), fg='#ecf0f1', bg='#34495e')
        user_info.pack(side='left', padx=10, pady=10)
        
        # Disconnect button
        disconnect_btn = tk.Button(top_frame, text="Disconnect", font=('Arial', 10), 
                                 bg='#e74c3c', fg='white', padx=15, pady=5, 
                                 command=self.disconnect)
        disconnect_btn.pack(side='right', padx=10, pady=10)
        
        # Main content frame
        main_frame = tk.Frame(self.chat_frame, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel for rooms
        left_panel = tk.Frame(main_frame, bg='#34495e', width=200)
        left_panel.pack(side='left', fill='y', padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Room controls
        room_header = tk.Label(left_panel, text="Chat Rooms", font=('Arial', 12, 'bold'), 
                             fg='#ecf0f1', bg='#34495e')
        room_header.pack(pady=10)
        
        # Create room button
        create_room_btn = tk.Button(left_panel, text="Create Room", font=('Arial', 10), 
                                  bg='#3498db', fg='white', padx=10, pady=3, 
                                  command=self.create_room_dialog)
        create_room_btn.pack(pady=5)
        
        # Rooms list
        self.rooms_listbox = tk.Listbox(left_panel, font=('Arial', 10), bg='#ecf0f1', 
                                       selectbackground='#3498db', height=15)
        self.rooms_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        self.rooms_listbox.bind('<Double-Button-1>', self.join_room)
        
        # Right panel for chat
        right_panel = tk.Frame(main_frame, bg='#34495e')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Chat header
        self.chat_header = tk.Label(right_panel, text="Select a room to start chatting", 
                                  font=('Arial', 14, 'bold'), fg='#ecf0f1', bg='#34495e')
        self.chat_header.pack(pady=10)
        
        # Messages area
        self.messages_text = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD, 
                                                     font=('Arial', 10), bg='#ecf0f1', 
                                                     fg='#2c3e50', height=20)
        self.messages_text.pack(fill='both', expand=True, padx=10, pady=10)
        self.messages_text.config(state='disabled')
        
        # Configure text tags for styling
        self.messages_text.tag_configure('username', foreground='#3498db', font=('Arial', 10, 'bold'))
        self.messages_text.tag_configure('timestamp', foreground='#7f8c8d', font=('Arial', 8))
        self.messages_text.tag_configure('system', foreground='#e74c3c', font=('Arial', 10, 'italic'))
        self.messages_text.tag_configure('emoji', font=('Arial', 14))
        
        # Message input frame
        input_frame = tk.Frame(right_panel, bg='#34495e')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        # Message entry
        self.message_entry = tk.Entry(input_frame, font=('Arial', 12), bg='#ecf0f1')
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', self.send_message)
        
        # Buttons frame
        buttons_frame = tk.Frame(input_frame, bg='#34495e')
        buttons_frame.pack(side='right')
        
        # Send button
        send_btn = tk.Button(buttons_frame, text="Send", font=('Arial', 10), 
                           bg='#2ecc71', fg='white', padx=15, pady=5, 
                           command=self.send_message)
        send_btn.pack(side='left', padx=2)
        
        # Emoji button
        emoji_btn = tk.Button(buttons_frame, text="😊", font=('Arial', 12), 
                            bg='#f39c12', fg='white', padx=10, pady=5, 
                            command=self.show_emoji_picker)
        emoji_btn.pack(side='left', padx=2)
        
        # File button
        file_btn = tk.Button(buttons_frame, text="📁", font=('Arial', 12), 
                           bg='#9b59b6', fg='white', padx=10, pady=5, 
                           command=self.send_file)
        file_btn.pack(side='left', padx=2)
        
        # Load rooms
        self.load_rooms()
        
    def connect_to_server(self):
        """Connect to the chat server"""
        try:
            server = self.server_entry.get()
            port = int(self.port_entry.get())
            key = self.key_entry.get()
            
            if not key:
                self.status_label.config(text="Please enter the encryption key")
                return False
                
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((server, port))
            
            # Set up encryption
            self.encryption_key = key.encode()
            self.cipher = Fernet(self.encryption_key)
            
            self.connected = True
            
            # Start receiving messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
            
        except Exception as e:
            self.status_label.config(text=f"Connection failed: {str(e)}")
            return False
            
    def encrypt_message(self, message):
        """Encrypt message before sending"""
        return base64.b64encode(self.cipher.encrypt(message.encode())).decode()
        
    def decrypt_message(self, encrypted_message):
        """Decrypt received message"""
        try:
            return self.cipher.decrypt(base64.b64decode(encrypted_message.encode())).decode()
        except:
            return encrypted_message
            
    def send_data(self, data):
        """Send encrypted data to server"""
        if self.connected:
            try:
                encrypted_data = self.encrypt_message(json.dumps(data))
                self.socket.send(encrypted_data.encode())
            except Exception as e:
                print(f"Error sending data: {e}")
                
    def receive_messages(self):
        """Receive and handle messages from server"""
        while self.connected:
            try:
                encrypted_data = self.socket.recv(1024).decode()
                if encrypted_data:
                    data = json.loads(self.decrypt_message(encrypted_data))
                    self.handle_server_message(data)
                else:
                    break
            except Exception as e:
                if self.connected:
                    print(f"Error receiving message: {e}")
                break
                
    def handle_server_message(self, data):
        """Handle different types of messages from server"""
        if data['type'] == 'auth_result':
            if data['success']:
                self.username = data['username']
                self.root.after(0, self.create_chat_window)
            else:
                self.root.after(0, lambda: self.status_label.config(text=data['error']))
                
        elif data['type'] == 'register_result':
            if data['success']:
                self.root.after(0, lambda: self.status_label.config(text="Registration successful! Please login."))
            else:
                self.root.after(0, lambda: self.status_label.config(text=data['error']))
                
        elif data['type'] == 'rooms_list':
            self.root.after(0, lambda: self.update_rooms_list(data['rooms']))
            
        elif data['type'] == 'room_joined':
            self.current_room = data['room']
            self.root.after(0, lambda: self.update_chat_header(data['room']))
            self.root.after(0, lambda: self.display_message_history(data['history']))
            
        elif data['type'] == 'message':
            self.root.after(0, lambda: self.display_message(data))
            self.play_notification_sound()
            
        elif data['type'] == 'user_joined':
            self.root.after(0, lambda: self.display_system_message(f"{data['username']} joined the room"))
            
        elif data['type'] == 'user_left':
            self.root.after(0, lambda: self.display_system_message(f"{data['username']} left the room"))
            
        elif data['type'] == 'room_created':
            if data['success']:
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Room '{data['room']}' created successfully!"))
                self.load_rooms()
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", data['error']))
                
    def login(self):
        """Handle user login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.status_label.config(text="Please enter username and password")
            return
            
        if self.connect_to_server():
            auth_data = {
                'type': 'auth',
                'action': 'login',
                'username': username,
                'password': password
            }
            self.send_data(auth_data)
            
    def register(self):
        """Handle user registration"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not username or not password:
            self.status_label.config(text="Please enter username and password")
            return
            
        if self.connect_to_server():
            auth_data = {
                'type': 'auth',
                'action': 'register',
                'username': username,
                'password': password,
                'email': email
            }
            self.send_data(auth_data)
            
    def load_rooms(self):
        """Load available rooms from server"""
        self.send_data({'type': 'get_rooms'})
        
    def update_rooms_list(self, rooms):
        """Update the rooms list in the GUI"""
        self.rooms_listbox.delete(0, tk.END)
        for room in rooms:
            self.rooms_listbox.insert(tk.END, room)
            
    def join_room(self, event=None):
        """Join a selected room"""
        selection = self.rooms_listbox.curselection()
        if selection:
            room = self.rooms_listbox.get(selection[0])
            self.send_data({'type': 'join_room', 'room': room})
            
    def create_room_dialog(self):
        """Show dialog to create a new room"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Room")
        dialog.geometry("300x150")
        dialog.configure(bg='#34495e')
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Room Name:", font=('Arial', 12), 
                fg='#ecf0f1', bg='#34495e').pack(pady=10)
        
        room_entry = tk.Entry(dialog, font=('Arial', 12), width=25)
        room_entry.pack(pady=10)
        room_entry.focus()
        
        def create_room():
            room_name = room_entry.get().strip()
            if room_name:
                self.send_data({'type': 'create_room', 'room_name': room_name})
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Please enter a room name")
                
        button_frame = tk.Frame(dialog, bg='#34495e')
        button_frame.pack(pady=10)
        
        create_btn = tk.Button(button_frame, text="Create", font=('Arial', 10), 
                             bg='#2ecc71', fg='white', padx=15, pady=5, 
                             command=create_room)
        create_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", font=('Arial', 10), 
                             bg='#e74c3c', fg='white', padx=15, pady=5, 
                             command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)
        
        dialog.bind('<Return>', lambda e: create_room())
        
    def update_chat_header(self, room):
        """Update the chat header with current room"""
        self.chat_header.config(text=f"Room: {room}")
        
    def display_message_history(self, history):
        """Display message history when joining a room"""
        self.messages_text.config(state='normal')
        self.messages_text.delete(1.0, tk.END)
        
        for message in history:
            username, content, msg_type, timestamp = message
            self.display_message({
                'username': username,
                'message': content,
                'message_type': msg_type,
                'timestamp': timestamp
            }, from_history=True)
            
        self.messages_text.config(state='disabled')
        
    def display_message(self, data, from_history=False):
        """Display a message in the chat window"""
        self.messages_text.config(state='normal')
        
        # Format timestamp
        if from_history:
            timestamp = data['timestamp']
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
        # Insert timestamp
        self.messages_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Insert username
        self.messages_text.insert(tk.END, f"{data['username']}: ", 'username')
        
        # Handle different message types
        if data.get('message_type') == 'image':
            self.display_image_message(data['message'])
        elif data.get('message_type') == 'file':
            self.display_file_message(data['message'])
        else:
            # Process text for emojis
            message = self.process_emojis(data['message'])
            self.messages_text.insert(tk.END, message + '\n')
            
        self.messages_text.config(state='disabled')
        self.messages_text.see(tk.END)
        
    def display_system_message(self, message):
        """Display system messages"""
        self.messages_text.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages_text.insert(tk.END, f"[{timestamp}] {message}\n", 'system')
        self.messages_text.config(state='disabled')
        self.messages_text.see(tk.END)
        
    def display_image_message(self, image_data):
        """Display image messages"""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Resize image if too large
            max_size = (300, 300)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            self.messages_text.image_create(tk.END, image=photo)
            self.messages_text.insert(tk.END, '\n')
            
            # Keep a reference to prevent garbage collection
            if not hasattr(self, 'images'):
                self.images = []
            self.images.append(photo)
            
        except Exception as e:
            self.messages_text.insert(tk.END, f"[Image could not be displayed: {str(e)}]\n")
            
    def display_file_message(self, file_data):
        """Display file messages"""
        try:
            file_info = json.loads(file_data)
            filename = file_info['filename']
            size = file_info['size']
            
            self.messages_text.insert(tk.END, f"📁 File: {filename} ({size} bytes)\n")
            
        except Exception as e:
            self.messages_text.insert(tk.END, f"[File info could not be displayed: {str(e)}]\n")
            
    def process_emojis(self, text):
        """Process emoji shortcuts in text"""
        emoji_dict = {
            ':)': '😊', ':-)': '😊', ':(': '😢', ':-(': '😢',
            ':D': '😄', ':-D': '😄', ';)': '😉', ';-)': '😉',
            ':P': '😛', ':-P': '😛', ':o': '😮', ':-o': '😮',
            '<3': '❤️', '</3': '💔', ':thumbsup:': '👍', ':thumbsdown:': '👎',
            ':fire:': '🔥', ':star:': '⭐', ':check:': '✅', ':cross:': '❌'
        }
        
        for shortcut, emoji in emoji_dict.items():
            text = text.replace(shortcut, emoji)
            
        return text
        
    def show_emoji_picker(self):
        """Show emoji picker dialog"""
        emoji_window = tk.Toplevel(self.root)
        emoji_window.title("Emoji Picker")
        emoji_window.geometry("400x300")
        emoji_window.configure(bg='#34495e')
        emoji_window.resizable(False, False)
        
        # Center the window
        emoji_window.transient(self.root)
        emoji_window.grab_set()
        
        # Common emojis
        emojis = [
            '😊', '😄', '😆', '😂', '🤣', '😍', '😘', '😗',
            '😙', '😚', '🤗', '🤔', '😐', '😑', '😶', '🙄',
            '😏', '😣', '😥', '😮', '🤐', '😯', '😪', '😫',
            '😴', '😌', '😛', '😜', '😝', '🤤', '😒', '😓',
            '😔', '😕', '🙃', '🤑', '😲', '🙁', '😖', '😞',
            '😟', '😤', '😢', '😭', '😦', '😧', '😨', '😩',
            '🤯', '😬', '😰', '😱', '😳', '🤪', '😵', '😡',
            '😠', '🤬', '😷', '🤒', '🤕', '🤢', '🤮', '🤧',
            '😇', '🤠', '🤡', '🤥', '🤫', '🤭', '🧐', '🤓',
            '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙',
            '👈', '👉', '👆', '👇', '☝️', '✋', '🤚', '🖐️',
            '🖖', '👋', '🤙', '💪', '🙏', '✍️', '💅', '🤳',
            '❤️', '💔', '💕', '💖', '💗', '💘', '💙', '💚',
            '💛', '🧡', '💜', '🖤', '💯', '💢', '💥', '💫',
            '💦', '💨', '🕳️', '💣', '💬', '💭', '💤', '🔥'
        ]
        
        # Create emoji buttons
        row = 0
        col = 0
        for emoji in emojis:
            btn = tk.Button(emoji_window, text=emoji, font=('Arial', 16), 
                          bg='#ecf0f1', fg='black', width=3, height=1,
                          command=lambda e=emoji: self.insert_emoji(e, emoji_window))
            btn.grid(row=row, column=col, padx=2, pady=2)
            
            col += 1
            if col > 7:
                col = 0
                row += 1
                
    def insert_emoji(self, emoji, window):
        """Insert selected emoji into message entry"""
        current_text = self.message_entry.get()
        cursor_pos = self.message_entry.index(tk.INSERT)
        new_text = current_text[:cursor_pos] + emoji + current_text[cursor_pos:]
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, new_text)
        self.message_entry.icursor(cursor_pos + len(emoji))
        window.destroy()
        self.message_entry.focus()
        
    def send_file(self):
        """Send a file"""
        file_path = filedialog.askopenfilename(
            title="Select file to send",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Documents", "*.txt *.pdf *.doc *.docx"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Check file size (limit to 5MB)
                file_size = os.path.getsize(file_path)
                if file_size > 5 * 1024 * 1024:
                    messagebox.showerror("Error", "File size must be less than 5MB")
                    return
                    
                filename = os.path.basename(file_path)
                mime_type, _ = mimetypes.guess_type(file_path)
                
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    
                # Check if it's an image
                if mime_type and mime_type.startswith('image/'):
                    # Send as image
                    encoded_data = base64.b64encode(file_data).decode()
                    message_data = {
                        'type': 'message',
                        'message': encoded_data,
                        'message_type': 'image'
                    }
                else:
                    # Send as file
                    file_info = {
                        'filename': filename,
                        'size': file_size,
                        'mime_type': mime_type,
                        'data': base64.b64encode(file_data).decode()
                    }
                    message_data = {
                        'type': 'message',
                        'message': json.dumps(file_info),
                        'message_type': 'file'
                    }
                    
                self.send_data(message_data)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send file: {str(e)}")
                
    def send_message(self, event=None):
        """Send a text message"""
        message = self.message_entry.get().strip()
        if message and self.current_room:
            message_data = {
                'type': 'message',
                'message': message,
                'message_type': 'text'
            }
            self.send_data(message_data)
            self.message_entry.delete(0, tk.END)
            
    def play_notification_sound(self):
        """Play notification sound for new messages"""
        try:
            # Generate a simple beep sound
            pygame.mixer.init()
            # Create a simple tone
            duration = 0.1
            sample_rate = 22050
            frames = int(duration * sample_rate)
            arr = []
            for i in range(frames):
                time_val = float(i) / sample_rate
                wave = 0.5 * np.sin(2 * np.pi * 800 * time_val)
                arr.append([int(wave * 32767), int(wave * 32767)])
            
            sound = pygame.sndarray.make_sound(np.array(arr))
            sound.play()
            
        except Exception as e:
            print(f"Could not play notification sound: {e}")
            
    def show_notification(self, title, message):
        """Show desktop notification (Windows/Linux)"""
        try:
            if os.name == 'nt':  # Windows
                import win10toast
                toaster = win10toast.ToastNotifier()
                toaster.show_toast(title, message, duration=3)
            else:  # Linux
                os.system(f'notify-send "{title}" "{message}"')
        except:
            pass  # Fallback: no notification
            
    def disconnect(self):
        """Disconnect from server and return to login"""
        self.connected = False
        if self.socket:
            self.socket.close()
            
        # Destroy chat frame and recreate login
        self.chat_frame.destroy()
        self.create_login_window()
        
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle application closing"""
        if self.connected:
            self.connected = False
            if self.socket:
                self.socket.close()
        self.root.destroy()

if __name__ == "__main__":
    # Install required packages if not available
    try:
        import pygame
        import numpy as np
        from PIL import Image, ImageTk
        from cryptography.fernet import Fernet
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install required packages:")
        print("pip install pygame pillow cryptography numpy")
        exit(1)
        
    client = ChatClient()
    client.run()