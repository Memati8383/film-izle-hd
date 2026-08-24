import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from extractor import get_all_movies

print("Tum filmler taraniyor (sinirsiz)...")
movies = get_all_movies(max_pages=0)
print(f"\nToplam film sayisi: {len(movies)}")
print("\nOrnek filmler:")
for i, m in enumerate(movies[:20], 1):
    yil = m.get('year', '')
    puan = m.get('rating', '')
    print(f"  {i}. {m['title']} ({yil}) [{puan}]")
