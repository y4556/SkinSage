INGREDIENT_ANALYSIS_PROMPT = """
### USER'S SKIN PROFILE ###
Skin Type: {skin_type}
Concerns: {concerns_str}

### ANALYSIS REQUEST ###
As a cosmetic chemist, analyze ALL {num_ingredients} skincare ingredients below for THIS specific user.
Analyze each ingredient COMPLETELY before moving to the next. DO NOT SKIP ANY INGREDIENT.

Ingredients to analyze:
{ingredients_list}

For EACH ingredient, provide:
1. Function in skincare
2. Safety: safe/caution/unsafe
3. Barrier Impact: positive/neutral/negative
4. Allergy Potential: low/medium/high
5. Special Concerns (if any)
6. Personalized notes for {skin_type} skin which skin concerns does it target {concerns_str} concerns and write 2-3 lines about it. When to use it and what to avoid using it with. Provide SOURCES from where you got the information.
7. Check if the product is a sunscreen and if so, analyze its SPF and PA rating

Then provide overall product assessment:
- Safety rating
- Barrier impact
- Allergy risk
- Personalized suitability score (1-5) using this rubric:
    5 = Excellent match (all ingredients beneficial for {skin_type} skin and addresses {concerns_str})
    4 = Good match (most ingredients beneficial, minor concerns)
    3 = Neutral (some beneficial ingredients, some concerns)
    2 = Poor match (mostly problematic ingredients)
    1 = Very poor match (multiple ingredients harmful for {skin_type} skin)
- Key concerns specifically for this user's skin profile

RECOMMEND 2-3 ALTERNATIVE PRODUCTS:
- Recommend specific brand+product alternatives that would be better for this user
- Include both commercial and natural options
- For each alternative, provide:
* Brand and product name
* Brief reason why it's better for this user's skin profile and which skin concerns does it target {concerns_str} concerns
* Key beneficial ingredients

IMPORTANT RULES:
1. Analyze ALL ingredients - DO NOT SKIP ANY
2. Output ONLY valid JSON
3. Use double quotes for all keys and string values
4. Do NOT add commas after the last element in arrays/objects
5. Keep ingredient analysis concise but complete
6. If any ingredient is not recognized, skip it.
7. Give source URL of the sources if available

Format response as JSON:
{{
    "overall_assessment": {{
        "safety_rating": "safe/caution/unsafe",
        "barrier_impact": "positive/neutral/negative",
        "allergy_risk": "low/medium/high",
        "suitability_score": 1-5,
        "key_concerns": ["list", "of", "concerns"],
        "personalized_notes": "Detailed notes for user's skin type with sources URL"
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
    ],
    "alternative_products": [
        {{
            "brand": "Brand Name",
            "product": "Product Name",
            "type": "commercial/natural",
            "reason": "Why it's better",
            "key_ingredients": ["ingredient1", "ingredient2"]
        }}
    ]
}}
"""

# Chat system role
CHAT_SYSTEM_ROLE = "You are a cosmetic chemist with 20 years of experience."

# Chat guidelines
CHAT_GUIDELINES = """
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
    13. Provide URL links to sources when possible and if of the article from where you get the information

"""


# Agent classification prompt
AGENT_CLASSIFICATION_PROMPT = """
You are a skincare product analyzer. Strictly follow these rules:
1. Analyze if text contains product name, ingredients, or both
2. If text contains BOTH product name and ingredients:
   - Return ONLY the product name (type=product)
   - Ignore all ingredients
3. If text contains ONLY ingredients:
   - Return the cleaned ingredients list (type=ingredients)
4. If text contains ONLY product name:
   - Return the product name (type=product)
5. Response MUST be JSON with EXACTLY these fields:
   {{
     "type": "product" OR "ingredients" (NO other values),
     "product_name": "..." (ONLY if type=product),
     "ingredients": "..." (ONLY if type=ingredients)
   }}
6. For product names, extract ONLY the brand+product name (no sizes, descriptions, etc.)
7. For ingredients, return ONLY comma-separated ingredients (no percentages, numbers, etc.)
"""
