"""
Advanced Password Generator with GUI
A comprehensive password generator with security features, customization options,
and clipboard integration using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import string
import secrets
import pyperclip
import json
import os
from datetime import datetime
import re

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Password Generator")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Character sets
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        self.ambiguous = "0O1lI"
        
        # Password history
        self.history_file = "password_history.json"
        self.password_history = self.load_history()
        
        # Create interface
        self.create_widgets()
        
        # Initialize variables
        self.update_character_preview()
        
    def load_history(self):
        """Load password generation history"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def save_history(self, password_info):
        """Save password to history"""
        try:
            self.password_history.append(password_info)
            # Keep only last 50 entries
            if len(self.password_history) > 50:
                self.password_history = self.password_history[-50:]
            
            with open(self.history_file, 'w') as f:
                json.dump(self.password_history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Title
        title_label = tk.Label(self.root, text="Advanced Password Generator", 
                       font=("Arial", 20, "bold"), 
                       bg='#f0f0f0', fg='#333')
        title_label.pack(pady=(5, 0))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Generator tab
        self.generator_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.generator_frame, text="Generator")
        self.create_generator_tab()
        
        # History tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="History")
        self.create_history_tab()
        
        # Security tab
        self.security_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.security_frame, text="Security Tips")
        self.create_security_tab()
    
    def create_generator_tab(self):
        """Create the main password generator interface"""
        # Password length frame
        length_frame = ttk.LabelFrame(self.generator_frame, text="Password Length", padding=10)
        length_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(length_frame, text="Length:").grid(row=0, column=0, sticky='w')
        self.length_var = tk.IntVar(value=12)
        length_spinbox = tk.Spinbox(length_frame, from_=4, to=128, 
                                   textvariable=self.length_var, width=10)
        length_spinbox.grid(row=0, column=1, padx=5)
        
        # Length slider
        self.length_scale = tk.Scale(length_frame, from_=4, to=64, 
                                    orient='horizontal', variable=self.length_var,
                                    command=self.on_length_change)
        self.length_scale.grid(row=0, column=2, padx=10, sticky='ew')
        length_frame.grid_columnconfigure(2, weight=1)
        
        # Character options frame
        char_frame = ttk.LabelFrame(self.generator_frame, text="Character Options", padding=10)
        char_frame.pack(fill='x', padx=10, pady=5)
        
        # Character type checkboxes
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(char_frame, text="Lowercase (a-z)", 
                       variable=self.use_lowercase,
                       command=self.update_character_preview).grid(row=0, column=0, sticky='w', pady=2)
        ttk.Checkbutton(char_frame, text="Uppercase (A-Z)", 
                       variable=self.use_uppercase,
                       command=self.update_character_preview).grid(row=0, column=1, sticky='w', pady=2)
        ttk.Checkbutton(char_frame, text="Digits (0-9)", 
                       variable=self.use_digits,
                       command=self.update_character_preview).grid(row=1, column=0, sticky='w', pady=2)
        ttk.Checkbutton(char_frame, text="Symbols (!@#$%^&*)", 
                       variable=self.use_symbols,
                       command=self.update_character_preview).grid(row=1, column=1, sticky='w', pady=2)
        
        # Advanced options frame
        advanced_frame = ttk.LabelFrame(self.generator_frame, text="Advanced Options", padding=10)
        advanced_frame.pack(fill='x', padx=10, pady=5)
        
        # Security options
        self.exclude_ambiguous = tk.BooleanVar(value=False)
        self.enforce_complexity = tk.BooleanVar(value=True)
        self.use_secure_random = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(advanced_frame, text="Exclude ambiguous characters (0, O, 1, l, I)", 
                       variable=self.exclude_ambiguous,
                       command=self.update_character_preview).grid(row=0, column=0, sticky='w', pady=2)
        ttk.Checkbutton(advanced_frame, text="Enforce complexity rules", 
                       variable=self.enforce_complexity).grid(row=1, column=0, sticky='w', pady=2)
        ttk.Checkbutton(advanced_frame, text="Use cryptographically secure random", 
                       variable=self.use_secure_random).grid(row=2, column=0, sticky='w', pady=2)
        
        # Custom exclusions
        tk.Label(advanced_frame, text="Exclude specific characters:").grid(row=3, column=0, sticky='w', pady=(10,2))
        self.exclude_chars_var = tk.StringVar()
        exclude_entry = ttk.Entry(advanced_frame, textvariable=self.exclude_chars_var, width=30)
        exclude_entry.grid(row=4, column=0, sticky='w', pady=2)
        exclude_entry.bind('<KeyRelease>', lambda e: self.update_character_preview())
        
        # Character preview
        preview_frame = ttk.LabelFrame(self.generator_frame, text="Character Set Preview", padding=10)
        preview_frame.pack(fill='x', padx=10, pady=5)
        
        self.char_preview = tk.Text(preview_frame, height=3, wrap='word', 
                                   font=("Courier", 10), state='disabled')
        self.char_preview.pack(fill='x')
        
        # Password generation frame
        gen_frame = ttk.LabelFrame(self.generator_frame, text="Generate Password", padding=10)
        gen_frame.pack(fill='x', padx=10, pady=5)
        
        # Generate button
        generate_btn = ttk.Button(gen_frame, text="Generate Password", 
                                 command=self.generate_password, 
                                 style='Accent.TButton')
        generate_btn.pack(pady=5)
        
        # Generated password display
        self.password_text = tk.Text(gen_frame, height=3, wrap='word', 
                                    font=("Courier", 12), bg='#ffffff')
        self.password_text.pack(fill='x', pady=5)
        
        # Action buttons frame
        action_frame = ttk.Frame(gen_frame)
        action_frame.pack(fill='x', pady=5)
        
        ttk.Button(action_frame, text="Copy to Clipboard", 
           command=self.copy_to_clipboard, width=20).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Save to File", 
           command=self.save_to_file, width=20).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Test Strength", 
           command=self.test_password_strength, width=20).pack(side='left', padx=5)
        
        # Strength indicator
        self.strength_frame = ttk.Frame(gen_frame)
        self.strength_frame.pack(fill='x', pady=5)
        
        tk.Label(self.strength_frame, text="Strength:").pack(side='left')
        self.strength_bar = ttk.Progressbar(self.strength_frame, mode='determinate')
        self.strength_bar.pack(side='left', fill='x', expand=True, padx=5)
        self.strength_label = tk.Label(self.strength_frame, text="", font=("Arial", 10, "bold"))
        self.strength_label.pack(side='right')
    
    def create_history_tab(self):
        """Create the password history interface"""
        # History listbox with scrollbar
        list_frame = ttk.Frame(self.history_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.history_listbox = tk.Listbox(list_frame, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.history_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons frame
        button_frame = ttk.Frame(self.history_frame)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Refresh History", 
                  command=self.refresh_history).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Copy Selected", 
                  command=self.copy_selected_from_history).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear History", 
                  command=self.clear_history).pack(side='left', padx=5)
        
        # Load initial history
        self.refresh_history()
    
    def create_security_tab(self):
        """Create the security tips interface"""
        # Security tips text
        tips_text = tk.Text(self.security_frame, wrap='word', padx=10, pady=10,
                           font=("Arial", 11), state='disabled')
        tips_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        security_tips = """
PASSWORD SECURITY BEST PRACTICES

1. PASSWORD LENGTH
   • Use at least 12 characters (16+ recommended)
   • Longer passwords are exponentially more secure
   • Each additional character dramatically increases cracking time

2. CHARACTER COMPLEXITY
   • Mix uppercase and lowercase letters
   • Include numbers and special symbols
   • Avoid predictable patterns or keyboard walks

3. UNIQUENESS
   • Use a unique password for each account
   • Never reuse passwords across different services
   • Consider using a password manager

4. AVOIDING COMMON MISTAKES
   • Don't use personal information (names, birthdays, addresses)
   • Avoid dictionary words or common phrases
   • Don't use simple substitutions (@ for a, 3 for e)

5. STORAGE AND MANAGEMENT
   • Use a reputable password manager
   • Enable two-factor authentication when available
   • Don't write passwords down in plain text

6. REGULAR UPDATES
   • Change passwords if a breach is suspected
   • Update passwords periodically for critical accounts
   • Monitor accounts for suspicious activity

7. ADDITIONAL SECURITY MEASURES
   • Use biometric authentication when available
   • Keep software and browsers updated
   • Be cautious of phishing attempts

Remember: A strong password is your first line of defense against cyber threats!
        """
        
        tips_text.config(state='normal')
        tips_text.insert('1.0', security_tips)
        tips_text.config(state='disabled')
    
    def on_length_change(self, value):
        """Handle password length change"""
        self.update_character_preview()
    
    def update_character_preview(self):
        """Update the character set preview"""
        charset = self.build_character_set()
        
        self.char_preview.config(state='normal')
        self.char_preview.delete('1.0', tk.END)
        
        if charset:
            preview_text = f"Available characters ({len(charset)}): {charset[:100]}"
            if len(charset) > 100:
                preview_text += f"... (+{len(charset) - 100} more)"
        else:
            preview_text = "No character types selected!"
        
        self.char_preview.insert('1.0', preview_text)
        self.char_preview.config(state='disabled')
    
    def build_character_set(self):
        """Build the character set based on user selections"""
        charset = ""
        
        if self.use_lowercase.get():
            charset += self.lowercase
        if self.use_uppercase.get():
            charset += self.uppercase
        if self.use_digits.get():
            charset += self.digits
        if self.use_symbols.get():
            charset += self.symbols
        
        # Remove ambiguous characters if requested
        if self.exclude_ambiguous.get():
            charset = ''.join(c for c in charset if c not in self.ambiguous)
        
        # Remove custom excluded characters
        exclude_chars = self.exclude_chars_var.get()
        if exclude_chars:
            charset = ''.join(c for c in charset if c not in exclude_chars)
        
        return charset
    
    def generate_password(self):
        """Generate a password based on user settings"""
        try:
            length = self.length_var.get()
            charset = self.build_character_set()
            
            if not charset:
                messagebox.showerror("Error", "Please select at least one character type!")
                return
            
            if length < 4:
                messagebox.showerror("Error", "Password length must be at least 4 characters!")
                return
            
            # Generate password
            if self.enforce_complexity.get():
                password = self.generate_complex_password(length, charset)
            else:
                password = self.generate_simple_password(length, charset)
            
            if not password:
                messagebox.showerror("Error", "Unable to generate password with current settings!")
                return
            
            # Display password
            self.password_text.delete('1.0', tk.END)
            self.password_text.insert('1.0', password)
            
            # Test strength
            self.test_password_strength()
            
            # Save to history
            self.save_to_history(password, length, charset)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate password: {str(e)}")
    
    def generate_simple_password(self, length, charset):
        """Generate a simple random password"""
        if self.use_secure_random.get():
            return ''.join(secrets.choice(charset) for _ in range(length))
        else:
            return ''.join(random.choice(charset) for _ in range(length))
    
    def generate_complex_password(self, length, charset):
        """Generate a password ensuring complexity requirements"""
        # Determine required character types
        required_types = []
        if self.use_lowercase.get():
            required_types.append(self.lowercase)
        if self.use_uppercase.get():
            required_types.append(self.uppercase)
        if self.use_digits.get():
            required_types.append(self.digits)
        if self.use_symbols.get():
            required_types.append(self.symbols)
        
        if not required_types or length < len(required_types):
            return None
        
        # Apply exclusions to required types
        exclude_chars = self.exclude_chars_var.get()
        if self.exclude_ambiguous.get():
            exclude_chars += self.ambiguous
        
        for i, char_type in enumerate(required_types):
            if exclude_chars:
                required_types[i] = ''.join(c for c in char_type if c not in exclude_chars)
        
        # Generate password ensuring at least one character from each type
        password = []
        random_func = secrets.choice if self.use_secure_random.get() else random.choice
        
        # Add one character from each required type
        for char_type in required_types:
            if char_type:  # Only if type has characters after exclusions
                password.append(random_func(char_type))
        
        # Fill remaining length with random characters from full charset
        remaining_length = length - len(password)
        for _ in range(remaining_length):
            password.append(random_func(charset))
        
        # Shuffle the password to avoid predictable patterns
        if self.use_secure_random.get():
            # Secure shuffle using secrets
            for i in range(len(password) - 1, 0, -1):
                j = secrets.randbelow(i + 1)
                password[i], password[j] = password[j], password[i]
        else:
            random.shuffle(password)
        
        return ''.join(password)
    
    def test_password_strength(self):
        """Test and display password strength"""
        password = self.password_text.get('1.0', tk.END).strip()
        if not password:
            return
        
        score = self.calculate_password_strength(password)
        
        # Update strength bar
        self.strength_bar['value'] = score
        
        # Update strength label
        if score < 30:
            strength_text = "Very Weak"
            color = "#ff4444"
        elif score < 50:
            strength_text = "Weak"
            color = "#ff8800"
        elif score < 70:
            strength_text = "Fair"
            color = "#ffaa00"
        elif score < 85:
            strength_text = "Good"
            color = "#88cc00"
        else:
            strength_text = "Strong"
            color = "#00cc44"
        
        self.strength_label.config(text=strength_text, fg=color)
    
    def calculate_password_strength(self, password):
        """Calculate password strength score (0-100)"""
        score = 0
        
        # Length scoring
        length = len(password)
        if length >= 8:
            score += 20
        if length >= 12:
            score += 10
        if length >= 16:
            score += 10
        
        # Character type scoring
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'[0-9]', password):
            score += 10
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 15
        
        # Complexity bonuses
        if len(set(password)) > length * 0.7:  # High character diversity
            score += 10
        if not re.search(r'(.)\1{2,}', password):  # No repeated characters
            score += 5
        if not re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde)', password.lower()):
            score += 5  # No sequential patterns
        
        return min(100, score)
    
    def copy_to_clipboard(self):
        """Copy generated password to clipboard"""
        password = self.password_text.get('1.0', tk.END).strip()
        if password:
            try:
                pyperclip.copy(password)
                messagebox.showinfo("Success", "Password copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No password to copy!")
    
    def save_to_file(self):
        """Save generated password to a file"""
        password = self.password_text.get('1.0', tk.END).strip()
        if not password:
            messagebox.showwarning("Warning", "No password to save!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(f"Generated Password: {password}\n")
                    f.write(f"Length: {len(password)}\n")
                    f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                messagebox.showinfo("Success", f"Password saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save password: {str(e)}")
    
    def save_to_history(self, password, length, charset):
        """Save password generation info to history"""
        history_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'length': length,
            'charset_length': len(charset),
            'password': password[:4] + '*' * (length - 4),  # Partially masked
            'strength': self.calculate_password_strength(password)
        }
        self.save_history(history_entry)
        self.refresh_history()
    
    def refresh_history(self):
        """Refresh the history listbox"""
        self.history_listbox.delete(0, tk.END)
        for entry in reversed(self.password_history):  # Most recent first
            line = f"{entry['timestamp']} | Len: {entry['length']:2d} | Chars: {entry['charset_length']:3d} | {entry['password']} | Strength: {entry['strength']:2d}"
            self.history_listbox.insert(tk.END, line)
    
    def copy_selected_from_history(self):
        """Copy selected password from history"""
        selection = self.history_listbox.curselection()
        if selection:
            messagebox.showinfo("Info", "For security reasons, full passwords are not stored in history.\nGenerate a new password instead.")
        else:
            messagebox.showwarning("Warning", "Please select a history entry first!")
    
    def clear_history(self):
        """Clear password history"""
        if messagebox.askyesno("Confirm", "Clear all password history?"):
            self.password_history = []
            try:
                if os.path.exists(self.history_file):
                    os.remove(self.history_file)
            except Exception:
                pass
            self.refresh_history()
            messagebox.showinfo("Success", "History cleared")

def main():
    """Main function to run the password generator"""
    root = tk.Tk()
    
    # Configure ttk styles
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
    
    app = PasswordGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()