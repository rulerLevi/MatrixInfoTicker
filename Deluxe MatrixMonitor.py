import tkinter as tk
import psutil
import random
import threading
import time
import subprocess
import webbrowser
import requests
import xml.etree.ElementTree as ET

# --- NewsAPI-Konfiguration ---
NEWS_API_KEY = "ApI"  # Bitte hier deinen API-Key eintragen!
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"

# RSS-Feed URL als zweite Quelle (z.B. Tagesschau)
RSS_FEED_URL = "https://www.tagesschau.de/xml/rss2/"

# Zeichen, die in der Matrix herunterrieseln sollen
MATRIX_CHARS = list(
    "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄ"
    "ﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
    "0123456789abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-=+[]{}|;:<>,.?/~\\■□█▓░"
)

# Farben, die bei den Vordergrund-Drops verwendet werden
RAINBOW_COLORS = ["red", "orange", "yellow", "green", "cyan", "blue", "magenta", "white", "lime"]

class MatrixMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💀 Deluxe Matrix Monitor 9000+ Turbo FX")
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Variablen für Dimensionen und Drop-Positionen
        self.columns = 0
        self.rows = 0
        self.drops_fg = []
        self.drops_bg = []

        # Steuerung, ob das Programm läuft
        self.running = True

        self.color_index = 0
        self.font_size = 12  # Schriftgröße für Matrix, Systeminfo usw. bleibt unverändert

        # Systeminfo-Text (zeigt CPU, RAM, GPU, Prozesse etc.)
        self.info_text = self.canvas.create_text(
            10, 40, anchor="nw", fill="white", font=("Consolas", self.font_size), text=""
        )
        self.info_x = 10
        self.info_y = 40
        self.info_dx = 1
        self.info_dy = 1

        # Newsticker (wird nun über NewsAPI und RSS-Feed befüllt)
        self.news_ticker_content = "Lade News..."
        self.news_font_size = 12  # Separate Schriftgröße für den Newsticker
        self.news_ticker = self.canvas.create_text(
            self.canvas.winfo_width(), 5, anchor="nw",
            fill="yellow", font=("Consolas", self.news_font_size), text=self.news_ticker_content
        )
        # Klick auf den Newsticker öffnet eine News-Seite im Browser (Beispiel: news.google.com)
        self.canvas.tag_bind(self.news_ticker, "<Button-1>", self.open_news)

        # Für das Netzwerkdiagramm: Listen für Download und Upload (in KB/s)
        self.net_download_data = []
        self.net_upload_data = []
        self.max_net_points = 50  # Maximale Anzahl an Datenpunkten im Diagramm
        self.last_net = psutil.net_io_counters()
        self.current_download_speed = 0.0
        self.current_upload_speed = 0.0

        # Erste Dimensionsberechnung
        self.update_dimensions()

        # Starte die periodischen Updates:
        self.update_matrix()        # Matrix-Effekt (über root.after)
        self.start_info_loop()      # Systeminfos (in einem separaten Thread, Update via after)
        self.animate_info()         # Animation des Systeminfo-Textes (via after)
        self.update_network()       # Netzwerk-Messung (alle 1000 ms)
        self.animate_news_ticker()  # Newsticker scrollt (via after)

        # Starte den News-Fetcher-Thread (News werden alle 30 Sekunden abgerufen)
        threading.Thread(target=self.news_fetcher, daemon=True).start()

        # Erstelle den Schriftgrößen-Regler (Scale) für den Newsticker ohne Label,
        # und positioniere ihn weiter rechts (z. B. 50 Pixel vom rechten Rand)
        self.news_font_scale = tk.Scale(root, from_=8, to=48, orient="vertical",
                                        command=self.update_news_font_size,
                                        bg="black", fg="white", highlightbackground="black")
        self.news_font_scale.set(self.news_font_size)
        self.news_font_scale.place(relx=1.0, rely=0.5, anchor="e", x=-50)

        # Bindings für Fenstergrößenänderung und Schließen
        self.root.bind("<Configure>", self.on_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_news_font_size(self, value):
        """Aktualisiert in Echtzeit die Schriftgröße des Newstickers."""
        self.news_font_size = int(value)
        self.canvas.itemconfig(self.news_ticker, font=("Consolas", self.news_font_size))

    def open_news(self, event):
        """
        Öffnet beim Klicken auf den Newsticker eine News-Seite im Browser.
        Hier wird beispielhaft news.google.com geöffnet.
        """
        webbrowser.open("https://news.google.com")

    def update_dimensions(self):
        """Berechnet die Fenstergröße und passt die Anzahl der Spalten/Zeilen an."""
        self.canvas.update_idletasks()
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        new_columns = width // self.font_size
        new_rows = height // self.font_size
        if new_columns != self.columns or new_rows != self.rows:
            self.columns = new_columns
            self.rows = new_rows
            self.drops_fg = [random.randint(0, self.rows) for _ in range(self.columns)]
            self.drops_bg = [random.randint(0, self.rows) for _ in range(self.columns)]

    def on_resize(self, event):
        """Wird beim Ändern der Fenstergröße aufgerufen und passt Dimensionen und Positionen an."""
        self.update_dimensions()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        text_bbox = self.canvas.bbox(self.info_text)
        if text_bbox:
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            if self.info_x + text_width > width:
                self.info_x = width - text_width
            if self.info_y + text_height > height:
                self.info_y = height - text_height
            self.canvas.coords(self.info_text, self.info_x, self.info_y)

    def on_close(self):
        """Beendet das Programm."""
        self.running = False
        self.root.destroy()

    def get_gpu_info(self):
        """Holt GPU-Informationen via nvidia-smi (nur NVIDIA GPUs)."""
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                 "--format=csv,noheader,nounits"],
                encoding="utf-8"
            )
            usage, mem_used, mem_total = map(int, output.strip().split(","))
            mem_percent = round((mem_used / mem_total) * 100, 1)
            return usage, mem_percent
        except Exception:
            return 0, 0

    def animate_info(self):
        """
        Bewegt den Systeminfo-Text im Fenster, sodass er an den Rändern abprallt.
        Läuft im Hauptthread via after().
        """
        if not self.running:
            return
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        text_bbox = self.canvas.bbox(self.info_text)
        if text_bbox:
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            if self.info_x < 0:
                self.info_x = 0
            if self.info_x + text_width > width:
                self.info_x = width - text_width
            if self.info_y < 0:
                self.info_y = 0
            if self.info_y + text_height > height:
                self.info_y = height - text_height
            if self.info_x <= 0 or self.info_x + text_width >= width:
                self.info_dx *= -1
            if self.info_y <= 0 or self.info_y + text_height >= height:
                self.info_dy *= -1
        self.info_x += self.info_dx
        self.info_y += self.info_dy
        self.canvas.coords(self.info_text, self.info_x, self.info_y)
        self.root.after(20, self.animate_info)

    def animate_news_ticker(self):
        """
        Lässt den Newsticker horizontal scrollen.
        Läuft über after().
        """
        if not self.running:
            return
        self.canvas.move(self.news_ticker, -1, 0)
        bbox = self.canvas.bbox(self.news_ticker)
        if bbox:
            if bbox[2] < 0:
                new_x = self.canvas.winfo_width()
                self.canvas.coords(self.news_ticker, new_x, 5)
        self.root.after(20, self.animate_news_ticker)

    def update_matrix(self):
        """
        Aktualisiert den Matrix-Effekt (Hintergrund- und Vordergrund-Drops).
        Läuft über after().
        """
        if not self.running:
            return
        self.update_dimensions()
        height = self.canvas.winfo_height()
        self.canvas.delete("char")
        for i in range(self.columns):
            if random.random() < 0.4:
                continue
            x = i * self.font_size
            y = self.drops_bg[i] * self.font_size
            char = random.choice(MATRIX_CHARS)
            self.canvas.create_text(
                x, y, text=char, fill="darkgreen",
                font=("Consolas", self.font_size), tags="char"
            )
            self.drops_bg[i] = (self.drops_bg[i] + 1) % self.rows
        for i in range(self.columns):
            char = random.choice(MATRIX_CHARS)
            x = i * self.font_size
            y = self.drops_fg[i] * self.font_size
            color = random.choice(RAINBOW_COLORS) if random.random() < 0.4 else "lime"
            self.canvas.create_text(
                x, y, text=char, fill=color,
                font=("Consolas", self.font_size), tags="char"
            )
            self.drops_fg[i] = 0 if y > height or random.random() < 0.02 else self.drops_fg[i] + 1
        self.root.after(10, self.update_matrix)

    def update_network(self):
        """
        Misst die Netzwerkaktivität (Download und Upload) und aktualisiert das Diagramm.
        Läuft alle 1000 ms über after().
        """
        if not self.running:
            return
        current_net = psutil.net_io_counters()
        diff_recv = current_net.bytes_recv - self.last_net.bytes_recv
        diff_sent = current_net.bytes_sent - self.last_net.bytes_sent
        self.last_net = current_net
        download_speed = diff_recv / 1024.0
        upload_speed = diff_sent / 1024.0
        self.current_download_speed = download_speed
        self.current_upload_speed = upload_speed
        self.net_download_data.append(download_speed)
        self.net_upload_data.append(upload_speed)
        if len(self.net_download_data) > self.max_net_points:
            self.net_download_data.pop(0)
        if len(self.net_upload_data) > self.max_net_points:
            self.net_upload_data.pop(0)
        self.update_network_chart()
        self.root.after(1000, self.update_network)

    def update_network_chart(self):
        """
        Zeichnet das Netzwerkdiagramm (Download in Cyan, Upload in Magenta) im unteren Bereich.
        Es wird kein störendes Hintergrundrechteck gezeichnet.
        """
        self.canvas.delete("netchart")
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        margin = 10
        chart_height = 100
        chart_width = cw - 2 * margin
        x0 = margin
        y1 = ch - margin
        y0 = y1 - chart_height
        max_val = max(self.net_download_data + self.net_upload_data + [1])
        x_step = chart_width / (self.max_net_points - 1) if len(self.net_download_data) > 1 else chart_width
        points_download = []
        for idx, val in enumerate(self.net_download_data):
            x = x0 + idx * x_step
            y = y1 - (val / max_val) * chart_height
            points_download.extend([x, y])
        if len(points_download) >= 4:
            self.canvas.create_line(points_download, fill="cyan", width=2, tags="netchart")
        points_upload = []
        for idx, val in enumerate(self.net_upload_data):
            x = x0 + idx * x_step
            y = y1 - (val / max_val) * chart_height
            points_upload.extend([x, y])
        if len(points_upload) >= 4:
            self.canvas.create_line(points_upload, fill="magenta", width=2, tags="netchart")
        info_net = f"↓ {self.current_download_speed:5.1f} KB/s    ↑ {self.current_upload_speed:5.1f} KB/s"
        self.canvas.create_text(x0 + 5, y0 + 5, anchor="nw",
                                fill="white", font=("Consolas", self.font_size),
                                text=info_net, tags="netchart")

    def fetch_news(self):
        """
        Ruft aktuelle News über NewsAPI.org ab und liefert eine Liste
        von Strings, jeweils bestehend aus Titel und kurzer Zusammenfassung.
        """
        params = {
            "country": "de",         # deutsche News – passe das ggf. an
            "pageSize": 10,
            "apiKey": NEWS_API_KEY,
            "category": "general"      # allgemeine News; auch 'business' etc. möglich
        }
        try:
            response = requests.get(NEWS_API_URL, params=params)
            data = response.json()
            articles = data.get("articles", [])
            headlines = []
            for article in articles:
                title = article.get("title", "")
                description = article.get("description", "")
                if description:
                    text = f"{title} - {description}"
                else:
                    text = title
                headlines.append(text)
            print(f"Fetched {len(headlines)} articles from API")
            return headlines
        except Exception as e:
            print("Fehler beim Abruf der NewsAPI:", e)
            return []

    def fetch_news_rss(self):
        """
        Ruft News über den RSS-Feed (z.B. Tagesschau) ab und liefert eine Liste
        von Strings, jeweils bestehend aus Titel und (falls vorhanden) kurzer Beschreibung.
        """
        try:
            response = requests.get(RSS_FEED_URL)
            # XML parsen
            root_xml = ET.fromstring(response.content)
            headlines = []
            # Im RSS sind die Artikel unter channel/item
            for item in root_xml.find("channel").findall("item"):
                title = item.find("title").text if item.find("title") is not None else ""
                description = item.find("description").text if item.find("description") is not None else ""
                if description:
                    text = f"{title} - {description}"
                else:
                    text = title
                headlines.append(text)
            print(f"Fetched {len(headlines)} articles from RSS")
            return headlines
        except Exception as e:
            print("Fehler beim Abruf des RSS-Feeds:", e)
            return []

    def news_fetcher(self):
        """
        Ruft alle 30 Sekunden die News ab und aktualisiert den Newsticker.
        Dabei werden die Ergebnisse von NewsAPI und dem RSS-Feed zusammengeführt.
        """
        while self.running:
            api_headlines = self.fetch_news()
            rss_headlines = self.fetch_news_rss()
            combined_headlines = api_headlines + rss_headlines
            if combined_headlines:
                self.news_ticker_content = "   ***   ".join(combined_headlines)
            else:
                self.news_ticker_content = "Keine News verfügbar"
            self.root.after(0, lambda: self.canvas.itemconfig(self.news_ticker, text=self.news_ticker_content))
            time.sleep(30)

    def start_info_loop(self):
        """
        Startet einen Thread, der Systeminformationen (CPU, RAM, GPU, Top-Prozesse) abruft
        und diese via after() im Systeminfo-Text anzeigt.
        """
        def loop():
            while self.running:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory().percent
                gpu, gpu_mem = self.get_gpu_info()
                processes = sorted(
                    psutil.process_iter(['name', 'cpu_percent', 'memory_percent']),
                    key=lambda p: (-p.info['cpu_percent'], -p.info['memory_percent'])
                )[:5]
                color = RAINBOW_COLORS[self.color_index % len(RAINBOW_COLORS)]
                self.color_index += 1
                info_lines = [
                    f"💥 CPU: {cpu:5.1f}%  🧠 RAM: {mem:5.1f}%  🎮 GPU: {gpu:5.1f}%  📦 GPU-RAM: {gpu_mem:5.1f}%",
                    "🚀 Top 5 Prozesse:"
                ]
                for p in processes:
                    name = (p.info['name'] or '')[:20].ljust(20)
                    cpu_p = f"{p.info['cpu_percent']:5.1f}%"
                    mem_p = f"{p.info['memory_percent']:5.1f}%"
                    info_lines.append(f"{name} | CPU: {cpu_p} | MEM: {mem_p}")
                self.root.after(0, lambda: self.canvas.itemconfig(
                    self.info_text, text="\n".join(info_lines), fill=color
                ))
                time.sleep(1)
        threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1400x900")
    app = MatrixMonitorApp(root)
    root.mainloop()
