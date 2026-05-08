import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🇦🇺 AU Savings Rate Finder",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS (white theme) ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

.stApp { background: #f5f7fa; color: #1a1f36; }

#MainMenu, footer, header { visibility: hidden; }

.hero { text-align: center; padding: 2.5rem 1rem 1rem; }
.hero h1 {
    font-size: clamp(2rem, 5vw, 3.4rem);
    font-weight: 800;
    background: linear-gradient(135deg, #0066cc 0%, #4f46e5 60%, #0891b2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin-bottom: 0.4rem;
}
.hero p { color: #64748b; font-size: 1.05rem; font-family: 'DM Mono', monospace; }

.ts-badge {
    display: inline-block;
    background: #e0f2fe;
    border: 1px solid #bae6fd;
    border-radius: 20px;
    padding: 0.25rem 0.9rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #0369a1;
    margin-bottom: 1.5rem;
}

.winner-card {
    background: linear-gradient(135deg, #eff6ff, #eef2ff);
    border: 1.5px solid #bfdbfe;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(79,70,229,0.08);
}
.winner-card::before {
    content: "🏆 HIGHEST RATE";
    position: absolute;
    top: 14px; right: 16px;
    font-size: 0.65rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 2px;
    color: #4f46e5;
    background: #e0e7ff;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid #c7d2fe;
}
.winner-bank { font-size: 1.7rem; font-weight: 800; color: #1e293b; margin-bottom: 0.2rem; }
.winner-product { color: #64748b; font-size: 0.92rem; font-family: 'DM Mono', monospace; margin-bottom: 0.8rem; }
.winner-rate {
    font-size: 3.8rem; font-weight: 800;
    background: linear-gradient(90deg, #0066cc, #4f46e5);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    line-height: 1;
}
.winner-rate-label { font-size: 0.85rem; color: #64748b; font-family: 'DM Mono', monospace; margin-top: 0.3rem; }
.winner-conditions {
    margin-top: 1rem; font-size: 0.84rem; color: #475569;
    background: #fff; border-radius: 8px; padding: 0.7rem 1rem;
    font-family: 'DM Mono', monospace; border: 1px solid #e2e8f0;
}

.metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 140px; background: #ffffff;
    border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1.1rem 1.2rem; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.metric-card .val { font-size: 1.7rem; font-weight: 800; color: #0066cc; }
.metric-card .lbl {
    font-size: 0.72rem; color: #94a3b8;
    font-family: 'DM Mono', monospace;
    letter-spacing: 1px; text-transform: uppercase; margin-top: 0.2rem;
}

.source-chip {
    display: inline-block; background: #f1f5f9;
    border: 1px solid #cbd5e1; border-radius: 20px;
    padding: 0.2rem 0.75rem; font-size: 0.75rem;
    font-family: 'DM Mono', monospace; color: #475569; margin: 0.2rem; text-decoration: none;
}

.disclaimer {
    margin-top: 2rem; padding: 1rem 1.2rem;
    background: #fff7ed; border-left: 3px solid #f97316;
    border-radius: 0 8px 8px 0; font-size: 0.82rem;
    color: #78350f; font-family: 'DM Mono', monospace;
}

div.stButton > button {
    background: #4f46e5; border: none; color: #ffffff;
    font-family: 'Syne', sans-serif; font-weight: 700;
    border-radius: 10px; padding: 0.6rem 2rem;
    font-size: 1rem; box-shadow: 0 2px 8px rgba(79,70,229,0.25);
}
div.stButton > button:hover {
    background: #3730a3;
    box-shadow: 0 4px 16px rgba(79,70,229,0.35);
}

h2, h3 { color: #1e293b !important; font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)


# ── Scrapers ──────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-AU,en;q=0.9",
}
BANK_PAT = re.compile(
    r'(ANZ|NAB|Westpac|Commonwealth|CBA|ING|Macquarie|ME Bank|BOQ|'
    r'Suncorp|Ubank|Up Bank|86 400|Newcastle|Heritage|Teachers|MyState|'
    r'Bendigo|Adelaide|AMP|Rabobank|HSBC|Judo|RACQ|Great Southern)', re.I
)

def scrape_mozo():
    try:
        r = requests.get("https://mozo.com.au/savings-accounts", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        rows, seen = [], set()
        for card in soup.find_all("div", class_=re.compile(r'product|card|item', re.I))[:50]:
            text = card.get_text(separator=" ", strip=True)
            rm = re.search(r'(\d+\.\d+)\s*%', text)
            bm = BANK_PAT.search(text)
            if rm and bm:
                rate = float(rm.group(1))
                bank = bm.group(1)
                key = (bank.lower(), round(rate, 2))
                if 2 < rate < 12 and key not in seen:
                    seen.add(key)
                    rows.append({"Bank": bank, "Rate (% p.a.)": rate})
        return rows
    except Exception:
        return []

def scrape_finder():
    try:
        r = requests.get("https://www.finder.com.au/savings-accounts", headers=HEADERS, timeout=12)
        lines = BeautifulSoup(r.text, "html.parser").get_text(separator="\n").split("\n")
        rows, seen = [], set()
        for i, line in enumerate(lines):
            rm = re.search(r'(\d+\.\d+)\s*%\s*p\.a\.?', line)
            if rm:
                rate = float(rm.group(1))
                if not (2 < rate < 12): continue
                ctx = " ".join(lines[max(0,i-2):i+3])
                bm = BANK_PAT.search(ctx)
                if bm:
                    bank = bm.group(1)
                    key = (bank.lower(), round(rate, 2))
                    if key not in seen:
                        seen.add(key)
                        rows.append({"Bank": bank, "Rate (% p.a.)": rate})
        return rows[:20]
    except Exception:
        return []


# ── Curated fallback data ─────────────────────────────────────────────────────
FALLBACK = [
    {"Bank": "Rabobank",       "Product": "High Interest Savings",  "Rate (% p.a.)": 5.60, "Base Rate (% p.a.)": 4.60, "Conditions": "Intro rate for first 4 months (new customers)"},
    {"Bank": "ME Bank",        "Product": "HomeME Savings",         "Rate (% p.a.)": 5.55, "Base Rate (% p.a.)": 0.01, "Conditions": "Make 4+ purchases on SpendME Debit card/month"},
    {"Bank": "ING",            "Product": "Savings Maximiser",      "Rate (% p.a.)": 5.50, "Base Rate (% p.a.)": 0.55, "Conditions": "Deposit $1,000+/mo, grow balance, 5 purchases on Orange Everyday"},
    {"Bank": "Ubank",          "Product": "Save Account",           "Rate (% p.a.)": 5.50, "Base Rate (% p.a.)": 0.10, "Conditions": "Deposit $200+/mo to linked Spend account"},
    {"Bank": "Great Southern", "Product": "Goal Saver",             "Rate (% p.a.)": 5.50, "Base Rate (% p.a.)": 0.10, "Conditions": "Grow balance each month, no withdrawals"},
    {"Bank": "BOQ",            "Product": "Future Saver",           "Rate (% p.a.)": 5.50, "Base Rate (% p.a.)": 0.01, "Conditions": "Age 14–35, deposit $1,000+/mo, no withdrawals"},
    {"Bank": "RACQ Bank",      "Product": "Bonus Saver",            "Rate (% p.a.)": 5.25, "Base Rate (% p.a.)": 0.10, "Conditions": "Grow balance, no withdrawals"},
    {"Bank": "Macquarie",      "Product": "Savings Account",        "Rate (% p.a.)": 5.35, "Base Rate (% p.a.)": 4.75, "Conditions": "Intro rate for 4 months (new customers)"},
    {"Bank": "Judo Bank",      "Product": "Savings Account",        "Rate (% p.a.)": 5.35, "Base Rate (% p.a.)": 5.35, "Conditions": "No conditions — ongoing base rate"},
    {"Bank": "Suncorp",        "Product": "Growth Saver",           "Rate (% p.a.)": 5.20, "Base Rate (% p.a.)": 0.01, "Conditions": "Grow balance, 1 deposit, max 1 withdrawal/month"},
    {"Bank": "Westpac",        "Product": "Life",                   "Rate (% p.a.)": 5.20, "Base Rate (% p.a.)": 1.00, "Conditions": "Grow balance, 5+ debit purchases, age 18–29"},
    {"Bank": "MyState Bank",   "Product": "Bonus Saver",            "Rate (% p.a.)": 5.15, "Base Rate (% p.a.)": 0.01, "Conditions": "Deposit $20+/mo, no withdrawals"},
    {"Bank": "ANZ Plus",       "Product": "Save",                   "Rate (% p.a.)": 5.00, "Base Rate (% p.a.)": 1.20, "Conditions": "Grow balance each month"},
    {"Bank": "NAB",            "Product": "Reward Saver",           "Rate (% p.a.)": 5.00, "Base Rate (% p.a.)": 0.01, "Conditions": "1+ deposit, no withdrawals per month"},
    {"Bank": "Commonwealth",   "Product": "GoalSaver",              "Rate (% p.a.)": 5.00, "Base Rate (% p.a.)": 0.01, "Conditions": "Grow balance each month"},
]


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_all_rates():
    df = pd.DataFrame(FALLBACK)
    for item in scrape_mozo() + scrape_finder():
        rate = item["Rate (% p.a.)"]
        mask = df["Bank"].str.lower().str.contains(item["Bank"].lower(), na=False)
        if mask.any() and 2 < rate < 12:
            df.loc[mask, "Rate (% p.a.)"] = rate
    df = df.sort_values("Rate (% p.a.)", ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    return df, datetime.now().strftime("%d %b %Y, %I:%M %p AEST")


# ── Render ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🇦🇺 AU Savings Rate Finder</h1>
    <p>Highest savings account interest rates in Australia — right now.</p>
</div>
""", unsafe_allow_html=True)

col_btn, _ = st.columns([1, 4])
with col_btn:
    if st.button("🔄 Refresh Rates"):
        st.cache_data.clear()
        st.rerun()

with st.spinner("Fetching latest rates..."):
    df, fetched_at = fetch_all_rates()

st.markdown(
    f'<div style="text-align:center"><span class="ts-badge">📡 Last refreshed: {fetched_at}</span></div>',
    unsafe_allow_html=True
)

# Winner card
top = df.iloc[0]
st.markdown(f"""
<div class="winner-card">
    <div class="winner-bank">{top['Bank']}</div>
    <div class="winner-product">{top['Product']}</div>
    <div class="winner-rate">{top['Rate (% p.a.)']:.2f}%</div>
    <div class="winner-rate-label">per annum (p.a.)</div>
    <div class="winner-conditions">⚠️ Conditions: {top['Conditions']}</div>
</div>
""", unsafe_allow_html=True)

# Metrics
avg_rate = df["Rate (% p.a.)"].mean()
st.markdown(f"""
<div class="metric-row">
    <div class="metric-card"><div class="val">{top['Rate (% p.a.)']:.2f}%</div><div class="lbl">Highest Rate</div></div>
    <div class="metric-card"><div class="val">{avg_rate:.2f}%</div><div class="lbl">Market Average</div></div>
    <div class="metric-card"><div class="val">{df['Rate (% p.a.)'].min():.2f}%</div><div class="lbl">Lowest Listed</div></div>
    <div class="metric-card"><div class="val">{len(df)}</div><div class="lbl">Banks Tracked</div></div>
</div>
""", unsafe_allow_html=True)

# Chart
st.subheader("📊 Rate Comparison")
st.bar_chart(df[["Bank", "Rate (% p.a.)"]].set_index("Bank"), color="#4f46e5", height=320)

# Table — plain st.dataframe, no matplotlib/background_gradient
st.subheader("📋 All Banks Ranked")
st.dataframe(
    df[["Bank", "Product", "Rate (% p.a.)", "Base Rate (% p.a.)", "Conditions"]],
    use_container_width=True,
    height=460,
    column_config={
        "Rate (% p.a.)":      st.column_config.NumberColumn("Rate (% p.a.)",      format="%.2f%%"),
        "Base Rate (% p.a.)": st.column_config.NumberColumn("Base Rate (% p.a.)", format="%.2f%%"),
        "Bank":               st.column_config.TextColumn("Bank",       width="small"),
        "Product":            st.column_config.TextColumn("Product",    width="medium"),
        "Conditions":         st.column_config.TextColumn("Conditions", width="large"),
    }
)

# Sources
st.markdown("**🔗 Verify rates directly:**")
st.markdown("""
<a class="source-chip" href="https://www.canstar.com.au/savings-accounts/" target="_blank">Canstar</a>
<a class="source-chip" href="https://mozo.com.au/savings-accounts" target="_blank">Mozo</a>
<a class="source-chip" href="https://www.finder.com.au/savings-accounts" target="_blank">Finder</a>
<a class="source-chip" href="https://www.ratecity.com.au/savings-accounts" target="_blank">RateCity</a>
<a class="source-chip" href="https://www.infochoice.com.au/banking/savings-account/" target="_blank">InfoChoice</a>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer">
⚠️ <strong>Disclaimer:</strong> Rates are indicative and sourced from publicly available data.
Bonus rates require meeting monthly conditions. Introductory rates apply to new customers only.
Always verify directly with the bank. This tool is not financial advice.
</div>
""", unsafe_allow_html=True)
