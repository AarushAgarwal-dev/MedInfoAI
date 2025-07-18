# MedInfo AI

Your Intelligent Health Companion  
---

## 🚀 Quick Links

- [Live Demo](#) <!-- Add your deployed link here -->
- [Documentation](#)
- [Open an Issue](https://github.com/AarushAgarwal-dev/medinfoai/issues)
- [Pull Requests](https://github.com/AarushAgarwal-dev/medinfoai/pulls)
- [Contributing Guide](#-contributing)

---

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Backend-Flask-green?logo=flask)
![React](https://img.shields.io/badge/Frontend-React-blue?logo=react)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)
![Open Source](https://badgen.net/badge/Open%20Source/Yes/green)
![Issues](https://img.shields.io/github/issues/your-username/medinfoai)
![Pull Requests](https://img.shields.io/github/issues-pr/your-username/medinfoai)
[![Live Demo](https://img.shields.io/badge/Demo-Live-green)](#)

---

## 🗂️ Table of Contents

- [Quick Links](#-quick-links)
- [Features](#-key-features)
- [Features Table](#-features-table)
- [Screenshots](#-screenshots)
- [Demo](#-demo)
- [Architecture Overview](#-architecture-overview)
- [How it Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Usage Guide](#-usage-guide)
- [Deployment](#-deployment)
- [Core API Endpoints](#-core-api-endpoints)
- [Accessibility & Inclusivity](#-accessibility--inclusivity)
- [Data Sources & Trust](#-data-sources--trust)
- [How to Contribute Data or Articles](#-how-to-contribute-data-or-articles)
- [Security & Privacy](#-security--privacy)
- [UI/UX Highlights](#-uiux-highlights)
- [Vision & Roadmap](#-vision--roadmap-expanded)
- [Community & Support](#-community--support)
- [FAQ](#-faq)
- [Contact & Support](#-contact--support)
- [Changelog](#-changelog)
- [Contributors](#-contributors)
- [Support Us](#-support-us)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

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

## 🗂️ Features Table

| Feature                        | Description                                                                 |
|------------------------------- |-----------------------------------------------------------------------------|
| Drug Search                    | Find drugs by brand/generic, view details, side effects, and warnings        |
| Brand/Generic Alternatives     | Discover equivalent medicines in your region                                 |
| AI Medical Assistant           | Chatbot answers health questions 24/7                                        |
| Kendra Finder                  | Locate Jan Aushadi Kendras on an interactive map                             |
| Price Comparison               | Compare prices from multiple online pharmacies                               |
| Daily Essentials               | Curated list of wellness essentials, add to cart                             |
| Saved Items                    | Save favourite medicines/products locally                                    |
| Responsive UI                  | Mobile-first, fast, and accessible                                           |

---

## 📸 Demo

Coming soon! (Feel free to open a PR with screenshots or a screencast.)

**Want to help?**
- Run the app locally (see [Getting Started](#-getting-started)).
- Take screenshots of key features (search, AI chat, price comparison, etc.).
- Add them to the `README.md` or open a PR with your images in a `/screenshots` folder.
- Or record a short screencast and link it here!

---


## 🧩 Core API Endpoints

| Endpoint                | Method | Description                                 |
|------------------------|--------|---------------------------------------------|
| `/search`              | POST   | Search for a medicine, get details, alternatives |
| `/price-comparison`    | POST   | Compare prices for a medicine               |
| `/ai-assistant`        | POST   | Chat with the AI medical assistant          |
| `/essentials/`         | GET    | Get daily essentials categories             |
| `/kendra`              | GET    | Find Jan Aushadi Kendras (India)            |
| `/blog`                | GET    | Fetch health & wellness articles            |
| `/users/saved/<user>`  | GET    | Get saved items for a user                  |

**Example: Medicine Search**
```http
POST /search
{
  "medicine_name": "Paracetamol"
}
```
_Response:_
```json
{
  "identified_medicine": "Paracetamol",
  "composition": "Paracetamol 500mg",
  "generic_name": "Paracetamol",
  "image_url": "...",
  "generic_info_paragraph": "...",
  "summary": {
    "uses": ["..."],
    "side_effects": ["..."],
    "warnings": ["..."]
  },
  "alternatives": [
    { "brand_name": "Brand 1", "manufacturer": "Company A", "match_confidence": "Exact Match" }
  ]
}
```

---

## ♿ Accessibility & Inclusivity

- **Simple Language:** Medical jargon is translated into clear, everyday language.
- **Visual Aids:** Icons, color, and layout help users of all literacy levels.
- **Future Voice Interface:** Plans for a voice-first experience to reach even more users.
- **Mobile-First:** Fully responsive for all devices.

---

## 🔗 Data Sources & Trust

- **Google Custom Search API:** For up-to-date, reputable web data.
- **Groq LLM:** For fast, accurate AI answers and synthesis.
- **Verified Databases:** Information is cross-checked for reliability.
- **No Misinformation:** Focus on clarity, accuracy, and safety.

---

## ✍️ How to Contribute Data or Articles

- **Blog:** Submit health & wellness articles via Pull Requests.
- **Suggest Medicines:** Open an issue to request new drugs or corrections.
- **Localization:** Help translate or adapt for your region.

---

## 🔒 Security & Privacy

- **No Personal Health Data Stored:** All saved items are local to your browser.
- **No Tracking:** No analytics or tracking of your health queries.
- **Open Source:** Code is transparent and auditable.

---

## 🎨 UI/UX Highlights

- **React + Vite + Tailwind:** Fast, modern, and beautiful interface.
- **Leaflet Maps:** Interactive, real-time Kendra Finder.
- **Accessible Design:** High contrast, keyboard navigation, and mobile support.
- **Instant Feedback:** Loading indicators, error messages, and helpful prompts.

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

## ⚙️ How it Works

1. **User interacts** with the React frontend (search, chat, compare, etc.).
2. **Frontend** sends API requests to the Flask backend for data, AI answers, or price info.
3. **Backend** processes requests, queries the SQLite DB, external APIs (Groq, Google), or scrapes pharmacy sites.
4. **Results** are returned to the frontend and displayed in a user-friendly UI.
5. **Saved items** are managed in the browser's `localStorage` for persistence.

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

## 🌐 Community & Support

- **Discussions:** [GitHub Discussions](https://github.com/AarushAgarwal-dev/medinfo-ai/discussions)
- **Issues:** [File an Issue](https://github.com/AarushAgarwal-dev/medinfo-ai/issues)
- **Pull Requests:** [Contribute Code](https://github.com/AarushAgarwal-dev/medinfo-ai/pulls)

Join our community to ask questions, suggest features, or get help!

---

## 🤔 FAQ

**Q: Is MedInfo AI a replacement for a doctor?**
A: No. MedInfo AI is for educational purposes only. Always consult a qualified healthcare provider for medical advice.

**Q: Is my data private?**
A: No personal health data is stored on the server. Saved items are stored locally in your browser.

**Q: Can I contribute new features?**
A: Absolutely! See [Contributing](#-contributing) below.

**Q: How do I get API keys?**
A: Sign up at [Groq Cloud](https://console.groq.com/keys) and [Google Cloud](https://console.cloud.google.com/) for free API keys.

**Q: Does it work outside India?**
A: Most features work globally, but some (like Kendra Finder) are India-specific.

---

## 📬 Contact & Support

For questions, bug reports, or feature requests:
- Open an [issue](https://github.com/AarushAgarwal-dev/medinfo-ai/issues)

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

---

## 📝 Changelog

See [Releases](https://github.com//AarushAgarwal-dev/medinfoai/releases) for the latest updates and changelog.

---

## 👥 Contributors

Thanks to these amazing people:

[![Contributors](https://contrib.rocks/image?repo=AarushAgarwal-dev/medinfoai)](https://github.com/AarushAgarwal-dev/medinfoai/graphs/contributors)

---

## 💖 Support Us

If you find MedInfo AI useful, please consider giving us a ⭐ star, sharing with friends, or contributing code/content!

[![Star](https://img.shields.io/github/stars/AarushAgarwal-dev/medinfoai?style=social)](https://github.com/AarushAgarwal-dev/medinfoai)
[![Forks](https://img.shields.io/github/forks/AarushAgarwal-dev/medinfoai?style=social)](https://github.com/AarushAgarwal-dev/medinfoai)

---
