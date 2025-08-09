import os
import re
import requests
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urlparse
import json

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
    """Download page and extract ingredients section with multiple strategies"""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Strategy 1: Look for common ingredient section patterns
        patterns = [
            r"ingredients?",
            r"ingredient list",
            r"composition",
            r"full ingredients?",
            r"what[’']?s in it",
            r"key ingredients",
            r"active ingredients",
            r"contains",
            r"ingrédients?",
            r"ingredientes"
        ]
        
        # Check for hidden elements (common in e-commerce sites)
        hidden_selectors = [
            '[class*="ingredient"]',
            '[id*="ingredient"]',
            '[class*="composition"]',
            '[id*="composition"]',
            '[data-testid="ingredients"]',
            '[itemprop="ingredients"]'
        ]
        
        # Strategy 2: Look for hidden elements with common class/id patterns
        for selector in hidden_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(separator=", ", strip=True)
                if len(text) > 50 and "," in text:
                    return text
        
        # Strategy 3: Look for headings with ingredient keywords
        for pattern in patterns:
            heading = soup.find(
                re.compile("^h[1-6]$|^div$|^section$|^span$|^p$", re.I),
                string=re.compile(pattern, re.I)
            )
            if heading:
                # Look in adjacent elements
                for sibling in [heading.find_next_sibling(), heading.parent]:
                    if sibling:
                        text = sibling.get_text(separator=", ", strip=True)
                        if len(text) > 50 and "," in text:
                            return text
        
        # Strategy 4: Look for common data structures
        common_structures = [
            {"name": "meta", "attrs": {"name": "ingredients"}},
            {"name": "meta", "attrs": {"property": "ingredients"}},
            {"name": "script", "attrs": {"type": "application/ld+json"}}
        ]
        
        for structure in common_structures:
            elements = soup.find_all(**structure)
            for element in elements:
                text = element.get_text(separator=", ", strip=True)
                if "ingredients" in text.lower() and len(text) > 50:
                    # Try to extract from JSON-LD
                    if "application/ld+json" in element.get("type", ""):
                        try:
                            data = json.loads(text)
                            if isinstance(data, dict) and "ingredients" in data:
                                return data["ingredients"]
                            elif isinstance(data, list):
                                for item in data:
                                    if "ingredients" in item:
                                        return item["ingredients"]
                        except:
                            pass
                    return text
        
        # Strategy 5: Look for tables with ingredient information
        tables = soup.find_all("table")
        for table in tables:
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if "ingredient" in " ".join(headers):
                ingredients = []
                for row in table.find_all("tr"):
                    cells = row.find_all("td")
                    if cells:
                        ingredient = cells[0].get_text(strip=True)
                        if ingredient and len(ingredient) > 2:
                            ingredients.append(ingredient)
                if ingredients:
                    return ", ".join(ingredients)
        
        # Strategy 6: Fallback to regex search
        body_text = soup.get_text(separator=" ", strip=True)
        match = re.search(
            r"(?:ingredients?|composition|contains)[\s:]*([\w\s,()\-/]+\.?)(?:\n|$)",
            body_text, 
            re.IGNORECASE | re.DOTALL
        )
        if match:
            possible = match.group(1)
            if len(possible) > 50 and "," in possible:
                return possible

        return None
    except Exception as e:
        logger.error(f"Failed to extract ingredients: {str(e)}")
        return None

def clean_ingredient_text(raw_text: str) -> str:
    """Clean and normalize ingredient text for all products"""
    if not raw_text:
        return ""
    
    # Remove HTML tags if any
    raw_text = re.sub(r"<[^>]+>", "", raw_text)
    
    # Normalize separators
    raw_text = re.sub(r"[\n\t•*▪➢–—/]", ",", raw_text)
    
    # Remove numbers and percentages
    raw_text = re.sub(r"\d+%?", "", raw_text)
    
    # Remove anything in parentheses except preservatives
    raw_text = re.sub(r"\((?!phenoxyethanol|benzyl alcohol|paraben|chlorphenesin)[^)]*\)", "", raw_text)
    
    # Remove trademark symbols
    raw_text = raw_text.replace("™", "").replace("®", "")
    
    # Remove common non-ingredient text
    stop_phrases = [
        "product type", "company", "shop", "medicine",
        "hair care", "baby care", "cosmetics", "contact",
        "terms", "refund", "policy", "track", "copyright",
        "cart", "mailing list", "disclaimer", "cruelty free",
        "vegan", "organic", "natural", "synthetic", "size"
    ]
    
    for phrase in stop_phrases:
        raw_text = re.sub(phrase, "", raw_text, flags=re.IGNORECASE)
    
    # Remove excessive whitespace
    raw_text = re.sub(r"\s{2,}", " ", raw_text)
    
    # Remove leading/trailing commas and spaces
    raw_text = re.sub(r"^[\s,]+|[\s,]+$", "", raw_text)
    
    # Standardize capitalization
    ingredients = [ing.strip().title() for ing in raw_text.split(",") if ing.strip()]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_ingredients = []
    for ing in ingredients:
        if ing not in seen:
            seen.add(ing)
            unique_ingredients.append(ing)
    
    return ", ".join(unique_ingredients)

def get_ingredients_by_product_name(product_name):
    """Find product ingredients with intelligent search"""
    # Try brand-specific searches first
    brands = {
        "the ordinary": "site:deciem.com",
        "cerave": "site:cerave.com",
        "la roche-posay": "site:laroche-posay.com",
        "neutrogena": "site:neutrogena.com",
        "paula's choice": "site:paulaschoice.com"
    }
    
    # Check if product belongs to a known brand
    brand_query = ""
    for brand, site in brands.items():
        if brand in product_name.lower():
            brand_query = site
            break
    
    query = f"{product_name} ingredients {brand_query}"
    logger.info("Searching for: %s", query)
    
    results = search_google_cse(query)
    if not results:
        # Fallback to generic search
        query = f"{product_name} ingredients"
        results = search_google_cse(query)
        if not results:
            logger.warning("No search results found.")
            return None, None
    
    # Try each result until we find ingredients
    for result in results:
        top_url = result["link"]
        logger.info("Trying URL: %s", top_url)
        raw_ingredients = extract_ingredients_from_url(top_url)
        
        if raw_ingredients:
            cleaned = clean_ingredient_text(raw_ingredients)
            if cleaned and len(cleaned) > 20:
                logger.info("Successfully extracted ingredients")
                return cleaned, top_url
    
    logger.warning("No ingredients found in any results")
    return None, None