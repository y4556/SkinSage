import os
from groq import Groq
import  json

def compare_products(analysis1, analysis2, skin_type, concerns):
    """Compare two product analyses using Groq"""
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    response = groq_client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {
                "role": "system",
                "content": "You are a skincare expert comparing two products"
            },
            {
                "role": "user",
                "content": (
                    f"Compare these products for {skin_type} skin with concerns: {', '.join(concerns)}\n\n"
                    "PRODUCT 1 ANALYSIS:\n" + json.dumps(analysis1) + "\n\n"
                    "PRODUCT 2 ANALYSIS:\n" + json.dumps(analysis2) + "\n\n"
                    "Output comparison in JSON format with these keys: "
                    "better_product (1 or 2), comparison_summary, key_differences"
                )
            }
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)