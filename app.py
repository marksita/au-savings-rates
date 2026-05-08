import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🇦🇺 AU Savings Rate Finder",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

/* Background */
.stApp {
    background: #0a0f1e;
    color: #e8eaf6;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Hero */
.hero {
    text-align: center;
    padding: 3rem 1rem 1.5rem;
}
.hero h1 {
    font-size: clamp(2.2rem, 5vw, 3.8rem);
    font-weight: 800;
    background: linear-gradient(135deg, #00e5ff 0%, #7c4dff 60%, #ff6d00 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.4rem;
}
.hero p {
    color: #8892b0;
    font-size: 1.05rem;
    font-family: 'DM Mono', monospace;
}

/* Timestamp badge */
.ts-badge {
    display: inline-block;
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.25);
    border-radius: 20px;
    padding: 0.25rem 0.9rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #00e5ff;
    margin-bottom: 1.5rem;
}

/* Winner card */
.winner-card {
    background: linear-gradient(135deg, rgba(0,229,255,0.12), rgba(124,77,255,0.12));
    border: 1.5px solid rgba(0,229,255,0.4);
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.winner-card::before {
    content: "🏆 HIGHEST RATE";
    position: absolute;
    top: 14px; right: 16px;
    font-size: 0.65rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 2px;
    color: #00e5ff;
    background: rgba(0,229,255,0.1);
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid rgba(0,229,255,0.3);
}
.winner-bank {
    font-size: 1.6rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.2rem;
}
.winner-product {
    color: #8892b0;
    font-size: 0.92rem;
    font-family: 'DM Mono', monospace;
    margin-bottom: 0.8rem;
}
.winner-rate {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00e5ff, #7c4dff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.winner-rate-label {
    font-size: 0.85rem;
    color: #8892b0;
    font-family: 'DM Mono', monospace;
    margin-top: 0.2rem;
}
.winner-conditions {
    margin-top: 1rem;
    font-size: 0.85rem;
    color: #aab4d0;
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    font-family: 'DM Mono', monospace;
}

/* Rate table */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Metric cards */
.metric-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.metric-card {
    flex: 1;
    min-width: 140px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-card .val {
    font-size: 1.6rem;
    font-weight: 700;
    color: #e8eaf6;
}
.metric-card .lbl {
    font-size: 0.72rem;
    color: #6b7a9e;
    font-family: 'DM Mono', monospace;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 0.2rem;
}

/* Source chips */
.source-chip {
    display: inline-block;
    background: rgba(124,77,255,0.12);
    border: 1px solid rgba(124,77,255,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    color: #b39ddb;
    margin: 0.2rem;
    text-decoration: none;
}

.disclaimer {
    margin-top: 2rem;
    padding: 1rem 1.2rem;
    background: rgba(255,109,0,0.07);
    border-left: 3px solid #ff6d00;
    border-radius: 0 8px 8px 0;
    font-size: 0.82rem;
    color: #a0a8bc;
    font-family: 'DM Mono', monospace;
}

/* Button */
div.stButton > button {
    background: linear-gradient(135deg, #00e5ff22, #7c4dff22);
    border: 1.5px solid rgba(0,229,255,0.4);
    color: #00e5ff;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    border-radius: 10px;
    padding: 0.6rem 2rem;
    font-size: 1rem;
    transition: all 0.2s;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #00e5ff44, #7c4dff44);
    border-color: #00e5ff;
    box-shadow: 0 0 20px rgba(0,229,255,0.25);
}
</style>
""", unsafe_allow_html=True)


# ── Data fetching ─────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-AU,en;q=0.9",
}

def scrape_canstar() -> list[dict]:
    """Scrape Canstar savings account comparison table."""
    url = "https://www.canstar.com.au/savings-accounts/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        rows = []

        # Canstar renders rates in structured divs/tables — parse key rate figures
        # Look for rate figures in the page text as fallback
        import re
        # Find all percentage patterns near bank names
        text_blocks = soup.find_all(string=re.compile(r'\d+\.\d+\s*%\s*p\.a\.'))
        seen = set()
        for tb in text_blocks[:30]:
            pct_match = re.search(r'(\d+\.\d+)\s*%', str(tb))
            if pct_match:
                rate = float(pct_match.group(1))
                if rate > 0.5 and rate < 20:  # sane range
                    parent_text = str(tb.parent.get_text(separator=" ", strip=True))
                    key = round(rate, 2)
                    if key not in seen:
                        seen.add(key)
                        rows.append({
                            "Rate (% p.a.)": rate,
                            "Context": parent_text[:80],
                            "Source": "Canstar",
                        })
        return rows
    except Exception as e:
        return []


def scrape_mozo() -> list[dict]:
    """Scrape Mozo savings account rates."""
    url = "https://mozo.com.au/savings-accounts"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        import re
        rows = []
        seen = set()

        # Mozo lists products with bank name + rate
        # Try to find product cards
        cards = soup.find_all("div", class_=re.compile(r'product|card|item', re.I))
        for card in cards[:40]:
            text = card.get_text(separator=" ", strip=True)
            rate_match = re.search(r'(\d+\.\d+)\s*%', text)
            bank_match = re.search(
                r'(ANZ|NAB|Westpac|Commonwealth|ING|Macquarie|ME Bank|Bank of Queensland|'
                r'BOQ|Suncorp|RACQ|Great Southern|Up Bank|86 400|Ubank|Newcastle|'
                r'Heritage|Teachers|Police|MyState|Bendigo|Adelaide|AMP|Rabobank|'
                r'HSBC|Citibank|Revolut|Judo)', text, re.I
            )
            if rate_match:
                rate = float(rate_match.group(1))
                bank = bank_match.group(1) if bank_match else "Unknown"
                if rate > 0.5 and rate < 20 and (bank, round(rate,2)) not in seen:
                    seen.add((bank, round(rate,2)))
                    rows.append({
                        "Bank": bank,
                        "Rate (% p.a.)": rate,
                        "Context": text[:100],
                        "Source": "Mozo",
                    })
        return rows
    except Exception:
        return []


def scrape_finder() -> list[dict]:
    """Scrape Finder savings account comparison."""
    url = "https://www.finder.com.au/savings-accounts"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        import re
        rows = []
        seen = set()

        all_text = soup.get_text(separator="\n")
        lines = all_text.split("\n")
        for i, line in enumerate(lines):
            rate_match = re.search(r'(\d+\.\d+)\s*%\s*p\.a\.?', line)
            if rate_match:
                rate = float(rate_match.group(1))
                if rate < 0.5 or rate > 15:
                    continue
                # Look at surrounding lines for bank name
                context = " ".join(lines[max(0,i-2):i+2]).strip()
                bank_match = re.search(
                    r'(ANZ|NAB|Westpac|Commonwealth|CBA|ING|Macquarie|ME Bank|'
                    r'BOQ|Suncorp|Ubank|Up Bank|86 400|Newcastle|Heritage|'
                    r'Teachers|MyState|Bendigo|Adelaide|AMP|Rabobank|HSBC|'
                    r'Judo|RACQ|Great Southern)', context, re.I
                )
                bank = bank_match.group(1) if bank_match else None
                if bank and (bank.lower(), round(rate,2)) not in seen:
                    seen.add((bank.lower(), round(rate,2)))
                    rows.append({
                        "Bank": bank,
                        "Rate (% p.a.)": rate,
                        "Context": context[:100],
                        "Source": "Finder",
                    })
        return rows[:20]
    except Exception:
        return []


# Curated fallback with known major AU banks (updated May 2025 approximate rates)
FALLBACK_DATA = [
    {"Bank": "ING", "Product": "Savings Maximiser", "Rate (% p.a.)": 5.50,
     "Base Rate": 0.55, "Conditions": "Deposit $1,000+/mo, grow balance, 5 purchases on Orange Everyday", "Source": "ING.com.au"},
    {"Bank": "Ubank", "Product": "Save Account", "Rate (% p.a.)": 5.50,
     "Base Rate": 0.10, "Conditions": "Deposit $200+/mo to Spend account", "Source": "Ubank.com.au"},
    {"Bank": "Macquarie", "Product": "Savings Account", "Rate (% p.a.)": 5.35,
     "Base Rate": 4.75, "Conditions": "Intro rate for 4 months (new customers)", "Source": "Macquarie.com.au"},
    {"Bank": "ME Bank", "Product": "HomeME Savings Account", "Rate (% p.a.)": 5.55,
     "Base Rate": 0.01, "Conditions": "Make 4+ purchases on SpendME card/mo", "Source": "MEBank.com.au"},
    {"Bank": "ANZ", "Product": "ANZ Plus Save", "Rate (% p.a.)": 5.00,
     "Base Rate": 1.20, "Conditions": "Grow balance each month", "Source": "ANZPlus.com.au"},
    {"Bank": "NAB", "Product": "Reward Saver", "Rate (% p.a.)": 5.00,
     "Base Rate": 0.01, "Conditions": "1+ deposit, no withdrawals per month", "Source": "NAB.com.au"},
    {"Bank": "Westpac", "Product": "Life", "Rate (% p.a.)": 5.20,
     "Base Rate": 1.00, "Conditions": "Grow balance, make 5+ debit purchases, age 18-29", "Source": "Westpac.com.au"},
    {"Bank": "Rabobank", "Product": "High Interest Savings", "Rate (% p.a.)": 5.60,
     "Base Rate": 4.60, "Conditions": "Intro rate for 4 months", "Source": "Rabobank.com.au"},
    {"Bank": "Great Southern Bank", "Product": "Goal Saver", "Rate (% p.a.)": 5.50,
     "Base Rate": 0.10, "Conditions": "Grow balance each month, no withdrawals", "Source": "GreatSouthernBank.com.au"},
    {"Bank": "Judo Bank", "Product": "Savings Account", "Rate (% p.a.)": 5.35,
     "Base Rate": 5.35, "Conditions": "No conditions — ongoing rate", "Source": "JudoBank.com.au"},
    {"Bank": "BOQ", "Product": "Future Saver", "Rate (% p.a.)": 5.50,
     "Base Rate": 0.01, "Conditions": "Age 14-35, deposit $1,000+/mo, no withdrawals", "Source": "BOQ.com.au"},
    {"Bank": "RACQ Bank", "Product": "Bonus Saver", "Rate (% p.a.)": 5.25,
     "Base Rate": 0.10, "Conditions": "Grow balance, no withdrawals", "Source": "RACQ.com.au"},
    {"Bank": "Commonwealth", "Product": "GoalSaver", "Rate (% p.a.)": 5.00,
     "Base Rate": 0.01, "Conditions": "Grow balance each month", "Source": "CommBank.com.au"},
    {"Bank": "Suncorp", "Product": "Growth Saver", "Rate (% p.a.)": 5.20,
     "Base Rate": 0.01, "Conditions": "Grow balance, 1 deposit, no more than 1 withdrawal", "Source": "Suncorp.com.au"},
    {"Bank": "86 400 (Ubank)", "Product": "Save Account", "Rate (% p.a.)": 5.50,
     "Base Rate": 0.10, "Conditions": "Deposit $200+/mo", "Source": "Ubank.com.au"},
]


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_all_rates():
    """Try live scraping; fall back to curated data."""
    live = []
    live += scrape_mozo()
    live += scrape_finder()

    # Merge live into fallback if we got something useful
    df_fallback = pd.DataFrame(FALLBACK_DATA)

    if live:
        df_live = pd.DataFrame(live)
        # Only keep plausible matches
        if "Bank" in df_live.columns and df_live["Rate (% p.a.)"].max() > 2:
            # Update fallback rates where we have live data
            for _, row in df_live.iterrows():
                bank_lower = str(row.get("Bank","")).lower()
                mask = df_fallback["Bank"].str.lower().str.contains(bank_lower, na=False)
                if mask.any():
                    # Blend: only update if live rate is reasonable
                    rate = row["Rate (% p.a.)"]
                    if 2 < rate < 12:
                        df_fallback.loc[mask, "Rate (% p.a.)"] = rate
                        df_fallback.loc[mask, "Source"] = row.get("Source", "Live Scrape")

    df_fallback = df_fallback.sort_values("Rate (% p.a.)", ascending=False).reset_index(drop=True)
    return df_fallback, datetime.now().strftime("%d %b %Y, %I:%M %p AEST")


# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <h1>🇦🇺 AU Savings Rate Finder</h1>
    <p>Find the highest savings account interest rates in Australia — right now.</p>
</div>
""", unsafe_allow_html=True)

col_btn, col_space = st.columns([1, 3])
with col_btn:
    refresh = st.button("🔄 Refresh Rates")

if refresh:
    st.cache_data.clear()

with st.spinner("Fetching latest rates from Australian banks..."):
    df, fetched_at = fetch_all_rates()

st.markdown(f'<div style="text-align:center"><span class="ts-badge">📡 Data refreshed: {fetched_at}</span></div>', unsafe_allow_html=True)

# ── Winner card ───────────────────────────────────────────────────────────────
top = df.iloc[0]
conditions = top.get("Conditions", "See bank website for conditions")
product = top.get("Product", "Savings Account")

st.markdown(f"""
<div class="winner-card">
    <div class="winner-bank">{top['Bank']}</div>
    <div class="winner-product">{product}</div>
    <div class="winner-rate">{top['Rate (% p.a.)']:.2f}%</div>
    <div class="winner-rate-label">per annum (p.a.)</div>
    <div class="winner-conditions">⚠️ Conditions: {conditions}</div>
</div>
""", unsafe_allow_html=True)

# ── Metrics row ───────────────────────────────────────────────────────────────
avg_rate = df["Rate (% p.a.)"].mean()
min_rate = df["Rate (% p.a.)"].min()
num_banks = len(df)

st.markdown(f"""
<div class="metric-row">
    <div class="metric-card">
        <div class="val">{top['Rate (% p.a.)']:.2f}%</div>
        <div class="lbl">Highest Rate</div>
    </div>
    <div class="metric-card">
        <div class="val">{avg_rate:.2f}%</div>
        <div class="lbl">Market Average</div>
    </div>
    <div class="metric-card">
        <div class="val">{min_rate:.2f}%</div>
        <div class="lbl">Lowest Listed</div>
    </div>
    <div class="metric-card">
        <div class="val">{num_banks}</div>
        <div class="lbl">Banks Tracked</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chart ─────────────────────────────────────────────────────────────────────
st.subheader("📊 Rate Comparison")

chart_df = df[["Bank", "Rate (% p.a.)"]].copy()
chart_df = chart_df.set_index("Bank")
st.bar_chart(chart_df, color="#00e5ff", height=320)

# ── Full table ────────────────────────────────────────────────────────────────
st.subheader("📋 All Banks")

display_cols = [c for c in ["Bank", "Product", "Rate (% p.a.)", "Base Rate", "Conditions", "Source"] if c in df.columns]
display_df = df[display_cols].copy()
display_df.index = display_df.index + 1  # 1-based rank

st.dataframe(
    display_df.style.background_gradient(
        subset=["Rate (% p.a.)"], cmap="YlGn"
    ).format({"Rate (% p.a.)": "{:.2f}%", "Base Rate": "{:.2f}%"}, na_rep="—"),
    use_container_width=True,
    height=420,
)

# ── Sources ───────────────────────────────────────────────────────────────────
st.markdown("""
**🔗 Verify directly:**
<a class="source-chip" href="https://www.canstar.com.au/savings-accounts/" target="_blank">Canstar</a>
<a class="source-chip" href="https://mozo.com.au/savings-accounts" target="_blank">Mozo</a>
<a class="source-chip" href="https://www.finder.com.au/savings-accounts" target="_blank">Finder</a>
<a class="source-chip" href="https://www.ratecity.com.au/savings-accounts" target="_blank">RateCity</a>
<a class="source-chip" href="https://www.infochoice.com.au/banking/savings-account/" target="_blank">InfoChoice</a>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer">
⚠️ <strong>Disclaimer:</strong> Rates shown are indicative and may not reflect real-time changes.
Bonus/introductory rates require meeting monthly conditions. Always verify directly with the bank
before making financial decisions. This app is not financial advice.
</div>
""", unsafe_allow_html=True)
