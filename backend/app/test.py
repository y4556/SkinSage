from backend.app.web_scraper import get_ingredients_by_product_name
if __name__ == "__main__":
    # Example product name
    product = "CeraVe Hydrating Facial Cleanser"

    # Call the function
    ingredients, url = get_ingredients_by_product_name(product)

    # Display results
    if url:
        print("\n✅ Product URL:")
        print(url)
    else:
        print("\n❌ No URL found.")

    if ingredients:
        print("\n✅ Extracted Ingredients:")
        print(ingredients)
    else:
        print("\n❌ No ingredients extracted.")
