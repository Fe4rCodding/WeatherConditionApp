import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import random 

class AdvancedWeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Data Analysis - Pro UI")
        self.root.geometry("1000x850") 
        
        self.theme = "dark"
        self.colors = {}
        self.last_graph_data = ([], []) 
        
        self.api_key = "cfd93bd25c18114a13f4dd3c8f7f531f" 
        self.base_url = "http://api.openweathermap.org/data/2.5/"
        
        self.weather_tr = {"Clear": "Güneşli", "Clouds": "Bulutlu", "Rain": "Yağmurlu", "Drizzle": "Çisenti", "Snow": "Karlı", "Mist": "Sisli", "Thunderstorm": "Fırtına"}
        self.days_tr = {"Monday": "Pzt", "Tuesday": "Sal", "Wednesday": "Çar", "Thursday": "Per", "Friday": "Cum", "Saturday": "Cmt", "Sunday": "Paz"}
        self.countries_tr = {
            "TR": "Türkiye", "US": "ABD", "GB": "İngiltere", "DE": "Almanya", 
            "FR": "Fransa", "IT": "İtalya", "ES": "İspanya", "RU": "Rusya", 
            "JP": "Japonya", "CN": "Çin", "IN": "Hindistan", "BR": "Brezilya", 
            "CA": "Kanada", "AU": "Avustralya", "NL": "Hollanda", "GR": "Yunanistan",
            "AZ": "Azerbaycan", "UA": "Ukrayna", "SA": "Suudi Arabistan", "EG": "Mısır"
        }

        self.anim_elements = []
        self.current_weather_type = None
        self.search_history = []

        self.set_colors()
        self.setup_ui()
        self.update_clock() 
        self.animation_loop() 
        
        self.auto_locate()
        
    def auto_locate(self):
        try:
            loc_resp = requests.get("https://ipapi.co/json/", timeout=5)
            loc_data = loc_resp.json()
            city = loc_data.get("city", "Konya")
            self.city_entry.set(city)
        except:
            self.city_entry.set("Konya")
        self.fetch_weather_data()

    def set_colors(self):
        if self.theme == "dark":
            self.colors = {"bg": "#202124", "fg": "white", "input": "#303134", "text_sec": "#9aa0a6", "graph": "#8ab4f8", "btn": "#303134"}
        else:
            self.colors = {"bg": "#ffffff", "fg": "#202124", "input": "#f1f3f4", "text_sec": "#5f6368", "graph": "#fbbc04", "btn": "#e8eaed"}
        self.root.configure(bg=self.colors["bg"])

    def toggle_theme(self, mode):
        self.theme = mode
        self.set_colors()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
        if self.last_graph_data[0]:
            self.draw_modern_graph(*self.last_graph_data)
        self.trigger_animation(self.current_weather_type) 
    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        try:
            if hasattr(self, 'clock_label') and self.clock_label.winfo_exists():
                self.clock_label.config(text=now)
        except: pass
        self.root.after(1000, self.update_clock) 
        

    def get_activity_advice(self, condition):
        advice = {
            "Clear": "☀️ Hava harika! Futbol oynamak veya yürüyüş için çok güzel bir gün.",
            "Clouds": "☁️ Hava biraz kapalı. Bisiklete binmek veya sakin bir yürüyüş için ideal.",
            "Rain": "🌧️ Yağmur yağıyor, şemsiyeni unutma! Kahve keyfi için harika bir hava.",
            "Thunderstorm": "⛈️ Dışarıda fırtına var! Evde sıcak ve güvende kalmak en iyisi.",
            "Snow": "❄️ Kar yağıyor! Sıkı giyinip karın tadını çıkarabilirsin."
        }
        return advice.get(condition, "Hava değişken olabilir, tedbiri elden bırakma.")

    def setup_ui(self):
        theme_frame = tk.Frame(self.root, bg=self.colors["bg"])
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.clock_label = tk.Label(theme_frame, text="00:00:00", font=("Segoe UI", 12, "bold"), bg=self.colors["bg"], fg=self.colors["text_sec"])
        self.clock_label.pack(side=tk.LEFT, padx=5)

        tk.Button(theme_frame, text="🌙 Koyu", command=lambda: self.toggle_theme("dark"), bg=self.colors["btn"], fg=self.colors["fg"], relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)
        tk.Button(theme_frame, text="☀️ Açık", command=lambda: self.toggle_theme("light"), bg=self.colors["btn"], fg=self.colors["fg"], relief=tk.FLAT).pack(side=tk.RIGHT)

        top_frame = tk.Frame(self.root, bg=self.colors["bg"], pady=10)
        top_frame.pack()
        
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except: pass
        style.configure('TCombobox', fieldbackground=self.colors["input"], background=self.colors["btn"], foreground=self.colors["fg"])
        
        self.city_entry = ttk.Combobox(top_frame, font=("Segoe UI", 12), width=23, style='TCombobox')
        self.city_entry.pack(side=tk.LEFT, padx=10, ipady=5)
        self.city_entry.bind('<Return>', lambda event: self.fetch_weather_data())
        self.city_entry.bind('<<ComboboxSelected>>', lambda event: self.fetch_weather_data())
        
        tk.Button(top_frame, text="Ara", command=self.fetch_weather_data, bg="#8ab4f8", fg="#202124", font=("Segoe UI", 10, "bold"), relief=tk.FLAT).pack(side=tk.LEFT)

        self.current_frame = tk.Frame(self.root, bg=self.colors["bg"], pady=5)
        self.current_frame.pack(fill=tk.X)

        self.city_label = tk.Label(self.current_frame, text="Şehir Aranıyor...", font=("Segoe UI", 24, "bold"), bg=self.colors["bg"], fg=self.colors["fg"])
        self.city_label.pack()

        self.country_label = tk.Label(self.current_frame, text="", font=("Segoe UI", 14), bg=self.colors["bg"], fg=self.colors["text_sec"])
        self.country_label.pack()

        # Dinamik Canvas
        self.anim_canvas = tk.Canvas(self.current_frame, height=120, bg=self.colors["bg"], highlightthickness=0)
        self.anim_canvas.pack(fill=tk.X)

        self.temp_label = tk.Label(self.current_frame, text="--°C", font=("Segoe UI", 48, "bold"), bg=self.colors["bg"], fg=self.colors["fg"])
        self.temp_label.pack()

        self.desc_label = tk.Label(self.current_frame, text="", font=("Segoe UI", 14), bg=self.colors["bg"], fg=self.colors["text_sec"])
        self.desc_label.pack()

        self.details_frame = tk.Frame(self.current_frame, bg=self.colors["bg"], pady=10)
        self.details_frame.pack()
        
        self.feels_label = tk.Label(self.details_frame, text="", font=("Segoe UI", 11), bg=self.colors["bg"], fg=self.colors["text_sec"])
        self.feels_label.pack(side=tk.LEFT, padx=15)
        
        self.wind_label = tk.Label(self.details_frame, text="", font=("Segoe UI", 11), bg=self.colors["bg"], fg=self.colors["text_sec"])
        self.wind_label.pack(side=tk.LEFT, padx=15)
        
        self.pressure_label = tk.Label(self.details_frame, text="", font=("Segoe UI", 11), bg=self.colors["bg"], fg=self.colors["text_sec"])
        self.pressure_label.pack(side=tk.LEFT, padx=15)

        self.activity_label = tk.Label(self.current_frame, text="", font=("Segoe UI", 11, "italic"), bg=self.colors["bg"], fg=self.colors["graph"], wraplength=700)
        self.activity_label.pack(pady=5)

        self.weekly_frame = tk.Frame(self.root, bg=self.colors["bg"], pady=5)
        self.weekly_frame.pack()

        self.graph_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def trigger_animation(self, weather_type):
        if not weather_type: return
        self.current_weather_type = weather_type
        self.anim_canvas.delete("all")
        self.anim_elements = []
        width = self.anim_canvas.winfo_width() if self.anim_canvas.winfo_width() > 1 else 1000

        if weather_type in ["Rain", "Drizzle", "Thunderstorm"]:
            for _ in range(50):
                x = random.randint(0, width)
                y = random.randint(-100, 120)
                speed = random.randint(4, 8)
                line = self.anim_canvas.create_line(x, y, x, y+15, fill="#8ab4f8", width=2)
                self.anim_elements.append({"id": line, "speed": speed, "type": "rain"})
        
        elif weather_type == "Snow":
            for _ in range(60):
                x = random.randint(0, width)
                y = random.randint(-100, 120)
                speed = random.uniform(1, 3)
                flake = self.anim_canvas.create_text(x, y, text="❄", fill="white", font=("Segoe UI", random.randint(8, 14)))
                self.anim_elements.append({"id": flake, "speed": speed, "type": "snow", "drift": random.uniform(-1, 1)})
                
        elif weather_type == "Mist" or weather_type == "Fog":
            for _ in range(5):
                x = random.randint(-100, width)
                y = random.randint(20, 100)
                fog = self.anim_canvas.create_oval(x, y, x+300, y+40, fill="#5f6368", outline="", stipple="gray50")
                self.anim_elements.append({"id": fog, "speed": random.uniform(0.2, 0.8), "type": "fog"})
        
        elif weather_type == "Clear":
            # Gelişmiş Güneş
            sun = self.anim_canvas.create_oval(width//2-40, 10, width//2+40, 90, fill="#fbbc04", outline="")
            self.anim_elements.append({"id": sun, "type": "sun", "x": width//2})
            
        elif weather_type == "Clouds":
            # Pofuduk Bulut Tasarımı (3'lü daire grubu)
            for _ in range(4):
                x = random.randint(0, width)
                y = random.randint(20, 50)
                
                c1 = self.anim_canvas.create_oval(x, y, x+60, y+40, fill="#5f6368", outline="")
                c2 = self.anim_canvas.create_oval(x+30, y-10, x+90, y+30, fill="#5f6368", outline="")
                c3 = self.anim_canvas.create_oval(x+50, y, x+110, y+40, fill="#5f6368", outline="")
                self.anim_elements.append({"ids": [c1, c2, c3], "speed": random.uniform(0.7, 1.8), "type": "cloud"})

    def animation_loop(self):
        width = self.anim_canvas.winfo_width()
        if width <= 1: width = 1000

        for item in self.anim_elements:
            if item["type"] == "rain":
                self.anim_canvas.move(item["id"], 0, item["speed"])
                pos = self.anim_canvas.coords(item["id"])
                if pos[1] > 120: 
                    self.anim_canvas.coords(item["id"], pos[0], -20, pos[0], -5)
            
            elif item["type"] == "cloud":
                for cloud_id in item["ids"]:
                    self.anim_canvas.move(cloud_id, item["speed"], 0)
                
                # Sınır kontrolü (Bulutun ilk parçasının pozisyonuna bakıyoruz)
                pos = self.anim_canvas.coords(item["ids"][0])
                if pos[0] > width: 
                    # Ekran dışına çıkınca en sola ışınla
                    dist = width + 150
                    for cloud_id in item["ids"]:
                        self.anim_canvas.move(cloud_id, -dist, 0)
                        
            elif item["type"] == "snow":
                self.anim_canvas.move(item["id"], item["drift"], item["speed"])
                pos = self.anim_canvas.coords(item["id"])
                if pos[1] > 120: 
                    self.anim_canvas.coords(item["id"], pos[0], -20)
            
            elif item["type"] == "fog":
                self.anim_canvas.move(item["id"], item["speed"], 0)
                pos = self.anim_canvas.coords(item["id"])
                if pos[0] > width:
                    self.anim_canvas.move(item["id"], -width-300, 0)
                    
        self.root.after(30, self.animation_loop) 

    def fetch_weather_data(self):
        city = self.city_entry.get().strip()
        if not city: return
        
        try:
            c_resp = requests.get(f"{self.base_url}weather?q={city}&appid={self.api_key}&units=metric", timeout=5)
            c_data = c_resp.json()

            if c_data.get("cod") != 200:
                messagebox.showerror("Hata", f"Şehir bulunamadı: {city.capitalize()}")
                return

            if city not in self.search_history:
                self.search_history.insert(0, city)
                if len(self.search_history) > 5:
                    self.search_history.pop()
                self.city_entry['values'] = self.search_history

            real_city_name = c_data["name"].replace(" Province", "").replace(" İli", "")
            country_code = c_data.get("sys", {}).get("country", "")
            country_name = self.countries_tr.get(country_code, country_code)
            current_temp = int(c_data["main"]["temp"])
            feels_like = int(c_data["main"]["feels_like"])
            pressure = c_data["main"]["pressure"]
            wind_speed = c_data["wind"]["speed"]
            cond_eng = c_data["weather"][0]["main"]
            cond_tr = self.weather_tr.get(cond_eng, cond_eng) 

            self.city_label.config(text=real_city_name.upper())
            self.country_label.config(text=f"{country_name}" if country_name else "")
            self.temp_label.config(text=f"{current_temp}°C")
            self.desc_label.config(text=f"{cond_tr} (Nem: %{c_data['main']['humidity']})")
            
            self.feels_label.config(text=f"🌡️ Hissedilen: {feels_like}°C")
            self.wind_label.config(text=f"💨 Rüzgar: {wind_speed} m/s")
            self.pressure_label.config(text=f"🧭 Basınç: {pressure} hPa")
            
            self.activity_label.config(text=self.get_activity_advice(cond_eng))
            self.trigger_animation(cond_eng)

            f_resp = requests.get(f"{self.base_url}forecast?q={city}&appid={self.api_key}&units=metric", timeout=5)
            f_data = f_resp.json()

            for widget in self.weekly_frame.winfo_children(): widget.destroy()
            
            daily_forecasts = []
            seen_dates = set()
            today_date = datetime.now().date()

            for item in f_data["list"]:
                dt = datetime.fromtimestamp(item["dt"])
                date_str = dt.strftime("%d.%m")
                
                if dt.date() > today_date and date_str not in seen_dates:
                    seen_dates.add(date_str)
                    daily_forecasts.append(item)
                    # Cumartesi ve sonrasını yakalamak için limiti 6 yaptık
                    if len(daily_forecasts) == 6: break 

            for item in daily_forecasts:
                dt = datetime.fromtimestamp(item["dt"])
                day_tr = self.days_tr.get(dt.strftime("%A"), dt.strftime("%A"))
                
                day_box = tk.Frame(self.weekly_frame, bg=self.colors["input"], padx=12, pady=10)
                day_box.pack(side=tk.LEFT, padx=5)
                
                tk.Label(day_box, text=day_tr, font=("Segoe UI", 12, "bold"), bg=self.colors["input"], fg=self.colors["fg"]).pack()
                tk.Label(day_box, text=dt.strftime("%d.%m"), font=("Segoe UI", 9), bg=self.colors["input"], fg=self.colors["text_sec"]).pack()
                tk.Label(day_box, text=self.weather_tr.get(item["weather"][0]["main"], item["weather"][0]["main"]), font=("Segoe UI", 10), bg=self.colors["input"], fg=self.colors["text_sec"]).pack()
                tk.Label(day_box, text=f"{int(item['main']['temp'])}°C", font=("Segoe UI", 14), bg=self.colors["input"], fg=self.colors["fg"]).pack()

            times, temps = [], []
            for item in f_data["list"][:8]: 
                times.append(datetime.fromtimestamp(item["dt"]).strftime("%H:%M"))
                temps.append(int(item["main"]["temp"]))
            
            self.last_graph_data = (times, temps) 
            self.draw_modern_graph(times, temps)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Bağlantı Hatası", "Lütfen internet bağlantınızı kontrol edin.\nDetay: " + str(e))
        except Exception as e:
            messagebox.showerror("Hata", "Beklenmeyen bir hata oluştu:\n" + str(e))

    def draw_modern_graph(self, times, temps):
        for widget in self.graph_frame.winfo_children(): widget.destroy()
        fig, ax = plt.subplots(figsize=(8, 3), facecolor=self.colors["bg"])
        ax.set_facecolor(self.colors["bg"])
        ax.plot(times, temps, color=self.colors["graph"], linewidth=3, marker='o')
        ax.fill_between(times, temps, min(temps)-2, color=self.colors["graph"], alpha=0.3)
        for s in ['top', 'right', 'left', 'bottom']: ax.spines[s].set_visible(False)
        ax.tick_params(axis='both', colors=self.colors["fg"], labelsize=8)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedWeatherApp(root)
    root.mainloop()