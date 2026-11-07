from src.extraction.mainfold_api import fetch_markets
from src.storage.local_storage import save_markets


# 1. API'dan marketlarni olish
markets = fetch_markets(
    limit=100,
    max_pages=3,
    retries=3
)

# 2. Ma'lumotlarni JSON faylga saqlash
file_path = save_markets(markets)

# 3. Natijani chiqarish
print("\n========== PIPELINE RESULTS ==========")
print("Total markets:", len(markets))
print("Saved file:", file_path)