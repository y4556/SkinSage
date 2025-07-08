import os
import logging
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

async def get_chat_response(
    question: str,
    context: dict,
    skin_type: str,
    concerns: list
) -> dict:
    """
    Get personalized AI response about product analysis
    """
    # Prepare context with user profile
    concerns_str = ", ".join(concerns) if concerns else "no specific concerns"
    
    context_str = (
        f"### USER'S SKIN PROFILE ###\n"
        f"Skin Type: {skin_type}\n"
        f"Concerns: {concerns_str}\n\n"
        "### PRODUCT ANALYSIS REPORT ###\n"
    )
    
    # Add overall assessment
    overall = context.get("overall_assessment", {})
    context_str += (
        f"Overall Assessment:\n"
        f"Safety Rating: {overall.get('safety_rating', 'unknown')}\n"
        f"Barrier Impact: {overall.get('barrier_impact', 'unknown')}\n"
        f"Allergy Risk: {overall.get('allergy_risk', 'unknown')}\n"
        f"Suitability Score: {overall.get('suitability_score', 'unknown')}\n"
        f"Key Concerns: {', '.join(overall.get('key_concerns', []))}\n"
        f"Personalized Notes: {overall.get('personalized_notes', '')}\n\n"
    )
    
    # Add ingredients analysis
    context_str += "Ingredients Analysis:\n"
    for ingredient in context.get("ingredients", []):
        context_str += (
            f"- {ingredient['name']}:\n"
            f"  Function: {ingredient.get('function', '')}\n"
            f"  Safety: {ingredient.get('safety', 'unknown')}\n"
            f"  Barrier Impact: {ingredient.get('barrier_impact', 'unknown')}\n"
            f"  Allergy Potential: {ingredient.get('allergy_potential', 'unknown')}\n"
            f"  Natural Alternatives: {', '.join(ingredient.get('natural_alternatives', []))}\n"
            f"  Special Concerns: {', '.join(ingredient.get('special_concerns', []))}\n"
            f"  Personalized Notes: {ingredient.get('personalized_notes', '')}\n\n"
        )
    
    # Prepare prompt with personalization guidelines
    prompt = f"""
    ### YOUR ROLE ###
    You are a cosmetic chemist assistant helping a user with:
    - Skin type: {skin_type}
    - Concerns: {concerns_str}
    
    ### CONTEXT ###
    {context_str}
    
    ### USER QUESTION ###
    {question}
    
    ### RESPONSE GUIDELINES ###
    1. Always consider the user's skin profile first
    2. Personalize recommendations for their skin type and concerns
    3. Be specific about ingredients and their effects
    4. Warn about potential allergens or barrier damage
    5. Recommend natural alternatives when relevant
    6. Explain why ingredients are good/bad for their specific skin
    7. If a question can't be answered with the report, say so
    8. Keep responses scientific but easy to understand
    9. Highlight any ingredients that address their concerns
    10. Note any ingredients that might worsen their concerns
    11. If the question is about the DIY product, provide steps 
    12. Always provide sources for your information
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
        "temperature": 0.5,
        "max_tokens": 1500
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROQ_API_URL, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Groq API error: Status {response.status}, Response: {error_text}")
                    return {
                        "response": "I'm having trouble answering that. Please try again later.",
                        "sources": []
                    }

                data = await response.json()
                response_content = data["choices"][0]["message"]["content"]
                
                return {
                    "response": response_content,
                    "sources": ["Cosmetic Ingredient Review", "PubMed research"]
                }

    except Exception as e:
        logger.exception("Chat failed")
        return {
            "response": "I'm experiencing technical difficulties. Please try again later.",
            "sources": []
        }