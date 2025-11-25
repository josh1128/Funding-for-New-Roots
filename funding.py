import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="New Roots CLT Grant Finder", layout="wide")
st.title("📌 New Roots CLT – Automated Grant Finder (Enhanced Version)")
st.write("This dashboard automatically scrapes funding opportunities from multiple Canadian sources.")

# --------------------------------------------------------
# Utility function: Safe Request
# --------------------------------------------------------

def safe_get(url):
    """Returns page content or None if blocked/failed."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.text
        return None
    except:
        return None


# --------------------------------------------------------
# SCRAPERS
# --------------------------------------------------------

def scrape_chrc():
    """ Community Housing Transformation Centre """
    url = "https://www.communityhousingtransformation.ca/"
    html = safe_get(url)
    if html is None: 
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for item in soup.find_all("div", class_="views-row"):
        title_tag = item.find("a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = "https://www.communityhousingtransformation.ca" + title_tag["href"]
        grants.append({
            "Source": "CHTC",
            "Title": title,
            "Deadline": "Varies",
            "Amount": "Varies",
            "Category": "Housing / Capacity Building",
            "Link": link
        })
    return grants


def scrape_red_cross():
    """ Red Cross Community Grants """
    url = "https://www.redcross.ca/how-we-help/emergencies-and-disasters-in-canada/financial-assistance"
    html = safe_get(url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for li in soup.find_all("li"):
        text = li.get_text(" ", strip=True)
        if "fund" in text.lower() or "grant" in text.lower():
            link = li.find("a")["href"] if li.find("a") else None
            grants.append({
                "Source": "Red Cross",
                "Title": text,
                "Deadline": "Varies",
                "Amount": "Varies",
                "Category": "Community Resilience / Youth",
                "Link": link
            })
    return grants


def scrape_cmhc_seed():
    """ CMHC Seed Funding """
    url = "https://www.cmhc-schl.gc.ca/en/financing-and-funding/funding-programs/all-funding-programs/seed-funding"
    html = safe_get(url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("h1").get_text(strip=True)
    return [{
        "Source": "CMHC",
        "Title": title,
        "Deadline": "Ongoing",
        "Amount": "Up to $350K (varies)",
        "Category": "Affordable Housing",
        "Link": url
    }]


def scrape_cmhc_co_invest():
    """ CMHC Co-Investment Fund """
    url = "https://www.cmhc-schl.gc.ca/en/financing-and-funding/funding-programs/co-investment-fund"
    html = safe_get(url)
    if html is None:
        return []
    return [{
        "Source": "CMHC",
        "Title": "Co-Investment Fund",
        "Deadline": "Ongoing",
        "Amount": "Large capital funding",
        "Category": "Affordable Housing / Construction",
        "Link": url
    }]


def scrape_infrastructure_canada():
    """ Infrastructure Canada Programs """
    url = "https://www.infrastructure.gc.ca/plan/programs-eng.html"
    html = safe_get(url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for li in soup.find_all("li"):
        if li.find("a"):
            title = li.get_text(strip=True)
            link = li.find("a")["href"]
            grants.append({
                "Source": "Infrastructure Canada",
                "Title": title,
                "Deadline": "Varies",
                "Amount": "Infrastructure funding",
                "Category": "Infrastructure / Community",
                "Link": link
            })
    return grants


def scrape_hrm_grants():
    """ HRM Community Grants """
    url = "https://www.halifax.ca/community/community-grants"
    html = safe_get(url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for a in soup.find_all("a"):
        title = a.get_text(strip=True)
        link = a["href"]
        if "grant" in title.lower():
            grants.append({
                "Source": "HRM",
                "Title": title,
                "Deadline": "Varies",
                "Amount": "Varies",
                "Category": "Municipal / Community",
                "Link": link
            })
    return grants


def scrape_united_way_halifax():
    """ United Way Halifax """
    url = "https://www.unitedwayhalifax.ca/"
    html = safe_get(url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for a in soup.find_all("a"):
        title = a.get_text(strip=True)
        if "grant" in title.lower() or "fund" in title.lower():
            link = a["href"]
            grants.append({
                "Source": "United Way Halifax",
                "Title": title,
                "Deadline": "Varies",
                "Amount": "Varies",
                "Category": "Community / Poverty Reduction",
                "Link": link
            })
    return grants


def scrape_cfc():
    """ Community Foundations of Canada """
    url = "https://communityfoundations.ca/news/"
    html = safe_get(url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for item in soup.find_all("h3"):
        title = item.get_text(strip=True)
        if "grant" in title.lower() or "fund" in title.lower():
            parent = item.find_parent("a")
            link = parent["href"] if parent else None
            grants.append({
                "Source": "CFC",
                "Title": title,
                "Deadline": "Varies",
                "Amount": "Varies",
                "Category": "Community / National",
                "Link": link
            })
    return grants


def scrape_google_org():
    """ Google.org Community Grants """
    url = "https://www.google.org/"
    html = safe_get(url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for card in soup.find_all("a"):
        text = card.get_text(strip=True)
        if "grant" in text.lower() or "fund" in text.lower():
            grants.append({
                "Source": "Google.org",
                "Title": text,
                "Deadline": "Varies",
                "Amount": "Large philanthropic grants",
                "Category": "Tech / Community / Equity",
                "Link": "https://www.google.org/"
            })
    return grants


def scrape_td_ready_commitment():
    """ TD Bank - Ready Commitment Grants """
    url = "https://www.td.com/ca/en/about-td/ready-commitment/funding"
    html = safe_get(url)
    if html is None:
        return []
    return [{
        "Source": "TD Ready Commitment",
        "Title": "TD Community Grants",
        "Deadline": "Varies",
        "Amount": "Varies",
        "Category": "Community / Equity",
        "Link": url
    }]


def scrape_rbc_foundation():
    """ RBC Foundation Grants """
    url = "https://www.rbc.com/community-social-impact/programs.html"
    html = safe_get(url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    grants = []
    for a in soup.find_all("a"):
        title = a.get_text(strip=True)
        if "grant" in title.lower() or "fund" in title.lower():
            grants.append({
                "Source": "RBC Foundation",
                "Title": title,
                "Deadline": "Varies",
                "Amount": "Varies",
                "Category": "Youth / Community / Equity",
                "Link": a["href"]
            })
    return grants


def scrape_vancity():
    """ Vancity Grants """
    url = "https://www.vancity.com/AboutVancity/Community"
    html = safe_get(url)
    if html is None:
        return []
    return [{
        "Source": "Vancity",
        "Title": "Vancity Community Grants",
        "Deadline": "Varies",
        "Amount": "Varies",
        "Category": "Community / Social Impact",
        "Link": url
    }]


# --------------------------------------------------------
# LOAD EVERYTHING
# --------------------------------------------------------
@st.cache_data(ttl=7200)
def load_all():
    df = pd.DataFrame([
        *scrape_chrc(),
        *scrape_red_cross(),
        *scrape_cmhc_seed(),
        *scrape_cmhc_co_invest(),
        *scrape_infrastructure_canada(),
        *scrape_hrm_grants(),
        *scrape_united_way_halifax(),
        *scrape_cfc(),
        *scrape_google_org(),
        *scrape_td_ready_commitment(),
        *scrape_rbc_foundation(),
        *scrape_vancity(),
    ])
    return df

df = load_all()

# --------------------------------------------------------
# FILTERS
# --------------------------------------------------------
st.sidebar.header("🔍 Filters")

keyword = st.sidebar.text_input("Search keyword")

source_filter = st.sidebar.multiselect("Filter by Source", df["Source"].unique(), df["Source"].unique())
category_filter = st.sidebar.multiselect("Filter by Category", df["Category"].unique(), df["Category"].unique())

results = df[
    (df["Source"].isin(source_filter)) & 
    (df["Category"].isin(category_filter))
]

if keyword:
    results = results[results["Title"].str.contains(keyword, case=False)]

# --------------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------------
st.subheader("📑 Funding Opportunities")
st.dataframe(results, use_container_width=True)

st.download_button(
    "📥 Download CSV",
    results.to_csv(index=False),
    "new_roots_grants.csv"
)

