import asyncio
from ocr import extract_ingredients

IMAGE_PATH = r"D:\red_buffer\VS Code\Project\backend\data\Equalberry.jpg"

async def main():
    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()

    try:
        ingredients = await extract_ingredients(image_bytes)
        print("\nExtracted Ingredients:\n")
        print(ingredients)
    except Exception as e:
        print(f"Error during OCR: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        pending = asyncio.all_tasks(loop=loop)
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()
