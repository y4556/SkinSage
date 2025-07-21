import os
import re
import logging
import aiohttp
import base64
from dotenv import load_dotenv
from PIL import Image, ImageEnhance
import io

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OCR_API_KEY = os.getenv("OCR_SPACE_API_KEY")
OCR_URL = "https://api.ocr.space/parse/image"


async def extract_raw_text_from_image(image_bytes: bytes) -> str:
    """Extract raw text from image without processing"""
    try:
        if not OCR_API_KEY:
            logger.error("OCR_SPACE_API_KEY environment variable not set")
            raise RuntimeError("OCR API key missing")
            
        # Optimize image for better OCR results
        optimized_image = await optimize_image(image_bytes)
        base64_image = base64.b64encode(optimized_image).decode("utf-8")
        
        # Prepare OCR request
        payload = {
            "base64Image": f"data:image/jpeg;base64,{base64_image}",
            "language": "eng",
            "isOverlayRequired": False,
            "filetype": "JPG",
            "OCREngine": 2,
            "scale": True,
            "detectOrientation": True
        }
        
        headers = {"apikey": OCR_API_KEY}
        
        # Send to OCR API
        async with aiohttp.ClientSession() as session:
            async with session.post(OCR_URL, data=payload, headers=headers) as response:
                result = await response.json()
                
                if response.status != 200 or result.get("IsErroredOnProcessing", True):
                    error = result.get("ErrorMessage", "Unknown OCR error")
                    logger.error(f"OCR error: {error}")
                    raise RuntimeError("OCR processing failed")
                
                # Return raw text without any processing
                return result["ParsedResults"][0]["ParsedText"]
                
    except Exception as e:
        logger.error(f"Raw text extraction failed: {str(e)}")
        raise RuntimeError("Failed to extract raw text from image")

async def extract_ingredients(image_bytes: bytes) -> str:
    """Extract ingredients from product image using OCR"""
    try:
        if not OCR_API_KEY:
            logger.error("OCR_SPACE_API_KEY environment variable not set")
            raise RuntimeError("OCR API key missing")
        # Optimize and process image
        optimized_image = await optimize_image(image_bytes)
        base64_image = base64.b64encode(optimized_image).decode("utf-8")
        
        # Prepare OCR request
        payload = {
            "base64Image": f"data:image/jpeg;base64,{base64_image}",
            "language": "eng",
            "isOverlayRequired": False,
            "filetype": "JPG",
            "OCREngine": 2,
            "scale": True,
            "detectOrientation": True
        }
        
        headers = {
            "apikey": OCR_API_KEY,
        }
        
        # Send to OCR API
        async with aiohttp.ClientSession() as session:
            async with session.post(OCR_URL, data=payload, headers=headers) as response:
                result = await response.json()
                
                if response.status != 200 or result.get("IsErroredOnProcessing", True):
                    error = result.get("ErrorMessage", "Unknown OCR error")
                    logger.error(f"OCR error: {error}")
                    raise RuntimeError("OCR processing failed")
                
                full_text = result["ParsedResults"][0]["ParsedText"]
                return process_ingredients_text(full_text)
                
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise RuntimeError("Failed to extract ingredients")

async def optimize_image(image_bytes: bytes) -> bytes:
    """Optimize image for better OCR results"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        max_size = (1600, 1600)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        if image.mode != "L":
            image = image.convert("L")
        
        # Enhance image quality
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        output_buffer = io.BytesIO()
        image.save(output_buffer, format="JPEG", quality=90)
        return output_buffer.getvalue()
    except Exception as e:
        logger.warning(f"Image optimization failed: {str(e)}")
        return image_bytes

def process_ingredients_text(full_text: str) -> str:
    """Process OCR text to extract clean ingredients list"""
    # Patterns that indicate end of ingredients section
    END_MARKERS = [
        r'\n\s*\n',       # Blank line
        r' {2,}',         # Excessive spaces
        r'(?i)\b(?:distribut|product of|made in|www\.|http|Ml|Floz|g|oz)\b',  # Common end markers
    ]
    
    # Find the ingredients section
    ingredients_section = extract_ingredients_section(full_text)
    
    # Process each line until we hit an end marker
    lines = ingredients_section.split('\n')
    ingredients = []
    
    for line in lines:
        # Stop if we hit an end marker
        if any(re.search(marker, line) for marker in END_MARKERS):
            break
            
        # Clean and process the line
        cleaned = clean_ingredient_line(line)
        if cleaned:
            ingredients.extend(cleaned)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_ingredients = [x for x in ingredients if not (x in seen or seen.add(x))]
    
    # Apply advanced cleaning
    cleaned_ingredients = [clean_ingredient_name(ing) for ing in unique_ingredients]
    cleaned_ingredients = [ing for ing in cleaned_ingredients if ing and len(ing) > 2]
    
    return ', '.join(cleaned_ingredients)

def extract_ingredients_section(text: str) -> str:
    """Find the ingredients section in the OCR text"""
    # Common ingredient section headers
    headers = [
        "ingredients", "ingrédients", "ingredientes", "成分",
        "contains", "composants", "active ingredients"
    ]
    
    for header in headers:
        pattern = fr"{header}[:\s]*(.*?)(?:\n\n|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # Fallback: return entire text if no header found
    return text

def clean_ingredient_line(line: str) -> list[str]:
    """Clean a single line of potential ingredients"""
    # Remove unwanted content
    line = re.sub(r'\([^)]*\)', '', line)  # Remove parentheses
    line = re.sub(r'\d+%?', '', line)      # Remove numbers/percentages
    line = re.sub(r'[•\*▪➢–—]', ',', line) # Replace bullet points
    
    # Split by commas and clean each item
    ingredients = []
    for item in line.split(','):
        ingredient = item.strip()
        
        # Skip empty items and common non-ingredients
        if not ingredient or len(ingredient) < 3:
            continue
            
        # Standardize capitalization
        ingredient = ingredient.title()
        
        ingredients.append(ingredient)
    
    return ingredients

def clean_ingredient_name(ingredient: str) -> str:
    """Clean and standardize ingredient names"""
    # Remove special characters and brand names
    ingredient = re.sub(r'[:.,]', '', ingredient)
    
    # Common OCR misreadings correction
    corrections = {
        r"Glydern": "Glycerin",
        r"Centagaythrty": "Cetearyl",
        r"Tetraethyl Hexandate": "Ethylhexanoate",
        r"Propamediole": "Propanediol",
        r"Eumonium Polyarn On Dime Thyl Taurate": "Behentrimonium Methosulfate",
        r"Polysoreate": "Polysorbate",
        r"Co Ceramide Np": "Ceramide NP",
        r"Coco-Betane": "Cocamidopropyl Betaine",
        r"Fanthenol": "Panthenol",
        r"Ml - \. Floz\.": "",
        r"\bAqua\b": "Water",
        r"\bWater\b": "Water",
        r"\bEau\b": "Water"
    }
    
    for pattern, replacement in corrections.items():
        ingredient = re.sub(pattern, replacement, ingredient, flags=re.IGNORECASE)
    
    # Remove size information
    ingredient = re.sub(r"\d+\s*(ml|floz|g|oz)", "", ingredient, flags=re.IGNORECASE)
    
    return ingredient.strip()