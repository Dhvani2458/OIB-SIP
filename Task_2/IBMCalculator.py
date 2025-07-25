"""
BMI Calculator - Advanced GUI Version
A comprehensive BMI calculator with GUI, data storage, and visualization capabilities.
Features: User management, historical data tracking, BMI trends, and interactive charts.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class BMICalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator - Advanced")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.data_file = "bmi_data.json"
        self.users_data = self.load_data()
        self.current_user = None
        self.root.option_add("*Button.Font", "Arial 10")

        
        # Create main interface
        self.create_widgets()
        
    def load_data(self):
        """Load user data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            return {}
    
    def save_data(self):
        """Save user data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.users_data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
    
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Title
        title_label = tk.Label(self.root, text="BMI Calculator", 
                              font=("Arial", 24, "bold"), 
                              bg='#f0f0f0', fg='#333')
        title_label.pack(pady=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Calculator tab
        self.calc_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.calc_frame, text="Calculator")
        self.create_calculator_tab()
        
        # History tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="History")
        self.create_history_tab()
        
        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self.create_stats_tab()
    
    def create_calculator_tab(self):
        """Create the main calculator interface"""
        # User selection frame
        user_frame = ttk.LabelFrame(self.calc_frame, text="User", padding=10)
        user_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(user_frame, text="Select User:").grid(row=0, column=0, sticky='w')
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(user_frame, textvariable=self.user_var, 
                                      values=list(self.users_data.keys()))
        self.user_combo.grid(row=0, column=1, padx=5)
        self.user_combo.bind('<<ComboboxSelected>>', self.on_user_selected)
        
        tk.Button(user_frame, text="New User", command=self.create_new_user,
          bg="#4CAF50", fg="white", activebackground="#388E3C",
          font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)
        
        # Input frame
        input_frame = ttk.LabelFrame(self.calc_frame, text="BMI Calculation", padding=10)
        input_frame.pack(fill='x', padx=10, pady=10)
        
        # Weight input
        tk.Label(input_frame, text="Weight (kg):").grid(row=0, column=0, sticky='w', pady=5)
        self.weight_var = tk.StringVar()
        self.weight_entry = ttk.Entry(input_frame, textvariable=self.weight_var, width=15)
        self.weight_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Height input
        tk.Label(input_frame, text="Height (m):").grid(row=1, column=0, sticky='w', pady=5)
        self.height_var = tk.StringVar()
        self.height_entry = ttk.Entry(input_frame, textvariable=self.height_var, width=15)
        self.height_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Calculate button
        tk.Button(input_frame, text="Calculate BMI", command=self.calculate_bmi,
          bg="#2196F3", fg="white", activebackground="#1976D2",
          font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.calc_frame, text="Results", padding=10)
        results_frame.pack(fill='x', padx=10, pady=10)
        
        self.result_label = tk.Label(results_frame, text="Enter your measurements and click Calculate", 
                                    font=("Arial", 12), bg='white', relief='sunken', padx=10, pady=10)
        self.result_label.pack(fill='x')
        
        # BMI categories info
        info_frame = ttk.LabelFrame(self.calc_frame, text="BMI Categories", padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        categories = [
            "Underweight: BMI < 18.5",
            "Normal weight: BMI 18.5-24.9",
            "Overweight: BMI 25-29.9",
            "Obese: BMI ≥ 30"
        ]
        
        for i, category in enumerate(categories):
            tk.Label(info_frame, text=category).grid(row=i, column=0, sticky='w', pady=2)
    
    def create_history_tab(self):
        """Create the history viewing interface"""
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
        
        tk.Button(button_frame, text="Refresh History", command=self.refresh_history,
          bg="#FF9800", fg="white", activebackground="#F57C00").pack(side='left', padx=5)
        tk.Button(button_frame, text="Export Data", command=self.export_data,
          bg="#9C27B0", fg="white", activebackground="#7B1FA2").pack(side='left', padx=5)
        tk.Button(button_frame, text="Clear History", command=self.clear_history,
          bg="#F44336", fg="white", activebackground="#D32F2F").pack(side='left', padx=5)
    
    def create_stats_tab(self):
        """Create the statistics and visualization interface"""
        # Controls frame
        controls_frame = ttk.Frame(self.stats_frame)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(controls_frame, text="Generate Chart", command=self.generate_chart,
          bg="#00BCD4", fg="white", activebackground="#0097A7").pack(side='left', padx=5)
        tk.Button(controls_frame, text="Show Statistics", command=self.show_statistics,
          bg="#607D8B", fg="white", activebackground="#455A64").pack(side='left', padx=5)
        
        # Chart frame
        self.chart_frame = ttk.Frame(self.stats_frame)
        self.chart_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_new_user(self):
        """Create a new user profile"""
        dialog = tk.Toplevel(self.root)
        dialog.title("New User")
        dialog.align = 'center'
        dialog.grab_set()
        
        tk.Label(dialog, text="Enter username:").pack(pady=10)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=20)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        def save_user():
            username = name_var.get().strip()
            if username:
                if username not in self.users_data:
                    self.users_data[username] = []
                    self.save_data()
                    self.user_combo['values'] = list(self.users_data.keys())
                    self.user_var.set(username)
                    self.current_user = username
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Username already exists!")
            else:
                messagebox.showerror("Error", "Please enter a username!")
        
        ttk.Button(dialog, text="Create", command=save_user).pack(pady=10)
        dialog.bind('<Return>', lambda e: save_user())
    
    def on_user_selected(self, event):
        """Handle user selection"""
        self.current_user = self.user_var.get()
        self.refresh_history()
    
    def calculate_bmi(self):
        """Calculate BMI and save to history"""
        try:
            weight = float(self.weight_var.get())
            height = float(self.height_var.get())
            
            # Validate inputs
            if not (20 <= weight <= 300):
                messagebox.showerror("Error", "Weight must be between 20 and 300 kg")
                return
            if not (1.0 <= height <= 2.5):
                messagebox.showerror("Error", "Height must be between 1.0 and 2.5 meters")
                return
            
            # Calculate BMI
            bmi = weight / (height ** 2)
            category = self.classify_bmi(bmi)
            
            # Display results
            result_text = f"BMI: {bmi:.2f}\nCategory: {category}\nWeight: {weight} kg\nHeight: {height} m"
            self.result_label.config(text=result_text)
            
            # Save to history if user is selected
            if self.current_user:
                record = {
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'weight': weight,
                    'height': height,
                    'bmi': round(bmi, 2),
                    'category': category
                }
                self.users_data[self.current_user].append(record)
                self.save_data()
                self.refresh_history()
            else:
                messagebox.showwarning("Warning", "Please select or create a user to save history")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for weight and height")
    
    def classify_bmi(self, bmi):
        """Classify BMI into health categories"""
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal weight"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    def refresh_history(self):
        """Refresh the history listbox"""
        self.history_listbox.delete(0, tk.END)
        if self.current_user and self.current_user in self.users_data:
            history = self.users_data[self.current_user]
            for record in reversed(history):  # Show most recent first
                line = f"{record['date']} | BMI: {record['bmi']:5.2f} | {record['category']:12} | {record['weight']:5.1f}kg, {record['height']:4.2f}m"
                self.history_listbox.insert(tk.END, line)
    
    def export_data(self):
        """Export user data to a file"""
        if not self.current_user:
            messagebox.showwarning("Warning", "Please select a user first")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump({self.current_user: self.users_data[self.current_user]}, f, indent=2)
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def clear_history(self):
        """Clear history for current user"""
        if not self.current_user:
            messagebox.showwarning("Warning", "Please select a user first")
            return
        
        if messagebox.askyesno("Confirm", f"Clear all history for {self.current_user}?"):
            self.users_data[self.current_user] = []
            self.save_data()
            self.refresh_history()
            messagebox.showinfo("Success", "History cleared")
    
    def generate_chart(self):
        """Generate BMI trend chart"""
        if not self.current_user or not self.users_data.get(self.current_user):
            messagebox.showwarning("Warning", "No data available for selected user")
            return
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Prepare data
        history = self.users_data[self.current_user]
        dates = [datetime.strptime(record['date'], "%Y-%m-%d %H:%M:%S") for record in history]
        bmis = [record['bmi'] for record in history]
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, bmis, marker='o', linewidth=2, markersize=6)
        ax.set_xlabel('Date')
        ax.set_ylabel('BMI')
        ax.set_title(f'BMI Trend for {self.current_user}')
        ax.grid(True, alpha=0.3)
        
        # Add BMI category zones
        ax.axhspan(0, 18.5, alpha=0.1, color='blue', label='Underweight')
        ax.axhspan(18.5, 25, alpha=0.1, color='green', label='Normal')
        ax.axhspan(25, 30, alpha=0.1, color='orange', label='Overweight')
        ax.axhspan(30, 50, alpha=0.1, color='red', label='Obese')
        
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Embed chart in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def show_statistics(self):
        """Show statistical summary"""
        if not self.current_user or not self.users_data.get(self.current_user):
            messagebox.showwarning("Warning", "No data available for selected user")
            return
        
        history = self.users_data[self.current_user]
        bmis = [record['bmi'] for record in history]
        
        if bmis:
            stats = {
                'Total Records': len(bmis),
                'Average BMI': np.mean(bmis),
                'Minimum BMI': min(bmis),
                'Maximum BMI': max(bmis),
                'BMI Range': max(bmis) - min(bmis),
                'Current BMI': bmis[-1] if bmis else 'N/A'
            }
            
            stats_text = f"Statistics for {self.current_user}:\n\n"
            for key, value in stats.items():
                if isinstance(value, float):
                    stats_text += f"{key}: {value:.2f}\n"
                else:
                    stats_text += f"{key}: {value}\n"
            
            messagebox.showinfo("Statistics", stats_text)

def main():
    """Main function to run the BMI calculator"""
    root = tk.Tk()
    app = BMICalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()