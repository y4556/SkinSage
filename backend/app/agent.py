import logging
import os
import json
import aiohttp
from typing import Dict, Optional
from dotenv import load_dotenv
from backend.app.ocr import extract_raw_text_from_image
from backend.app.web_scraper import get_ingredients_by_product_name
from backend.app.analysis import analyze_ingredients
from backend.prompts.prompts import AGENT_CLASSIFICATION_PROMPT

logger = logging.getLogger(__name__)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class SkincareAgent:
    def __init__(self, user_profile):
        self.user_profile = user_profile
        
    async def process_input(self, input_type, input_data):
        """Main agent entry point"""
        if input_type == "image":
            raw_text = await extract_raw_text_from_image(input_data)
            return await self._determine_and_process(raw_text)
        elif input_type == "text":
            return await self._determine_and_process(input_data)
        else:
            raise ValueError("Invalid input type")

    async def _determine_and_process(self, text):
        """Let the agent decide how to process the text with strict rules"""
        if not GROQ_API_KEY:
            logger.error("GROQ_API_KEY is not set")
            raise RuntimeError("Groq API key missing")

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": AGENT_CLASSIFICATION_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Analyze this text: '{text}'"
                }
            ],
            "temperature": 0.0,
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
                        raise RuntimeError("Groq API request failed")

                    data = await response.json()
                    result = json.loads(data["choices"][0]["message"]["content"])
                    logger.info(f"Agent classification result: {result}")

                    # Validate the response format
                    if "type" not in result:
                        raise ValueError("Missing 'type' in response")
                        
                    if result["type"] not in ["product", "ingredients"]:
                        raise ValueError(f"Invalid type: {result['type']}")
                        
                    if result["type"] == "product" and "product_name" not in result:
                        raise ValueError("Product type missing product_name")
                        
                    if result["type"] == "ingredients" and "ingredients" not in result:
                        raise ValueError("Ingredients type missing ingredients")

        except (aiohttp.ClientError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error processing text: {str(e)}")
            # Fallback to treating as product name
            result = {"type": "product", "product_name": text}

        # Process based on the agent's determination
        if result["type"] == "ingredients":
            return await analyze_ingredients(
                result["ingredients"],
                self.user_profile["skin_type"],
                self.user_profile["concerns"]
            )
        else:  # product
            ingredients, url = get_ingredients_by_product_name(result["product_name"])
            return await analyze_ingredients(
                ingredients,
                self.user_profile["skin_type"],
                self.user_profile["concerns"],
                url 
            )