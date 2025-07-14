import os
import json
import logging
import aiohttp
import re
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def extract_and_fix_json(text: str) -> dict:
    """Robust JSON extraction with advanced error correction"""
    try:
        # First try direct parsing
        return json.loads(text)
    except json.JSONDecodeError:
        logger.info("Attempting to repair malformed JSON")
        
        # Common JSON fixes
        text = re.sub(r",\s*}", "}", text)  # Remove trailing commas in objects
        text = re.sub(r",\s*]", "]", text)  # Remove trailing commas in arrays
        text = re.sub(r"\\'", "'", text)    # Fix escaped single quotes
        text = re.sub(r'\\"', '"', text)    # Fix escaped double quotes
        text = re.sub(r"(\w)\s*:\s*'", r'\1: "', text)  # Fix single quoted values
        text = re.sub(r"(\w)\s*:\s*(\w+)\s*([,\}])", r'\1: "\2"\3', text)  # Quote unquoted values
        
        # Find JSON boundaries
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == -1:
            raise ValueError("No JSON structure found")
        
        # Try to parse the extracted JSON
        try:
            return json.loads(text[start_idx:end_idx])
        except json.JSONDecodeError as e:
            logger.error(f"JSON repair failed: {str(e)}")
            raise

def fallback_analysis(ingredients: str = "") -> dict:
    """Fallback analysis when Groq API fails"""
    return {
        "overall_assessment": {
            "safety_rating": "caution",
            "barrier_impact": "neutral",
            "allergy_risk": "medium",
            "suitability_score": 3,
            "key_concerns": ["Analysis unavailable"],
            "personalized_notes": "Could not analyze ingredients. Please try again or check the ingredient list."
        },
        "ingredients": [
            {
                "name": "Unknown",
                "function": "N/A",
                "safety": "caution",
                "barrier_impact": "neutral",
                "allergy_potential": "medium",
                "special_concerns": ["Analysis failed"],
                "personalized_notes": "Analysis unavailable"
            }
        ]
    }

async def analyze_ingredients(
    ingredients_str: str,
    skin_type: str = "normal",
    concerns: list = None
) -> dict:
    """Analyze ingredients with user's skin profile"""
    concerns = concerns or []
    concerns_str = ", ".join(concerns) if concerns else "none"
    
    # Split ingredients into a list
    ingredients_list = [ing.strip() for ing in ingredients_str.split(",") if ing.strip()]
    
    prompt = f"""
    ### USER'S SKIN PROFILE ###
    Skin Type: {skin_type}
    Concerns: {concerns_str}
    
    ### ANALYSIS REQUEST ###
    As a cosmetic chemist, analyze ALL {len(ingredients_list)} skincare ingredients below for THIS specific user.
    Analyze each ingredient COMPLETELY before moving to the next. DO NOT SKIP ANY INGREDIENT.
    
    Ingredients to analyze:
    {", ".join(ingredients_list)}
    
    For EACH ingredient, provide:
    1. Function in skincare
    2. Safety: safe/caution/unsafe
    3. Barrier Impact: positive/neutral/negative
    4. Allergy Potential: low/medium/high
    5. Special Concerns (if any)
    6. Personalized notes for {skin_type} skin and {concerns_str} concerns and tell what other ingredients would work better for this user.
    7. Check if the prodcut is a suncreen and if so, analyze its SPF and PA rating
    
    Then provide overall product assessment:
    - Safety rating
    - Barrier impact
    - Allergy risk
    - Personalized suitability score (1-5)
    - Key concerns specifically for this user's skin profile
    - Recommendations for alternative ingredients that would work better

    IMPORTANT RULES:
    1. Analyze ALL ingredients - DO NOT SKIP ANY
    2. Output ONLY valid JSON
    3. Use double quotes for all keys and string values
    4. Do NOT add commas after the last element in arrays/objects
    5. Keep ingredient analysis concise but complete

    Format response as JSON:
    {{
        "overall_assessment": {{
            "safety_rating": "safe/caution/unsafe",
            "barrier_impact": "positive/neutral/negative",
            "allergy_risk": "low/medium/high",
            "suitability_score": 1-5,
            "key_concerns": ["list", "of", "concerns"],
            "personalized_notes": "Detailed notes for user's skin type",
            "recommended_alternatives": ["alternative1", "alternative2"]
        }},
        "ingredients": [
            {{
                "name": "ingredient_name",
                "function": "string",
                "safety": "safe/caution/unsafe",
                "barrier_impact": "positive/neutral/negative",
                "allergy_potential": "low/medium/high",
                "special_concerns": ["concern1", "concern2"],
                "personalized_notes": "Notes for user's skin type"
            }}
        ]
    }}
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gemma2-9b-it",
        "messages": [
            {
                "role": "system",
                "content": "You are a cosmetic chemist. Analyze ALL ingredients. Output ONLY valid JSON without any additional text."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,  # Lower temperature for more consistent results
        "max_tokens": 4000,   # Increased token limit
        "response_format": {"type": "json_object"}
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROQ_API_URL, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Groq API error: {error_text}")
                    return fallback_analysis(ingredients_str)

                data = await response.json()
                response_content = data["choices"][0]["message"]["content"]
                logger.info("Raw model output:\n%s", response_content)

                # Handle JSON parsing
                try:
                    analysis = extract_and_fix_json(response_content)
                    
                    # Verify all ingredients were analyzed
                    analyzed_ingredients = [ing['name'] for ing in analysis.get('ingredients', [])]
                    missing = [ing for ing in ingredients_list if ing not in analyzed_ingredients]
                    
                    if missing:
                        logger.warning(f"Missing analysis for {len(missing)} ingredients")
                        # Add placeholder for missing ingredients
                        for ing in missing:
                            analysis['ingredients'].append({
                                "name": ing,
                                "function": "Unknown",
                                "safety": "caution",
                                "barrier_impact": "neutral",
                                "allergy_potential": "medium",
                                "special_concerns": ["Analysis incomplete"],
                                "personalized_notes": "Could not analyze this ingredient"
                            })
                    
                    return analysis
                except Exception as e:
                    logger.error(f"JSON parsing failed: {str(e)}")
                    return fallback_analysis(ingredients_str)

    except Exception as e:
        logger.exception("Groq analysis failed")
        return fallback_analysis(ingredients_str)