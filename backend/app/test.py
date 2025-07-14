# import asyncio
# from ocr import extract_ingredients

# IMAGE_PATH = r"D:\red_buffer\VS Code\Project\backend\data\Equalberry.jpg"

# async def main():
#     with open(IMAGE_PATH, "rb") as f:
#         image_bytes = f.read()

#     try:
#         ingredients = await extract_ingredients(image_bytes)
#         print("\nExtracted Ingredients:\n")
#         print(ingredients)
#     except Exception as e:
#         print(f"Error during OCR: {e}")

# if __name__ == "__main__":
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         loop.run_until_complete(main())
#     finally:
#         pending = asyncio.all_tasks(loop=loop)
#         for task in pending:
#             task.cancel()
#         loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
#         loop.close()
import os
import requests
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("GOOGLE_CX")

def google_search(query, num_results=5):
    """
    Performs a Google Custom Search.

    Args:
        query (str): The search query.
        num_results (int): How many results to fetch.

    Returns:
        List of search result dictionaries.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "num": num_results
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} {response.text}")

    data = response.json()
    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })

    return results

if __name__ == "__main__":
    # Example search
    query = "best skincare ingredients"
    search_results = google_search(query)

    for idx, res in enumerate(search_results, start=1):
        print(f"{idx}. {res['title']}")
        print(f"URL: {res['link']}")
        print(f"Snippet: {res['snippet']}")
        print("---")
