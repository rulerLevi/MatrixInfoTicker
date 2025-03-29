

---

# DeluxeMatrixDashboard

DeluxeMatrixDashboard is an innovative application that combines a dynamic Matrix effect with real-time system monitoring and an integrated news ticker. It delivers real-time information on CPU, RAM, GPU, and network usage, all set against a continuously animated Matrix-style background. Additionally, a built-in news ticker aggregates current headlines and short summaries from multiple sources (using NewsAPI.org and an RSS feed), ensuring that up-to-date news scrolls across the screen.

## Features

- **Matrix Effect:**  
  A continuously updated Matrix-style animation that serves as a captivating background.

- **Real-Time System Monitoring:**  
  Displays CPU, RAM, GPU, and network activity in real-time.

- **Integrated News Ticker:**  
  Combines news headlines and brief summaries from two sources—NewsAPI.org and an RSS feed (e.g., from Tagesschau)—to provide up-to-date news.

- **Interactive News:**  
  Clickable headlines in the news ticker open the corresponding news page in your default browser.

- **Customizable Appearance:**  
  A slider allows you to adjust the news ticker's font size in real time, ensuring the display fits your preferences.

- **Responsive Layout:**  
  The application dynamically adjusts to changes in window size, ensuring that all elements remain visible and well-positioned.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/DeluxeMatrixDashboard.git
   cd DeluxeMatrixDashboard
   ```

2. **Install Dependencies:**

   The project requires Python 3 and the following libraries:
   - `tkinter` (usually included with Python)
   - `psutil`
   - `requests`

   Install the required packages using pip:

   ```bash
   pip install psutil requests
   ```

3. **Configure the API Key:**

   Open the source code file and replace `"YOUR_NEWSAPI_KEY_HERE"` with your actual API key from [NewsAPI.org](https://newsapi.org).

## Usage

Run the application with:

```bash
python DeluxeMatrixDashboard.py
```

The application window will open, displaying the Matrix effect, system monitoring information, and a scrolling news ticker. You can adjust the news ticker’s font size using the slider on the right. Clicking on any news headline will open the associated news page in your default browser.

## License

This project is released under the [MIT License](LICENSE).

---
!



# MatrixInfoTicker
Matrix-Effekt mit Systeminfos und einem dynamischen News-Ticker kombinierst
DeluxeMatrixDashboard
DeluxeMatrixDashboard ist eine innovative Anwendung, die auf eindrucksvolle Weise einen klassischen Matrix-Effekt mit moderner Systemüberwachung und aktuellen Nachrichten kombiniert. Das Dashboard zeigt in Echtzeit Informationen zur CPU-, RAM-, GPU- und Netzwerkaktivität, während im Hintergrund ein dynamischer Matrix-Effekt die Konsole füllt. Gleichzeitig scrollt ein integrierter Newsticker – gespeist aus NewsAPI.org und einem RSS-Feed (z. B. von Tagesschau) – aktuelle Nachrichten inklusive kurzer Zusammenfassungen. Interaktive Elemente wie anklickbare News, die im Browser geöffnet werden, und ein Regler zur Anpassung der News-Schriftgröße runden das Benutzererlebnis ab. Ideal für alle, die Systemperformance und weltweite Nachrichten auf einen Blick erleben möchten – mit einem Hauch von Retro-Matrix-Ästhetik.
