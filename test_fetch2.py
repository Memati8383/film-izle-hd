import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from extractor import get_all_movies, get_movies_from_page

# Test: 1 sayfa
print("=== 1 SAYFA TEST ===")
movies1, total = get_movies_from_page('https://hdfilmcehennemini.com/')
print(f"  Sayfa 1: {len(movies1)} film, Toplam sayfa: {total}")

# Test: 5 sayfa
print("\n=== 5 SAYFA TEST ===")
movies5 = get_all_movies(max_pages=5)
print(f"  5 sayfa toplam: {len(movies5)} film")
for i, m in enumerate(movies5[:5], 1):
    print(f"    {i}. {m['title']}")
