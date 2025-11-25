import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re


# ------------------------------------------------------------
# STREAMLIT SETUP
# ------------------------------------------------------------
st.set_page_config(page_title="New Roots CLT Grant Scanner", layout="wide")
st.title("📌 New Roots CLT – Future Funding Opportunities (Post-2026)")
st.write("Automatically scraped, filtered by deadline, and matched to New Roots priorities.")


# ------------------------------------------------------------
# SAFE GET (avoids crashes if a site blocks request)
# ------------------------------------------------------------
def safe_get(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            return r.text
        return None
    except:
        return None


# ------------------------------------------------------------
# NEW ROOTS KEYWORDS (from strategy doc)
# ------------------------------------------------------------
NEW_ROOTS_KEYWORDS = [
    # Anti-Black racism / ANS
    "anti-black", "anti black", "african nova scotian", "ans", "black communities",
    "racial equity", "anti-racism", "equity", "inclusion", "diaspora",

    # Financial literacy + economic empowerment
    "financial literacy", "economic empowerment", "entrepreneurship",
    "business development", "capacity building", "economic prosperity",

    # Housing + CLT themes
    "affordable housing", "community land trust", "clt", "mixed-use",
    "mixed income", "housing", "acquisition", "pre-development",
    "community development", "neighbourhood", "urban renewal",

    # Youth + engagement
    "youth", "youth leadership", "community engagement",

    # Climate + green building
    "climate", "resilience", "sustainable", "green", "environment"
]


# ------------------------------------------------------------
# DEADLINE PARSER
# ------------------------------------------------------------
def extract_deadline(text):
    if not text:
        return None

    patterns = [
        r"([A-Za-z]+\s+\d{1,2},\s*\d{4})",  # January 5, 2027
        r"(\d{4}-\d{2}-\d{2})",            # 2026-02-15
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            value = m.group(1)
            try:
                return datetime.strptime(value, "%B %d, %Y")
            except:
                try:
                    return datetime.strptime(value, "%Y-%m-%d")
                except:
                    return None
    return None


# ------------------------------------------------------------
# SCRAPERS
# ------------------------------------------------------------

def scrape_chrc():
    url = "https://www.communityhousingtransformation.ca/"
    html = safe_get(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for g in soup.find_all("div", class_="views-row"):
        tag = g.find("a")
        if tag:
            grants.append({
                "Source": "CHTC",
                "Title": tag.get_text(strip=True),
                "Deadline": "Varies",
                "Description": "",
                "Amount": "Varies",
                "Category": "Housing / Capacity",
                "Link": "https://www.communityhousingtransformation.ca" + tag["href"]
            })
    return grants


def scrape_red_cross():
    url = "https://www.redcross.ca/how-we-help/emergencies-and-disasters-in-canada/financial-assistance"
    html = safe_get(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for li in soup.find_all("li"):
        text = li.get_text(" ", strip=True)
        if "grant" in text.lower() or "fund" in text.lower():
            link = li.find("a")["href"] if li.find("a") else None
            grants.append({
                "Source": "Red Cross",
                "Title": text,
                "Deadline": "Varies",
                "Description": text,
                "Amount": "Varies",
                "Category": "Community / Resilience",
                "Link": link
            })
    return grants


def scrape_cmhc_seed():
    url = "https://www.cmhc-schl.gc.ca/en/financing-and-funding/funding-programs/all-funding-programs/seed-funding"
    html = safe_get(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("h1").get_text(strip=True)
    return [{
        "Source": "CMHC",
        "Title": title,
        "Deadline": "Ongoing",
        "Description": "Seed Funding program for affordable housing.",
        "Amount": "Up to $350K",
        "Category": "Affordable Housing",
        "Link": url
    }]


def scrape_cmhc_co_invest():
    url = "https://www.cmhc-schl.gc.ca/en/financing-and-funding/funding-programs/co-investment-fund"
    return [{
        "Source": "CMHC",
        "Title": "Co-Investment Fund",
        "Deadline": "Ongoing",
        "Description": "Funding for major affordable housing projects.",
        "Amount": "Large capital funding",
        "Category": "Housing / Construction",
        "Link": url
    }]


def scrape_infrastructure_canada():
    url = "https://www.infrastructure.gc.ca/plan/programs-eng.html"
    html = safe_get(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for li in soup.find_all("li"):
        if li.find("a"):
            grants.append({
                "Source": "Infrastructure Canada",
                "Title": li.get_text(strip=True),
                "Deadline": "Varies",
                "Description": li.get_text(strip=True),
                "Amount": "Varies",
                "Category": "Infrastructure / Community",
                "Link": li.find("a")["href"]
            })
    return grants


def scrape_hrm():
    url = "https://www.halifax.ca/community/community-grants"
    html = safe_get(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        if "grant" in text.lower():
            grants.append({
                "Source": "HRM",
                "Title": text,
                "Deadline": "Varies",
                "Description": text,
                "Amount": "Varies",
                "Category": "Municipal Grants",
                "Link": a["href"]
            })
    return grants


def scrape_rbc():
    url = "https://www.rbc.com/community-social-impact/programs.html"
    html = safe_get(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for a in soup.find_all("a"):
        title = a.get_text(strip=True)
        if "fund" in title.lower() or "grant" in title.lower():
            grants.append({
                "Source": "RBC Foundation",
                "Title": title,
                "Deadline": "Varies",
                "Description": title,
                "Amount": "Varies",
                "Category": "Youth / Community",
                "Link": a["href"]
            })
    return grants


def scrape_td():
    return [{
        "Source": "TD Ready Commitment",
        "Title": "TD Community Grants",
        "Deadline": "Varies",
        "Description": "Funding for equity, financial literacy, and inclusion.",
        "Amount": "Varies",
        "Category": "Equity / Inclusion",
        "Link": "https://www.td.com/ca/en/about-td/ready-commitment/funding"
    }]


def scrape_vancity():
    return [{
        "Source": "Vancity",
        "Title": "Vancity Community Grants",
        "Deadline": "Varies",
        "Description": "Funding for community development and inclusion.",
        "Amount": "Varies",
        "Category": "Community",
        "Link": "https://www.vancity.com/AboutVancity/Community"
    }]


# ------------------------------------------------------------
# LOAD + FILTER ALL DATA
# ------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_all():

    data = []

    data.extend(scrape_chrc())
    data.extend(scrape_red_cross())
    data.extend(scrape_cmhc_seed())
    data.extend(scrape_cmhc_co_invest())
    data.extend(scrape_infrastructure_canada())
    data.extend(scrape_hrm())
    data.extend(scrape_rbc())
    data.extend(scrape_td())
    data.extend(scrape_vancity())

    df = pd.DataFrame(data)

    # Parse deadlines
    df["Deadline_Date"] = df["Deadline"].apply(extract_deadline)
    df = df.dropna(subset=["Deadline_Date"])

    # Only grants AFTER January 1, 2026
    cutoff = datetime(2026, 1, 1)
    df = df[df["Deadline_Date"] >= cutoff]

    # New Roots alignment filter
    def matches(grant):
        text = (grant["Title"] + " " + grant["Description"]).lower()
        return any(kw in text for kw in NEW_ROOTS_KEYWORDS)

    df = df[df.apply(matches, axis=1)]

    return df


df = load_all()


# ------------------------------------------------------------
# DISPLAY RESULTS
# ------------------------------------------------------------
st.subheader("🎯 Matched Grants (Post-Jan 2026 Only)")
st.dataframe(df, use_container_width=True, hide_index=True)

st.download_button(
    "📥 Download Results as CSV",
    df.to_csv(index=False),
    file_name="new_roots_future_grants.csv"
)
