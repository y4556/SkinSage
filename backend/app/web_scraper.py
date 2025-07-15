import os
import re
import requests
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")

def search_google_cse(query, num_results=3):
    """Search Google CSE and return JSON results"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": num_results
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("items", [])

def extract_ingredients_from_url(url):
    """Download page and extract ingredients section"""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Try the known <summary> + <p> pattern first
        summary = soup.find("summary", attrs={"data-closed": "See Full Ingredient List"})
        if summary:
            p_tag = summary.find_next("p")
            if p_tag:
                text = p_tag.get_text(separator=" ", strip=True)
                if len(text) > 20 and "," in text:
                    return text

        # Heuristic heading search
        patterns = [
            r"ingredients?",
            r"ingredient list",
            r"composition",
            r"full ingredients?",
            r"what[’']?s in it",
            r"key ingredients",
            r"active ingredients"
        ]

        for pat in patterns:
            heading = soup.find(
                ["h2", "h3", "h4", "h5", "h6", "span", "div"],
                string=re.compile(pat, re.I)
            )
            if heading:
                next_el = heading.find_next_sibling()
                while next_el:
                    text = next_el.get_text(separator=" ", strip=True)
                    if len(text) > 50 and "," in text:
                        return text
                    next_el = next_el.find_next_sibling()

                parent = heading.find_parent(["div", "section", "article"])
                if parent:
                    text = parent.get_text(separator=" ", strip=True)
                    if len(text) > 100 and "," in text:
                        return text

        # Regex fallback
        body_text = soup.get_text(separator=" ", strip=True)
        match = re.search(r"Ingredients?\s*[:\-]?\s*(.*)", body_text, re.I)
        if match:
            possible = match.group(1)
            if len(possible) > 50 and "," in possible:
                return possible

        return None
    except Exception as e:
        logger.error(f"Failed to extract ingredients: {str(e)}")
        return None

def clean_ingredient_text(raw_text: str) -> str:
    """
    Truncates the text at the first occurrence of any stop keyword,
    preserving all text before it.
    """
    if not raw_text:
        return ""

    stop_keywords = [
        "product type", "company", "shop", "medicine",
        "hair care", "baby care", "cosmetics", "contact",
        "terms", "refund", "policy", "track", "copyright",
        "cart", "mailing list"
    ]

    text_lower = raw_text.lower()
    cutoff_index = len(raw_text)

    for keyword in stop_keywords:
        idx = text_lower.find(keyword)
        if idx != -1 and idx < cutoff_index:
            cutoff_index = idx

    cleaned = raw_text[:cutoff_index].strip()

    # Remove excessive whitespace
    cleaned = re.sub(r"\s{2,}", " ", cleaned)

    return cleaned


def get_ingredients_by_product_name(product_name):
    """Combine search and scrape with cleaning"""
    query = f"{product_name} ingredients"
    logger.info("Searching for: %s", query)
    results = search_google_cse(query)
    if not results:
        logger.warning("No search results found.")
        return None, None

    top_url = results[0]["link"]
    logger.info("Found URL: %s", top_url)
    raw_ingredients = extract_ingredients_from_url(top_url)
    cleaned = clean_ingredient_text(raw_ingredients)

    return cleaned, top_url


