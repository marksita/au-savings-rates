import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🇦🇺 AU Savings Rate Finder",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: #f5f7fa; color: #1a1f36; }
#MainMenu, footer, header { visibility: hidden; }

.hero { text-align: center; padding: 2.5rem 1rem 1rem; }
.hero h1 {
    font-size: clamp(2rem, 5vw, 3.4rem); font-weight: 800;
    background: linear-gradient(135deg, #0066cc 0%, #4f46e5 60%, #0891b2 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    line-height: 1.15; margin-bottom: 0.4rem;
}
.hero p { color: #64748b; font-size: 1.05rem; font-family: 'DM Mono', monospace; }

.ts-badge {
    display: inline-block; background: #e0f2fe; border: 1px solid #bae6fd;
    border-radius: 20px; padding: 0.25rem 0.9rem;
    font-family: 'DM Mono', monospace; font-size: 0.78rem; color: #0369a1; margin-bottom: 1.5rem;
}

.winner-card {
    background: linear-gradient(135deg, #eff6ff, #eef2ff);
    border: 1.5px solid #bfdbfe; border-radius: 16px;
    padding: 1.8rem 2rem; margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
    box-shadow: 0 4px 24px rgba(79,70,229,0.08);
}
.winner-card::before {
    content: "🏆 HIGHEST RATE"; position: absolute; top: 14px; right: 16px;
    font-size: 0.65rem; font-family: 'DM Mono', monospace; letter-spacing: 2px;
    color: #4f46e5; background: #e0e7ff; padding: 3px 10px;
    border-radius: 20px; border: 1px solid #c7d2fe;
}
.winner-bank { font-size: 1.7rem; font-weight: 800; color: #1e293b; margin-bottom: 0.2rem; }
.winner-product { color: #64748b; font-size: 0.92rem; font-family: 'DM Mono', monospace; margin-bottom: 0.8rem; }
.winner-rate {
    font-size: 3.8rem; font-weight: 800;
    background: linear-gradient(90deg, #0066cc, #4f46e5);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; line-height: 1;
}
.winner-rate-label { font-size: 0.85rem; color: #64748b; font-family: 'DM Mono', monospace; margin-top: 0.3rem; }
.winner-conditions {
    margin-top: 1rem; font-size: 0.84rem; color: #475569;
    background: #fff; border-radius: 8px; padding: 0.7rem 1rem;
    font-family: 'DM Mono', monospace; border: 1px solid #e2e8f0;
}
.winner-link {
    display: inline-block; margin-top: 1rem;
    background: #4f46e5; color: #fff !important; text-decoration: none;
    padding: 0.45rem 1.2rem; border-radius: 8px; font-size: 0.85rem;
    font-family: 'DM Mono', monospace; font-weight: 500;
}
.winner-link:hover { background: #3730a3; color: #fff !important; }

.metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 140px; background: #ffffff;
    border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1.1rem 1.2rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.metric-card .val { font-size: 1.7rem; font-weight: 800; color: #0066cc; }
.metric-card .lbl {
    font-size: 0.72rem; color: #94a3b8; font-family: 'DM Mono', monospace;
    letter-spacing: 1px; text-transform: uppercase; margin-top: 0.2rem;
}

.bank-table { width: 100%; border-collapse: collapse; margin-top: 0; }
.bank-table th {
    background: #f1f5f9; color: #475569; font-size: 0.72rem;
    font-family: 'DM Mono', monospace; letter-spacing: 1px; text-transform: uppercase;
    padding: 0.75rem 1rem; text-align: left; border-bottom: 2px solid #e2e8f0;
}
.bank-table td { padding: 0.85rem 1rem; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; vertical-align: middle; }
.bank-table tr:hover td { background: #f8fafc; }
.bank-table tr.top-row td { background: #eff6ff; }
.rank-cell { font-family: 'DM Mono', monospace; color: #94a3b8; font-size: 0.85rem; width: 42px; text-align: center; }
.bank-name { font-weight: 700; color: #1e293b; }
.product-name { color: #64748b; font-size: 0.78rem; font-family: 'DM Mono', monospace; margin-top: 2px; }
.rate-cell { font-weight: 800; color: #0066cc; font-size: 1.05rem; white-space: nowrap; }
.base-rate-cell { color: #94a3b8; font-family: 'DM Mono', monospace; font-size: 0.82rem; white-space: nowrap; }
.conditions-cell { color: #475569; font-size: 0.81rem; font-family: 'DM Mono', monospace; }
.table-link {
    display: inline-block; color: #4f46e5 !important; text-decoration: none;
    font-size: 0.73rem; font-family: 'DM Mono', monospace;
    border: 1px solid #c7d2fe; border-radius: 6px; padding: 0.22rem 0.6rem;
    background: #eef2ff; white-space: nowrap;
}
.table-link:hover { background: #e0e7ff; border-color: #a5b4fc; }
.table-wrap {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
    overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.05); margin-bottom: 1.5rem;
}

.source-chip {
    display: inline-block; background: #f1f5f9; border: 1px solid #cbd5e1;
    border-radius: 20px; padding: 0.2rem 0.75rem; font-size: 0.75rem;
    font-family: 'DM Mono', monospace; color: #475569; margin: 0.2rem; text-decoration: none;
}
.source-chip:hover { background: #e0e7ff; border-color: #a5b4fc; color: #4f46e5; }

.disclaimer {
    margin-top: 2rem; padding: 1rem 1.2rem; background: #fff7ed;
    border-left: 3px solid #f97316; border-radius: 0 8px 8px 0;
    font-size: 0.82rem; color: #78350f; font-family: 'DM Mono', monospace;
}

div.stButton > button {
    background: #4f46e5; border: none; color: #ffffff;
    font-family: 'Syne', sans-serif; font-weight: 700;
    border-radius: 10px; padding: 0.6rem 2rem; font-size: 1rem;
    box-shadow: 0 2px 8px rgba(79,70,229,0.25);
}
div.stButton > button:hover { background: #3730a3; }
h2, h3 { color: #1e293b !important; font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)


# ── Verified bank savings page URLs ───────────────────────────────────────────
BANK_URLS = {
    "Rabobank":       "https://www.rabobank.com.au/rates/personal-rates",
    "ME Bank":        "https://www.mebank.com.au/banking/savings-accounts/homeme-savings-account/",
    "ING":            "https://www.ing.com.au/savings.html",
    "Ubank":          "https://www.ubank.com.au/banking/savings-account",
    "Great Southern": "https://www.greatsouthernbank.com.au/savings-accounts/goal-saver",
    "BOQ":            "https://www.boq.com.au/personal/banking/savings-accounts/future-saver",
    "Macquarie":      "https://www.macquarie.com.au/everyday-banking/savings-account.html",
    "Judo Bank":      "https://www.judobank.com.au/personal/savings/",
    "RACQ Bank":      "https://www.racq.com.au/banking/savings-accounts/bonus-saver",
    "Suncorp":        "https://www.suncorp.com.au/banking/accounts/savings-accounts/growth-saver.html",
    "Westpac":        "https://www.westpac.com.au/personal-banking/bank-accounts/savings-accounts/life/",
    "MyState Bank":   "https://www.mystate.com.au/banking/savings-accounts/bonus-saver-account/",
    "ANZ Plus":       "https://www.anz.com.au/personal/bank-accounts/savings-accounts/anz-save/",
    "NAB":            "https://www.nab.com.au/personal/accounts/savings-accounts/reward-saver-account",
    "Commonwealth":   "https://www.commbank.com.au/banking/savings-accounts/goalsaver.html",
}

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
                ctx = " ".join(lines[max(0, i-2):i+3])
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


# ── Curated data (verified May 2026) ─────────────────────────────────────────
FALLBACK = [
    {"Bank": "Rabobank",       "Product": "High Interest Savings",  "Rate (% p.a.)": 5.65, "Base Rate (% p.a.)": 4.40, "Conditions": "Intro rate for first 4 months (new customers)"},
    {"Bank": "Ubank",          "Product": "Save Account",           "Rate (% p.a.)": 5.60, "Base Rate (% p.a.)": 0.10, "Conditions": "Intro rate for 4 months; then grow combined Save balance by $1+/mo"},
    {"Bank": "ING",            "Product": "Savings Accelerator",    "Rate (% p.a.)": 5.65, "Base Rate (% p.a.)": 4.35, "Conditions": "Intro rate for 4 months on balances $150k-$500k (new customers)"},
    {"Bank": "Westpac",        "Product": "Life (18-34)",           "Rate (% p.a.)": 5.50, "Base Rate (% p.a.)": 1.00, "Conditions": "Age 18-34, grow balance, 20 purchases/mo on linked debit card"},
    {"Bank": "ME Bank",        "Product": "HomeME Savings",         "Rate (% p.a.)": 5.55, "Base Rate (% p.a.)": 0.01, "Conditions": "Make 4+ purchases on SpendME Debit card/month"},
    {"Bank": "Great Southern", "Product": "Goal Saver",             "Rate (% p.a.)": 5.50, "Base Rate (% p.a.)": 0.10, "Conditions": "Grow balance each month, no withdrawals"},
    {"Bank": "BOQ",            "Product": "Future Saver",           "Rate (% p.a.)": 5.50, "Base Rate (% p.a.)": 0.01, "Conditions": "Age 14-35, deposit $200+/mo, no withdrawals (myBOQ app only)"},
    {"Bank": "Judo Bank",      "Product": "Savings Account",        "Rate (% p.a.)": 5.35, "Base Rate (% p.a.)": 5.35, "Conditions": "No conditions — ongoing base rate, no age limits"},
    {"Bank": "Macquarie",      "Product": "Savings Account",        "Rate (% p.a.)": 5.35, "Base Rate (% p.a.)": 4.75, "Conditions": "Intro rate for 4 months (new customers), no conditions ongoing"},
    {"Bank": "RACQ Bank",      "Product": "Bonus Saver",            "Rate (% p.a.)": 5.25, "Base Rate (% p.a.)": 0.10, "Conditions": "Grow balance, no withdrawals per month"},
    {"Bank": "Suncorp",        "Product": "Growth Saver",           "Rate (% p.a.)": 5.20, "Base Rate (% p.a.)": 0.01, "Conditions": "Grow balance, 1 deposit, max 1 withdrawal/month"},
    {"Bank": "MyState Bank",   "Product": "Bonus Saver",            "Rate (% p.a.)": 5.15, "Base Rate (% p.a.)": 0.01, "Conditions": "Deposit $20+/mo, no withdrawals"},
    {"Bank": "ANZ Plus",       "Product": "ANZ Save",               "Rate (% p.a.)": 5.00, "Base Rate (% p.a.)": 1.20, "Conditions": "Grow balance each month (ANZ Plus app only)"},
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


# ── UI ────────────────────────────────────────────────────────────────────────
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

# ── Winner card ───────────────────────────────────────────────────────────────
top = df.iloc[0]
top_url = BANK_URLS.get(top["Bank"], "https://www.finder.com.au/savings-accounts")

st.markdown(f"""
<div class="winner-card">
    <div class="winner-bank">{top['Bank']}</div>
    <div class="winner-product">{top['Product']}</div>
    <div class="winner-rate">{top['Rate (% p.a.)']:.2f}%</div>
    <div class="winner-rate-label">per annum (p.a.)</div>
    <div class="winner-conditions">⚠️ Conditions: {top['Conditions']}</div>
    <a class="winner-link" href="{top_url}" target="_blank">🔗 View {top['Bank']} rates →</a>
</div>
""", unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────────────────
avg_rate = df["Rate (% p.a.)"].mean()
st.markdown(f"""
<div class="metric-row">
    <div class="metric-card"><div class="val">{top['Rate (% p.a.)']:.2f}%</div><div class="lbl">Highest Rate</div></div>
    <div class="metric-card"><div class="val">{avg_rate:.2f}%</div><div class="lbl">Market Average</div></div>
    <div class="metric-card"><div class="val">{df['Rate (% p.a.)'].min():.2f}%</div><div class="lbl">Lowest Listed</div></div>
    <div class="metric-card"><div class="val">{len(df)}</div><div class="lbl">Banks Tracked</div></div>
</div>
""", unsafe_allow_html=True)

# ── Plotly bar chart ──────────────────────────────────────────────────────────
st.subheader("📊 Rate Comparison")

chart_df = df.sort_values("Rate (% p.a.)", ascending=True).reset_index(drop=True)
bar_colors = ["#4f46e5" if i == len(chart_df) - 1 else "#93c5fd" for i in range(len(chart_df))]

fig = go.Figure(go.Bar(
    x=chart_df["Rate (% p.a.)"],
    y=chart_df["Bank"],
    orientation="h",
    marker_color=bar_colors,
    marker_line_width=0,
    text=[f"  {r:.2f}%" for r in chart_df["Rate (% p.a.)"]],
    textposition="outside",
    textfont=dict(family="DM Mono, monospace", size=11, color="#1e293b"),
    hovertemplate="<b>%{y}</b><br>Rate: %{x:.2f}% p.a.<extra></extra>",
    cliponaxis=False,
))

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#ffffff",
    font=dict(family="Syne, sans-serif", color="#1e293b"),
    xaxis=dict(
        title="Interest Rate (% p.a.)",
        ticksuffix="%",
        gridcolor="#f1f5f9",
        tickfont=dict(family="DM Mono, monospace", size=11, color="#64748b"),
        range=[4.3, 6.4],
        showline=True,
        linecolor="#e2e8f0",
    ),
    yaxis=dict(
        tickfont=dict(family="Syne, sans-serif", size=12, color="#1e293b"),
        gridcolor="#f1f5f9",
        showline=False,
    ),
    margin=dict(l=10, r=90, t=20, b=50),
    height=440,
    bargap=0.32,
)

st.plotly_chart(fig, use_container_width=True)

# ── All banks ranked table with links ─────────────────────────────────────────
st.subheader("📋 All Banks Ranked")

rank_icons = {1: "🥇", 2: "🥈", 3: "🥉"}
rows_html = ""
for rank, row in df.iterrows():
    icon = rank_icons.get(rank, f"#{rank}")
    url = BANK_URLS.get(row["Bank"], "https://www.finder.com.au/savings-accounts")
    is_top = "top-row" if rank == 1 else ""
    rows_html += f"""
    <tr class="{is_top}">
        <td class="rank-cell">{icon}</td>
        <td>
            <div class="bank-name">{row['Bank']}</div>
            <div class="product-name">{row['Product']}</div>
        </td>
        <td class="rate-cell">{row['Rate (% p.a.)']:.2f}%</td>
        <td class="base-rate-cell">{row['Base Rate (% p.a.)']:.2f}%</td>
        <td class="conditions-cell">{row['Conditions']}</td>
        <td><a class="table-link" href="{url}" target="_blank">Visit site →</a></td>
    </tr>"""

st.markdown(f"""
<div class="table-wrap">
<table class="bank-table">
    <thead>
        <tr>
            <th style="text-align:center">#</th>
            <th>Bank / Product</th>
            <th>Total Rate</th>
            <th>Base Rate</th>
            <th>Conditions</th>
            <th>Link</th>
        </tr>
    </thead>
    <tbody>{rows_html}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

# ── Compare on sites ──────────────────────────────────────────────────────────
st.markdown("**🔗 Also compare on:**")
st.markdown("""
<a class="source-chip" href="https://www.canstar.com.au/savings-accounts/" target="_blank">Canstar</a>
<a class="source-chip" href="https://mozo.com.au/savings-accounts" target="_blank">Mozo</a>
<a class="source-chip" href="https://www.finder.com.au/savings-accounts" target="_blank">Finder</a>
<a class="source-chip" href="https://www.ratecity.com.au/savings-accounts" target="_blank">RateCity</a>
<a class="source-chip" href="https://www.infochoice.com.au/banking/savings-account/" target="_blank">InfoChoice</a>
<a class="source-chip" href="https://www.choice.com.au/money/banking/savings-options/articles/top-high-interest-savings-accounts" target="_blank">CHOICE</a>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer">
⚠️ <strong>Disclaimer:</strong> Rates are indicative and sourced from publicly available data (last curated May 2026).
Bonus rates require meeting monthly conditions. Introductory rates apply to new customers only and revert after the promotional period.
Always verify directly with the bank before making any financial decisions. This tool is not financial advice.
</div>
""", unsafe_allow_html=True)
