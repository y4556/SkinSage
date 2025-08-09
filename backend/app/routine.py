import os
import json
import logging
import aiohttp
import re
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

async def generate_routine_with_groq(time_of_day: str, skin_type: str, concerns: List[str]) -> Optional[Dict]:
    """Generate skincare routine using Groq API"""
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY is not set")
        return None
    
    # Define routine steps based on time of day
    steps = {
        "AM": ["cleanser", "toner", "serum", "moisturizer", "sunscreen"],
        "PM": ["oil cleanser", "toner", "treatment", "eye cream", "moisturizer"]
    }
    
    # Prepare the prompt
    concerns_str = ", ".join(concerns) if concerns else "no specific concerns"
    prompt = f"""
You are an expert skincare formulator creating a personalized skincare routine.
Create a {time_of_day} routine for someone with {skin_type} skin and these concerns: {concerns_str}.

For each step, recommend specific products.
Include the direct link to the OFFICIAL BRAND WEBSITE for each product (not third-party retailers).
Provide a short, 1-sentence description of how this product helps with {skin_type} skin and {concerns_str} concerns.

Return ONLY valid JSON in this format:
{{
    "routine": [
        {{
            "step": "step name",
            "product": "Brand Product Name",
            "link": "https://brand.com",
            "description": "Brief description of how this product helps with {skin_type} skin and {concerns_str} concerns."
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
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 1500,
        "response_format": {"type": "json_object"}
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    logger.error(f"Groq API error: {response.status} - {error}")
                    return None
                
                data = await response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Clean and parse JSON
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    return json.loads(json_match.group(0))
                
                logger.error("Failed to extract JSON from response")
                return None
    except Exception as e:
        logger.error(f"Groq API request failed: {str(e)}")
        return None