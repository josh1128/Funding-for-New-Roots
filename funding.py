import streamlit as st
import pandas as pd
from datetime import datetime
import re

st.set_page_config(page_title="New Roots CLT Grant Scanner", layout="wide")
st.title("📌 New Roots CLT – Future Grants Finder (Post-2026 Only)")

# ----------------------------
# KEYWORD FILTERS (New Roots)
# ----------------------------
NEW_ROOTS_KEYWORDS = [
    "anti-black", "anti black", "anti racism", "anti-racism", "black communities",
    "BIPOC", "African Nova Scotian", "diaspora", "racial equity", "equity",

    "financial literacy", "economic empowerment", "business development",
    "entrepreneurship", "capacity building",

    "affordable housing", "housing", "community land trust", "CLT",
    "mixed-income", "mixed-use", "acquisition", "pre-development",
    "neighbourhood", "community development",

    "climate", "resilience", "sustainable", "green", "environment",

    "youth", "youth leadership", "community engagement"
]

# ----------------------------
# DATE PARSER
# ----------------------------
def extract_deadline(text):
    if not text:
        return None

    patterns = [
        r"([A-Za-z]+\s+\d{1,2},\s*\d{4})",
        r"(\d{4}-\d{2}-\d{2})"
    ]

    for p in patterns:
        match = re.search(p, text)
        if match:
            value = match.group(1)
            try:
                return datetime.strptime(value, "%B %d, %Y")
            except:
                try:
                    return datetime.strptime(value, "%Y-%m-%d")
                except:
                    return None
    return None

# ----------------------------
# LOAD SCRAPED DATA
# ----------------------------
@st.cache_data(ttl=3600)
def load_all():
    # Use your expanded scraping code here (CHTC, CMHC, HRM, etc.)
    from grant_scrapers import scrape_all_sources  # You can modularize
    df = scrape_all_sources()

    # Parse deadlines
    df["Deadline_Date"] = df["Deadline"].apply(extract_deadline)

    # Keep only grants with real dates
    df = df.dropna(subset=["Deadline_Date"])

    # Future-only (post-2026)
    cutoff = datetime(2026, 1, 1)
    df = df[df["Deadline_Date"] >= cutoff]

    # Apply New Roots keyword filtering
    def matches(grant):
        text = (grant["Title"] + " " + grant.get("Description", "")).lower()
        return any(kw in text for kw in NEW_ROOTS_KEYWORDS)

    df = df[df.apply(matches, axis=1)]

    return df

df = load_all()

# ----------------------------
# DISPLAY
# ----------------------------
st.subheader("🔎 Future Funding Opportunities (Aligned to New Roots Priorities)")
st.write("Filtered to **post-January 2026** and **relevant themes** such as anti-Black racism, financial literacy, ANS community, housing equity, youth, and climate resilience.")

st.dataframe(df, use_container_width=True, hide_index=True)

st.download_button("📥 Download CSV", df.to_csv(index=False), "new_roots_future_grants.csv")
