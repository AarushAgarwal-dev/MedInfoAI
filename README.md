# MedInfo AI

Your Intelligent Health Companion  
*(An open-source project by **Anshika Agarwal**, Grade 10)*

---

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Backend-Flask-green?logo=flask)
![React](https://img.shields.io/badge/Frontend-React-blue?logo=react)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

MedInfo AI is a full-stack web application that helps users quickly find reliable medication information, compare prices across pharmacies, discover generic alternatives, and chat with an empathetic AI medical assistant — all in one place.

> **Disclaimer**  
> MedInfo AI provides information for educational purposes only and is **not** a replacement for professional medical advice. Always consult a qualified healthcare provider for diagnosis or treatment.

---

## ✨ Key Features

1. **Comprehensive Drug Search** – composition, indications, side-effects, contraindications, and warnings.
2. **Brand & Generic Alternatives** – discover region-specific equivalent brands or generics.
3. **AI Medical Assistant** – 24 × 7 AI chatbot powered by Groq to answer health questions.
4. **Jan Aushadi Kendra Finder** – locate government-run generic medicine stores in India via Leaflet maps.
5. **Price Comparison** – scrape/aggregate prices from multiple online pharmacies.
6. **Daily Essentials List** – curated wellness essentials with quick add-to-cart capability.
7. **Saved Items** – persist favourite medicines/products locally via `localStorage`.
8. **Responsive UI** – built with React + Tailwind CSS for mobile-first experience.

---

## 🗺️ Table of Contents

- [Demo](#-demo)
- [Architecture](#-architecture-overview)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running Locally](#running-locally)
- [Usage Guide](#-usage-guide)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## 📸 Demo

Coming soon! (Feel free to open a PR with screenshots or a screencast.)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────┐          ┌──────────────────────────┐
│         Frontend           │          │         Backend          │
│  React + Vite + Tailwind   │  HTTPS   │  Flask REST API + Groq   │
└────────────┬───────────────┘          └──────────┬───────────────┘
             │                                       │
             ▼                                       ▼
      User Browser                         External APIs (Groq, Google CSE)
```

- **Frontend** communicates with Flask via REST endpoints for data, and uses Leaflet for maps.  
- **Backend** orchestrates AI queries (Groq) and Google Custom Search, performs web-scraping for price data, and serves static HTML templates.  
- **Database**: Light-weight SQLite seed file for sample blog/articles; client-side `localStorage` for saved items.

---

## 🔧 Tech Stack

| Layer      | Technology                                                |
|------------|-----------------------------------------------------------|
| Frontend   | React, TypeScript, Vite, Tailwind CSS, Leaflet.js         |
| Backend    | Python 3.8+, Flask, Groq API, Google Custom Search API    |
| Database   | SQLite 3 (server-side seed data) & `localStorage` (client) |
| Tooling    | ESLint, Prettier, Vite dev server                         |

---

## 📁 Project Structure

```
medicine_website/
├── app.py                 # Flask entry-point (legacy template)
├── backend/               # Modern Flask application package
│   ├── app/               #   ↳ __init__.py, routes, db, etc.
│   ├── medicine_db.sqlite3
│   └── seed_data.py       # Seed script for demo data
├── frontend/              # React / Vite application
│   ├── src/               #   ↳ components, pages, assets
│   └── package.json
├── static/                # Legacy static assets (HTML/CSS/JS)
├── templates/             # Jinja2 HTML templates
└── README.md              # You are here 🥳
```

> Note: Two historical copies (`medicine_website - Copy/`) exist for reference. Active development happens in the root-level `backend/` & `frontend/` folders.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (recommend ≥ 3.11 for best performance)
- **Node.js 18+** & **npm 9+**

### Installation

```bash
# 1) Clone the repository
$ git clone https://github.com/your-username/medinfo-ai.git
$ cd medicine_website

# 2) BACKEND ────────────────────────────────────────────
$ python -m venv venv
$ # Windows
$ venv\Scripts\activate
$ # macOS/Linux
$ source venv/bin/activate
$ pip install -r requirements.txt

# 3) FRONTEND ───────────────────────────────────────────
$ cd frontend
$ npm install
```

### Environment Variables

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
```

> Sign up for keys at [Groq Cloud](https://console.groq.com/keys) and [Google Cloud](https://console.cloud.google.com/).

### Running Locally

```bash
# Terminal 1 – Backend (root folder)
$ flask --app backend.app.main run --reload
# Accessible at http://127.0.0.1:5000

# Terminal 2 – Frontend (frontend/ folder)
$ npm run dev
# Vite dev server → usually http://localhost:5173
```

Navigate to `http://localhost:5173` and start exploring!

---

## 📖 Usage Guide

1. **Search a drug** by generic or brand name.  
2. Click **"View Details"** to see composition, uses, side-effects, and precautions.  
3. **Compare prices** by selecting the **Price** tab.  
4. Open the **AI Assistant** page to chat with the Groq-powered bot.  
5. Add items to **Saved List** for quick reference.

---

## 🛫 Deployment

### Production Build

```bash
# Build the React frontend
$ cd frontend && npm run build
# The static output lives in frontend/dist/

# (Optional) Copy build into Flask static folder
$ cp -r dist ../backend/app/static
```

Deploy the Flask app on your favourite PaaS (Railway, Render, Fly.io, etc.). Remember to set environment variables and serve the built React app as static files.

---

## 🤝 Contributing

Contributions are very welcome! 💖  

1. Fork the repo & create a new branch `git checkout -b feature/awesome`
2. Commit your changes with conventional commits.
3. Run `npm run lint && npm test` before pushing.
4. Open a Pull Request and describe your changes.

---

## 📅 Roadmap

- [ ] Migrate legacy Flask templates to React pages
- [ ] Add user authentication (JWT)
- [ ] Integrate pharmacy APIs for real-time prices
- [ ] Implement unit & e2e tests (PyTest, Playwright)
- [ ] Dark mode 🌙

---

## 📜 License

This project is licensed under the **MIT License** – see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [Groq Cloud](https://console.groq.com/) for blazing-fast large language models.
- [Google Custom Search API](https://developers.google.com/custom-search/v1/overview) for search results.
