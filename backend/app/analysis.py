import os
import json
import logging
import aiohttp
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def extract_json_from_text(text: str) -> str:
    """
    Extract the first JSON object from model output text.
    """
    json_pattern = re.compile(r"\{.*\}", re.DOTALL)
    match = json_pattern.search(text)
    if match:
        return match.group(0)
    raise ValueError("No JSON found in response.")

async def analyze_ingredients(
    ingredients_str: str,
    skin_type: str = "normal",
    concerns: list = None
) -> dict:
    """Analyze ingredients with user's skin profile"""
    
    concerns = concerns or []
    concerns_str = ", ".join(concerns) if concerns else "none"
    
    prompt = f"""
    ### USER'S SKIN PROFILE ###
    Skin Type: {skin_type}
    Concerns: {concerns_str}
    
    ### ANALYSIS REQUEST ###
    As a cosmetic chemist, analyze these skincare ingredients for THIS specific user, if its not an ingredient skip it:
    {ingredients_str}
    
    For each ingredient, provide:
    1. Function in skincare
    2. Safety: safe/caution/unsafe
    3. Barrier Impact: positive/neutral/negative
    4. Allergy Potential: low/medium/high
    5. Special Concerns (e.g., pregnancy, photosensitivity)
    6. Personalized notes for {skin_type} skin and {concerns_str} concerns

    Provide overall product assessment:
    - Safety rating
    - Barrier impact
    - Allergy risk
    - Personalized suitability score (1-5)
    - Key concerns specifically for this user's skin profile

    Format response as JSON:
    {{
        "overall_assessment": {{
            "safety_rating": "safe/caution/unsafe",
            "barrier_impact": "positive/neutral/negative",
            "allergy_risk": "low/medium/high",
            "suitability_score": 1-5,
            "key_concerns": ["list", "of", "concerns"],
            "personalized_notes": "Detailed notes for user's skin type"
        }},
        "ingredients": [
            {{
                "name": "ingredient_name",
                "function": "string",
                "safety": "safe/caution/unsafe",
                "barrier_impact": "positive/neutral/negative",
                "allergy_potential": "low/medium/high",
                "natural_alternatives": ["alt1", "alt2"],
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
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are a cosmetic chemist with 20 years of experience."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROQ_API_URL, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Groq API error: {error_text}")
                    raise RuntimeError(f"API request failed with status {response.status}")

                data = await response.json()
                response_content = data["choices"][0]["message"]["content"]
                logger.info("Raw model output:\n%s", response_content)

                json_text = extract_json_from_text(response_content)
                return json.loads(json_text)

    except Exception as e:
        logger.exception("Groq analysis failed.")
        return {"error": "Analysis failed"}