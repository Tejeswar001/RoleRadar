# 🔍 Role Radar

**Role Radar** is a lightweight Flask-based tool that helps users find domain experts with 10+ years of experience using minimal input. It uses dummy data, simulates AI/NLP scoring, and offers a clean UI for future integration with real data sources.

---

## 🚀 Features

- Minimalist UI for expert discovery
- Domain + optional keyword-based search
- Simulated results with confidence scoring
- TailwindCSS-styled responsive layout
- Flask backend (ready for real data/API in V1)

---

## 🧪 Tech Stack

- Python 3.x
- Flask
- TailwindCSS (via CDN)
- Render (for deployment)

---

## 📸 Screens

| Page       | Description                       |
|------------|---------------------------------|
| `/`        | Home page                       |
| `/signin`  | Dummy sign-in page              |
| `/signup`  | Dummy sign-up page              |
| `/finder`  | Search form for domain/keywords |
| `/results` | Displays dummy expert results   |

---

## 🛠 Setup Instructions

### 📦 Prerequisites

- Python 3.x
- `pip` (Python package manager)

### 🔧 Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/your-username/role-radar.git
   cd role-radar
   ```

2. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app locally**:

   ```bash
   python app.py
   ```

5. Open your browser at: [http://localhost:5000](http://localhost:5000)

---

## 🚀 Deployment on Render

### ✅ Build & Start Commands

* **Build Command**:

  ```bash
  pip install -r requirements.txt
  ```

* **Start Command**:

  ```bash
  gunicorn app:app
  ```

> Ensure your `app.py` file defines the Flask app as:

```python
app = Flask(__name__)
```

---

## 📂 Project Structure

```
role-radar/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── home.html
│   ├── signin.html
│   ├── signup.html
│   ├── finder.html
│   └── results.html
└── static/
    └── (optional assets like styles, images)
```

---

## 📜 License

MIT License — feel free to use, modify, and share.

---

## 🙌 Acknowledgements

Made with ❤️ using Flask and TailwindCSS
