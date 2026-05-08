[README.md](https://github.com/user-attachments/files/27502705/README.md)
# 🇦🇺 AU Savings Rate Finder

> Find the highest savings account interest rates in Australia — updated automatically.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🏦 Tracks **15+ major Australian banks** (ING, Macquarie, ME Bank, Rabobank, Ubank, ANZ Plus, NAB, Westpac, CBA, BOQ, and more)
- 🔄 **Live scraping** from Mozo & Finder with curated fallback data
- 🏆 Highlights the **#1 highest rate** with conditions at a glance
- 📊 Visual bar chart comparison across all banks
- ⚠️ Shows bonus rate conditions so you know what's required
- 🆓 **100% free** — no API keys, no database, no subscriptions

---

## 🚀 Deploy in 5 Minutes (Free)

### Step 1 — Fork this repo on GitHub

Click **Fork** (top right of this page) to copy the repo to your GitHub account.

### Step 2 — Deploy on Streamlit Community Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub
2. Click **"New app"**
3. Select your forked repo
4. Set **Main file path** to `app.py`
5. Click **"Deploy!"**

That's it. Your app will be live at a free `*.streamlit.app` URL in ~60 seconds. ✅

---

## 💻 Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/au-savings-rate-finder.git
cd au-savings-rate-finder

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## 📁 Project Structure

```
au-savings-rate-finder/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🔍 How It Works

1. **Live scraping** — On each refresh, the app attempts to scrape current rates from Mozo and Finder using `requests` + `BeautifulSoup`
2. **Smart fallback** — If scraping fails (anti-bot protections, rate limiting), a curated dataset of ~15 major banks is used
3. **Rate blending** — Live scraped rates are merged into the curated dataset when plausible values are found
4. **Caching** — Results are cached for 30 minutes to avoid hammering comparison sites

### Tracked Banks
ING · Ubank · ME Bank · Rabobank · Macquarie · Great Southern Bank · Westpac · BOQ · Suncorp · ANZ Plus · NAB · Commonwealth · Judo Bank · RACQ · and more

---

## ⚠️ Disclaimer

Rates shown are indicative only and may not reflect real-time changes. Bonus rates require meeting monthly conditions (deposits, card purchases, balance growth, etc.). Always verify directly with the bank. This app is **not financial advice**.

---

## 📜 License

MIT — free to use, modify, and deploy.
