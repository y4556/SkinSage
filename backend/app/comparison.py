import os
from groq import Groq
import  json
import yaml
from pathlib import Path

config_path = Path(__file__).parent.parent / "config" / "config.yaml"
cfg = yaml.safe_load(config_path.read_text())

def compare_products(analysis1, analysis2, skin_type, concerns):
    """Compare two product analyses using Groq"""
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    response = groq_client.chat.completions.create(
        model=cfg["models"]["comparison"]["name"],
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