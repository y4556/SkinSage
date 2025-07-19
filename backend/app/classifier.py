

def classify_ocr_text(text):
    """Classify OCR text as product name or ingredients"""
    # Heuristic 1: Check for ingredient list keywords
    ingredient_keywords = ["ingredients", "ingrédients", "composition", "contains", "ing:"]
    has_ingredients = any(keyword in text.lower() for keyword in ingredient_keywords)
    
    # Heuristic 2: Check for common ingredient patterns
    common_ingredients = ["aqua", "water", "glycerin", "alcohol", "parfum"]
    has_common_ingredients = sum(ing in text.lower() for ing in common_ingredients) > 3
    
    # Heuristic 3: Check for product name patterns
    brand_keywords = ["by", "for", "collection", "serum", "cream", "lotion"]
    has_brand_terms = sum(term in text.lower() for term in brand_keywords) > 2
    
    # Heuristic 4: Length-based detection
    is_long_text = len(text.split()) > 50
    
    if has_ingredients or has_common_ingredients or is_long_text:
        return "ingredients"
    elif has_brand_terms:
        return "product_name"
    else:
        return "ambiguous"