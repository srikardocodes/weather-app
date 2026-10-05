import os
import tkinter as tk
from tkinter import ttk
from io import BytesIO
from datetime import datetime

import requests
from PIL import Image, ImageTk




API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5"

ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"




def get_current_weather(city):
    

    url = f"{BASE_URL}/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code == 401:
        raise ValueError("Invalid API key.")

    if response.status_code == 404:
        raise ValueError("City not found.")

    if response.status_code == 429:
        raise ValueError("API rate limit exceeded. Try again later.")

    response.raise_for_status()

    return response.json()


def get_forecast(city):
   

    url = f"{BASE_URL}/forecast"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code == 401:
        raise ValueError("Invalid API key.")

    if response.status_code == 404:
        raise ValueError("City not found.")

    if response.status_code == 429:
        raise ValueError("API rate limit exceeded. Try again later.")

    response.raise_for_status()

    return response.json()


def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32



def download_icon(icon_code, size=(70, 70)):
    

    try:
        url = ICON_URL.format(icon_code)

        response = requests.get(url, timeout=5)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        image = image.resize(size, Image.Resampling.LANCZOS)

        return ImageTk.PhotoImage(image)

    except requests.RequestException:
        return None

class WeatherApp:

    def __init__(self, root):

        self.root = root

        self.root.title("Real-Time Weather App")
        self.root.geometry("900x750")
        self.root.resizable(False, False)

        self.root.configure(bg="#0f172a")

        self.current_weather = None
        self.forecast_data = None

        self.unit = "C"

        self.icon_references = []

        self.create_styles()
        self.create_widgets()

   

    def create_styles(self):

        self.style = ttk.Style()

        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure(
            "TFrame",
            background="#0f172a"
        )

        self.style.configure(
            "Card.TFrame",
            background="#1e293b"
        )

        self.style.configure(
            "TLabel",
            background="#0f172a",
            foreground="white",
            font=("Arial", 11)
        )

        self.style.configure(
            "Card.TLabel",
            background="#1e293b",
            foreground="white",
            font=("Arial", 11)
        )

        self.style.configure(
            "Title.TLabel",
            background="#0f172a",
            foreground="white",
            font=("Arial", 26, "bold")
        )

        self.style.configure(
            "Temperature.TLabel",
            background="#1e293b",
            foreground="white",
            font=("Arial", 38, "bold")
        )

        self.style.configure(
            "Condition.TLabel",
            background="#1e293b",
            foreground="#cbd5e1",
            font=("Arial", 15)
        )

        self.style.configure(
            "TButton",
            font=("Arial", 10, "bold"),
            padding=8
        )

    def create_widgets(self):

        main_frame = ttk.Frame(
            self.root,
            padding=25
        )

        main_frame.pack(
            fill="both",
            expand=True
        )

        

        title = ttk.Label(
            main_frame,
            text="🌤️ Real-Time Weather",
            style="Title.TLabel"
        )

        title.pack(pady=(0, 20))

        

        search_frame = tk.Frame(
            main_frame,
            bg="#0f172a"
        )

        search_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        self.city_entry = tk.Entry(
            search_frame,
            font=("Arial", 14),
            bg="#1e293b",
            fg="white",
            insertbackground="white",
            relief="flat"
        )

        self.city_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=10,
            padx=(0, 10)
        )

        self.city_entry.insert(
            0,
            "Enter city name..."
        )

        self.city_entry.bind(
            "<FocusIn>",
            self.clear_placeholder
        )

        self.city_entry.bind(
            "<Return>",
            lambda event: self.get_weather()
        )

        search_button = ttk.Button(
            search_frame,
            text="Get Weather",
            command=self.get_weather
        )

        search_button.pack(
            side="right"
        )

        

        unit_frame = tk.Frame(
            main_frame,
            bg="#0f172a"
        )

        unit_frame.pack(
            pady=(0, 10)
        )

        ttk.Label(
            unit_frame,
            text="Temperature Unit:"
        ).pack(side="left", padx=5)

        self.unit_button = ttk.Button(
            unit_frame,
            text="°C",
            command=self.toggle_unit
        )

        self.unit_button.pack(side="left")

        self.error_label = tk.Label(
            main_frame,
            text="",
            bg="#0f172a",
            fg="#f87171",
            font=("Arial", 11, "bold")
        )

        self.error_label.pack()

        

        self.current_card = tk.Frame(
            main_frame,
            bg="#1e293b"
        )

        self.current_card.pack(
            fill="x",
            pady=10
        )

        self.location_label = tk.Label(
            self.current_card,
            text="Search for a city",
            bg="#1e293b",
            fg="white",
            font=("Arial", 20, "bold")
        )

        self.location_label.pack(pady=(15, 5))

        self.icon_label = tk.Label(
            self.current_card,
            bg="#1e293b"
        )

        self.icon_label.pack()

        self.temperature_label = tk.Label(
            self.current_card,
            text="--°",
            bg="#1e293b",
            fg="white",
            font=("Arial", 42, "bold")
        )

        self.temperature_label.pack()

        self.condition_label = tk.Label(
            self.current_card,
            text="",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Arial", 15)
        )

        self.condition_label.pack()

        self.details_label = tk.Label(
            self.current_card,
            text="",
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Arial", 11),
            justify="center"
        )

        self.details_label.pack(
            pady=(10, 20)
        )

       

        hourly_title = tk.Label(
            main_frame,
            text="Next 6 Hours",
            bg="#0f172a",
            fg="white",
            font=("Arial", 16, "bold")
        )

        hourly_title.pack(
            anchor="w",
            pady=(15, 5)
        )

        self.hourly_frame = tk.Frame(
            main_frame,
            bg="#0f172a"
        )

        self.hourly_frame.pack(
            fill="x"
        )

        
        daily_title = tk.Label(
            main_frame,
            text="5-Day Forecast",
            bg="#0f172a",
            fg="white",
            font=("Arial", 16, "bold")
        )

        daily_title.pack(
            anchor="w",
            pady=(15, 5)
        )

        self.daily_frame = tk.Frame(
            main_frame,
            bg="#0f172a"
        )

        self.daily_frame.pack(
            fill="x"
        )

    
    def clear_placeholder(self, event):

        if self.city_entry.get() == "Enter city name...":
            self.city_entry.delete(0, tk.END)

    def get_weather(self):

        city = self.city_entry.get().strip()

        if not city or city == "Enter city name...":

            self.show_error(
                "Please enter a city name."
            )

            return

        if not API_KEY:

            self.show_error(
                "OpenWeatherMap API key is not configured."
            )

            return

        self.error_label.config(text="")

        try:

            self.current_weather = get_current_weather(city)

            self.forecast_data = get_forecast(city)

            self.display_current_weather()
            self.display_hourly_forecast()
            self.display_daily_forecast()

        except requests.exceptions.Timeout:

            self.show_error(
                "Request timed out. Please try again."
            )

        except requests.exceptions.ConnectionError:

            self.show_error(
                "Unable to connect to the weather service."
            )

        except requests.exceptions.RequestException:

            self.show_error(
                "Unable to retrieve weather information."
            )

        except ValueError as error:

            self.show_error(str(error))

    def display_current_weather(self):

        data = self.current_weather

        city = data["name"]
        country = data["sys"]["country"]

        temperature = data["main"]["temp"]

        humidity = data["main"]["humidity"]

        wind_speed = data["wind"]["speed"]

        condition = data["weather"][0]["main"]
        description = data["weather"][0]["description"]

        icon_code = data["weather"][0]["icon"]

        self.location_label.config(
            text=f"{city}, {country}"
        )

        self.condition_label.config(
            text=description.title()
        )

        self.update_temperature(
            temperature
        )

        self.details_label.config(
            text=(
                f" Humidity: {humidity}%  "
                f"Wind: {wind_speed} m/s\n"
                f"Condition: {condition}"
            )
        )

        icon = download_icon(
            icon_code,
            size=(100, 100)
        )

        if icon:

            self.icon_references.append(icon)

            self.icon_label.config(
                image=icon
            )

    def update_temperature(self, celsius):

        if self.unit == "C":

            temperature = celsius

            text = f"{temperature:.1f}°C"

        else:

            temperature = celsius_to_fahrenheit(
                celsius
            )

            text = f"{temperature:.1f}°F"

        self.temperature_label.config(
            text=text
        )

   

    def toggle_unit(self):

        if self.unit == "C":

            self.unit = "F"

            self.unit_button.config(
                text="°F"
            )

        else:

            self.unit = "C"

            self.unit_button.config(
                text="°C"
            )

        if self.current_weather:

            temperature = self.current_weather[
                "main"
            ]["temp"]

            self.update_temperature(
                temperature
            )

        self.display_hourly_forecast()
        self.display_daily_forecast()

    
    def display_hourly_forecast(self):

        for widget in self.hourly_frame.winfo_children():
            widget.destroy()

        self.icon_references.clear()

        if not self.forecast_data:
            return

        forecast_list = self.forecast_data["list"]

        
        next_hours = forecast_list[:2]

        for item in next_hours:

            self.create_forecast_card(
                self.hourly_frame,
                item,
                hourly=True
            )

    def display_daily_forecast(self):

        for widget in self.daily_frame.winfo_children():
            widget.destroy()

        if not self.forecast_data:
            return

        forecast_list = self.forecast_data["list"]

        daily_data = {}

        for item in forecast_list:

            date = item["dt_txt"].split(" ")[0]

            if date not in daily_data:
                daily_data[date] = item

        days = list(daily_data.values())[:5]

        for item in days:

            self.create_forecast_card(
                self.daily_frame,
                item,
                hourly=False
            )

   
    def create_forecast_card(
        self,
        parent,
        item,
        hourly=False
    ):

        card = tk.Frame(
            parent,
            bg="#1e293b",
            width=160,
            height=130
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=4
        )

        card.pack_propagate(False)

        date_text = datetime.fromtimestamp(
            item["dt"]
        )

        if hourly:

            time_text = date_text.strftime(
                "%H:%M"
            )

        else:

            time_text = date_text.strftime(
                "%a"
            )

        time_label = tk.Label(
            card,
            text=time_text,
            bg="#1e293b",
            fg="white",
            font=("Arial", 10, "bold")
        )

        time_label.pack(
            pady=(8, 0)
        )

        icon_code = item["weather"][0]["icon"]

        icon = download_icon(
            icon_code,
            size=(50, 50)
        )

        if icon:

            self.icon_references.append(icon)

            icon_label = tk.Label(
                card,
                image=icon,
                bg="#1e293b"
            )

            icon_label.pack()

        temperature = item["main"]["temp"]

        if self.unit == "F":

            temperature = celsius_to_fahrenheit(
                temperature
            )

            temp_text = f"{temperature:.1f}°F"

        else:

            temp_text = f"{temperature:.1f}°C"

        temp_label = tk.Label(
            card,
            text=temp_text,
            bg="#1e293b",
            fg="white",
            font=("Arial", 12, "bold")
        )

        temp_label.pack()

        condition = item["weather"][0]["main"]

        condition_label = tk.Label(
            card,
            text=condition,
            bg="#1e293b",
            fg="#cbd5e1",
            font=("Arial", 9)
        )

        condition_label.pack()

    def show_error(self, message):

        self.error_label.config(
            text=f"⚠ {message}"
        )

if __name__ == "__main__":

    root = tk.Tk()

    app = WeatherApp(root)

    root.mainloop()
