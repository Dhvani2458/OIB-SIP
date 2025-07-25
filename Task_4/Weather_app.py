import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime, timedelta
import threading
from PIL import Image, ImageTk
import io
import base64

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Weather App")
        self.root.geometry("800x800")
        self.root.configure(bg='#2c3e50')
        
        # Weather API key (you'll need to get your own from OpenWeatherMap)
        self.api_key = "48ec904046a66f2a9a9d1266d8b92aa8"  # Replace with your OpenWeatherMap API key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # Temperature unit (metric or imperial)
        self.temp_unit = tk.StringVar(value="metric")
        
        # Create GUI elements
        self.create_widgets()
        
        # Load default location
        self.get_weather_by_location("New York")
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header frame
        header_frame = tk.Frame(main_frame, bg='#2c3e50')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(header_frame, text="🌤️ Advanced Weather App", 
                              font=('Arial', 20, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(side=tk.LEFT)
        
        # Unit selection
        unit_frame = tk.Frame(header_frame, bg='#2c3e50')
        unit_frame.pack(side=tk.RIGHT)
        
        tk.Label(unit_frame, text="Units:", font=('Arial', 12), 
                fg='#ecf0f1', bg='#2c3e50').pack(side=tk.LEFT)
        
        celsius_rb = tk.Radiobutton(unit_frame, text="°C", variable=self.temp_unit, 
                                   value="metric", font=('Arial', 10),
                                   fg='#ecf0f1', bg='#2c3e50', 
                                   selectcolor='#34495e',
                                   command=self.refresh_weather)
        celsius_rb.pack(side=tk.LEFT, padx=5)
        
        fahrenheit_rb = tk.Radiobutton(unit_frame, text="°F", variable=self.temp_unit, 
                                      value="imperial", font=('Arial', 10),
                                      fg='#ecf0f1', bg='#2c3e50', 
                                      selectcolor='#34495e',
                                      command=self.refresh_weather)
        fahrenheit_rb.pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg='#2c3e50')
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.location_entry = tk.Entry(search_frame, font=('Arial', 14), 
                                      width=30, relief=tk.FLAT, 
                                      bg='#34495e', fg='#ecf0f1',
                                      insertbackground='#ecf0f1')
        self.location_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=8)
        self.location_entry.bind('<Return>', self.on_search)
        
        search_btn = tk.Button(search_frame, text="🔍 Search", 
                              font=('Arial', 12, 'bold'),
                              bg='#3498db', fg='white', 
                              relief=tk.FLAT, padx=15, pady=8,
                              command=self.search_weather)
        search_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        gps_btn = tk.Button(search_frame, text="📍 Current Location", 
                           font=('Arial', 12, 'bold'),
                           bg='#e74c3c', fg='white', 
                           relief=tk.FLAT, padx=15, pady=8,
                           command=self.get_current_location)
        gps_btn.pack(side=tk.LEFT)
        
        # Weather display frame
        self.weather_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        self.weather_frame.pack(fill=tk.BOTH, expand=True)
        
        # Current weather frame
        self.current_frame = tk.Frame(self.weather_frame, bg='#34495e')
        self.current_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Forecast frame
        self.forecast_frame = tk.Frame(self.weather_frame, bg='#34495e')
        self.forecast_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Status bar
        self.status_bar = tk.Label(main_frame, text="Ready", 
                                  font=('Arial', 10), 
                                  fg='#7f8c8d', bg='#2c3e50',
                                  anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Initialize weather display
        self.show_loading()
    
    def show_loading(self):
        """Show loading message"""
        for widget in self.current_frame.winfo_children():
            widget.destroy()
        
        loading_label = tk.Label(self.current_frame, text="🌍 Loading weather data...", 
                                font=('Arial', 18), 
                                fg='#ecf0f1', bg='#34495e')
        loading_label.pack(pady=50)
    
    def on_search(self, event):
        """Handle Enter key press in search entry"""
        self.search_weather()
    
    def search_weather(self):
        """Search weather for entered location"""
        location = self.location_entry.get().strip()
        if location:
            self.show_loading()
            threading.Thread(target=self.get_weather_by_location, 
                           args=(location,), daemon=True).start()
        else:
            messagebox.showwarning("Input Error", "Please enter a location name")
    
    def get_current_location(self):
        """Get weather for current location using IP geolocation"""
        self.show_loading()
        self.status_bar.config(text="Getting current location...")
        threading.Thread(target=self._get_current_location, daemon=True).start()
    
    def _get_current_location(self):
        """Get current location using IP geolocation"""
        try:
            # Use a geolocation API to get current location
            response = requests.get("http://ip-api.com/json/", timeout=10)
            data = response.json()
            
            if data['status'] == 'success':
                lat, lon = data['lat'], data['lon']
                city = data['city']
                country = data['country']
                
                self.root.after(0, lambda: self.status_bar.config(
                    text=f"Location detected: {city}, {country}"))
                
                self.get_weather_by_coordinates(lat, lon)
            else:
                raise Exception("Location detection failed")
                
        except Exception as e:
            self.root.after(0, lambda: self.handle_error(f"Location detection failed: {str(e)}"))
    
    def get_weather_by_location(self, location):
        """Get weather data for a specific location"""
        try:
            self.status_bar.config(text=f"Fetching weather for {location}...")
            
            # Get current weather
            current_url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': self.temp_unit.get()
            }
            
            response = requests.get(current_url, params=params, timeout=10)
            
            if response.status_code == 401:
                self.handle_error("Invalid API key. Please get a valid key from OpenWeatherMap.")
                return
            elif response.status_code == 404:
                self.handle_error(f"Location '{location}' not found.")
                return
            elif response.status_code != 200:
                self.handle_error(f"Error fetching weather data: {response.status_code}")
                return
            
            current_data = response.json()
            
            # Get forecast data
            forecast_url = f"{self.base_url}/forecast"
            forecast_response = requests.get(forecast_url, params=params, timeout=10)
            forecast_data = forecast_response.json() if forecast_response.status_code == 200 else None
            
            # Update UI in main thread
            self.root.after(0, lambda: self.display_weather(current_data, forecast_data))
            self.root.after(0, lambda: self.status_bar.config(text="Weather data loaded successfully"))
            
        except requests.exceptions.Timeout:
            self.root.after(0, lambda: self.handle_error("Request timeout. Please try again."))
        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: self.handle_error("Connection error. Please check your internet connection."))
        except Exception as e:
            self.root.after(0, lambda: self.handle_error(f"Error: {str(e)}"))
    
    def get_weather_by_coordinates(self, lat, lon):
        """Get weather data for specific coordinates"""
        try:
            # Get current weather
            current_url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': self.temp_unit.get()
            }
            
            response = requests.get(current_url, params=params, timeout=10)
            
            if response.status_code != 200:
                self.handle_error(f"Error fetching weather data: {response.status_code}")
                return
            
            current_data = response.json()
            
            # Get forecast data
            forecast_url = f"{self.base_url}/forecast"
            forecast_response = requests.get(forecast_url, params=params, timeout=10)
            forecast_data = forecast_response.json() if forecast_response.status_code == 200 else None
            
            # Update UI in main thread
            self.root.after(0, lambda: self.display_weather(current_data, forecast_data))
            
        except Exception as e:
            self.root.after(0, lambda: self.handle_error(f"Error: {str(e)}"))
    
    def display_weather(self, current_data, forecast_data):
        """Display weather data in the GUI"""
        # Clear previous data
        for widget in self.current_frame.winfo_children():
            widget.destroy()
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()
        
        # Current weather display
        self.display_current_weather(current_data)
        
        # Forecast display
        if forecast_data:
            self.display_forecast(forecast_data)
    
    def display_current_weather(self, data):
        """Display current weather information"""
        # Location and time
        location = f"{data['name']}, {data['sys']['country']}"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        location_label = tk.Label(self.current_frame, text=location, 
                                 font=('Arial', 15, 'bold'), 
                                 fg='#ecf0f1', bg='#34495e')
        location_label.pack(pady=(0, 5))
        
        time_label = tk.Label(self.current_frame, text=current_time, 
                             font=('Arial', 12), 
                             fg='#bdc3c7', bg='#34495e')
        time_label.pack(pady=(0, 20))
        
        # Main weather info frame
        main_info_frame = tk.Frame(self.current_frame, bg='#34495e')
        main_info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Weather icon and temperature
        left_frame = tk.Frame(main_info_frame, bg='#34495e')
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Weather icon (using emoji as placeholder)
        emoji_font = ('Segoe UI Emoji', 60)
        weather_emoji = self.get_weather_emoji(data['weather'][0]['icon'])
        icon_label = tk.Label(left_frame, text=weather_emoji, 
                             font=('Segoe UI Emoji', 60), bg='#34495e')
        icon_label.pack(pady=(0, 10))
        
        # Temperature
        temp = data['main']['temp']
        unit_symbol = '°C' if self.temp_unit.get() == 'metric' else '°F'
        temp_label = tk.Label(left_frame, text=f"{temp:.1f}{unit_symbol}", 
                             font=('Arial', 32, 'bold'), 
                             fg='#e74c3c', bg='#34495e')
        temp_label.pack()
        
        # Weather description
        desc = data['weather'][0]['description'].title()
        desc_label = tk.Label(left_frame, text=desc, 
                             font=('Arial', 14), 
                             fg='#ecf0f1', bg='#34495e')
        desc_label.pack(pady=(5, 0))
        
        # Weather details
        right_frame = tk.Frame(main_info_frame, bg='#34495e')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(40, 0))
        
        # Details grid
        details = [
            ("Feels Like", f"{data['main']['feels_like']:.1f}{unit_symbol}"),
            ("Humidity", f"{data['main']['humidity']}%"),
            ("Pressure", f"{data['main']['pressure']} hPa"),
            ("Wind Speed", f"{data['wind']['speed']} {'m/s' if self.temp_unit.get() == 'metric' else 'mph'}"),
            ("Wind Direction", f"{data['wind'].get('deg', 'N/A')}°"),
            ("Visibility", f"{data.get('visibility', 'N/A')} m" if data.get('visibility') else "N/A"),
            ("Sunrise", datetime.fromtimestamp(data['sys']['sunrise']).strftime("%H:%M")),
            ("Sunset", datetime.fromtimestamp(data['sys']['sunset']).strftime("%H:%M"))
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = i % 2
            
            detail_frame = tk.Frame(right_frame, bg='#2c3e50', relief=tk.RAISED, bd=1)
            detail_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            tk.Label(detail_frame, text=label, font=('Arial', 10, 'bold'), 
                    fg='#bdc3c7', bg='#2c3e50').pack(anchor='w', padx=8, pady=(5, 0))
            tk.Label(detail_frame, text=value, font=('Arial', 12), 
                    fg='#ecf0f1', bg='#2c3e50').pack(anchor='w', padx=8, pady=(0, 5))
        
        # Configure grid weights
        for i in range(2):
            right_frame.columnconfigure(i, weight=1)
    
    def display_forecast(self, data):
        """Display 5-day forecast"""
        # Forecast title
        forecast_title = tk.Label(self.forecast_frame, text="5-Day Forecast", 
                                 font=('Arial', 15, 'bold'), 
                                 fg='#ecf0f1', bg='#34495e')
        forecast_title.pack(pady=(0, 10))
        
        # Forecast container
        forecast_container = tk.Frame(self.forecast_frame, bg='#34495e')
        forecast_container.pack(fill=tk.BOTH, expand=True)
        
        # Process forecast data (group by day)
        daily_forecasts = {}
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).date()
            if date not in daily_forecasts:
                daily_forecasts[date] = []
            daily_forecasts[date].append(item)
        
        # Display first 5 days
        unit_symbol = '°C' if self.temp_unit.get() == 'metric' else '°F'
        for i, (date, day_data) in enumerate(list(daily_forecasts.items())[:5]):
            # Get representative data for the day (midday if available)
            day_weather = day_data[len(day_data)//2]  # Middle of the day
            
            # Day frame
            day_frame = tk.Frame(forecast_container, bg='#2c3e50', relief=tk.RAISED, bd=1)
            day_frame.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            
            # Day name
            day_name = date.strftime("%a")
            if date == datetime.now().date():
                day_name = "Today"
            elif date == datetime.now().date() + timedelta(days=1):
                day_name = "Tomorrow"
            
            day_label = tk.Label(day_frame, text=day_name, font=('Arial', 12, 'bold'), 
                               fg='#ecf0f1', bg='#2c3e50')
            day_label.pack(pady=(10, 5))
            
            # Weather icon
            weather_emoji = self.get_weather_emoji(day_weather['weather'][0]['icon'])
            icon_label = tk.Label(day_frame, text=weather_emoji, 
                                 font=('Segoe UI Emoji', 30), bg='#2c3e50')
            icon_label.pack(pady=5)
            
            # Temperature range
            temps = [item['main']['temp'] for item in day_data]
            min_temp = min(temps)
            max_temp = max(temps)
            
            temp_label = tk.Label(day_frame, 
                                 text=f"{max_temp:.0f}°/{min_temp:.0f}°", 
                                 font=('Arial', 11, 'bold'), 
                                 fg='#e74c3c', bg='#2c3e50')
            temp_label.pack(pady=5)
            
            # Weather description
            desc = day_weather['weather'][0]['description'].title()
            desc_label = tk.Label(day_frame, text=desc, 
                                 font=('Arial', 9), 
                                 fg='#bdc3c7', bg='#2c3e50',
                                 wraplength=100)
            desc_label.pack(pady=(0, 10))
        
        # Configure grid weights
        for i in range(5):
            forecast_container.columnconfigure(i, weight=1)
    
    def get_weather_emoji(self, icon_code):
        """Get weather emoji based on icon code"""
        emoji_map = {
            '01d': '☀️', '01n': '🌙',  # clear sky
            '02d': '⛅', '02n': '☁️',  # few clouds
            '03d': '☁️', '03n': '☁️',  # scattered clouds
            '04d': '☁️', '04n': '☁️',  # broken clouds
            '09d': '🌧️', '09n': '🌧️',  # shower rain
            '10d': '🌦️', '10n': '🌧️',  # rain
            '11d': '⛈️', '11n': '⛈️',  # thunderstorm
            '13d': '❄️', '13n': '❄️',  # snow
            '50d': '🌫️', '50n': '🌫️',  # mist
        }
        return emoji_map.get(icon_code, '🌤️')
    
    def refresh_weather(self):
        """Refresh weather data with new units"""
        location = self.location_entry.get().strip()
        if location:
            self.show_loading()
            threading.Thread(target=self.get_weather_by_location, 
                           args=(location,), daemon=True).start()
    
    def handle_error(self, message):
        """Handle and display errors"""
        # Clear weather display
        for widget in self.current_frame.winfo_children():
            widget.destroy()
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()
        
        # Show error message
        error_label = tk.Label(self.current_frame, text="❌ Error", 
                              font=('Arial', 24, 'bold'), 
                              fg='#e74c3c', bg='#34495e')
        error_label.pack(pady=(50, 10))
        
        msg_label = tk.Label(self.current_frame, text=message, 
                            font=('Arial', 12), 
                            fg='#ecf0f1', bg='#34495e',
                            wraplength=400)
        msg_label.pack(pady=(0, 20))
        
        # API key help
        if "API key" in message:
            help_label = tk.Label(self.current_frame, 
                                 text="Get your free API key from:\nhttps://openweathermap.org/api", 
                                 font=('Arial', 10), 
                                 fg='#3498db', bg='#34495e')
            help_label.pack()
        
        self.status_bar.config(text="Error occurred")

def main():
    root = tk.Tk()
    app = WeatherApp(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()