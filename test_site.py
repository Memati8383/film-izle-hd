import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://hdfilmcehennemini.com/'
}

url = 'https://hdfilmcehennemini.com/'
res = requests.get(url, headers=HEADERS, timeout=12)
soup = BeautifulSoup(res.text, 'html.parser')

# Sayfalama linklerini bul
print("=== PAGINATION LINKS ===")
for a in soup.select('a'):
    href = a.get('href', '')
    if '/page/' in href or 'pagination' in str(a.get('class', '')).lower() or 'next' in str(a.get('class', '')).lower():
        print(f"  {href} (class={a.get('class')})")

# Tum linkleri kontrol et
print("\n=== ALL LINKS WITH /page/ ===")
for a in soup.select('a[href*="/page/"]'):
    print(f"  {a.get('href')}")

# Kategori linklerini bul
print("\n=== CATEGORY LINKS ===")
for a in soup.select('a'):
    href = a.get('href', '')
    if '/kategori/' in href or '/film-izle/' in href or '/dizi-izle/' in href:
        print(f"  {href}")

# Tum movie-box sayisini kontrol et
movie_boxes = soup.select('.listmovie, .movie-box, .poster, .movie-card')
print(f"\n=== ANA SAYFA FILM KUTUSU SAYISI: {len(movie_boxes)} ===")

# movie-box parsersini kontrol et
print("\n=== PARSER TEST ===")
boxes = soup.select('.movie-box')
print(f"  .movie-box: {len(boxes)}")
boxes2 = soup.select('.listmovie')
print(f"  .listmovie: {len(boxes2)}")
boxes3 = soup.select('.film-ismi')
print(f"  .film-ismi: {len(boxes3)}")
boxes4 = soup.select('.movie-card')
print(f"  .movie-card: {len(boxes4)}")

# hangisi calisiyor?
all_divs = soup.find_all('div')
movie_divs = [d for d in all_divs if d.get('class') and any('movie' in c.lower() or 'film' in c.lower() or 'poster' in c.lower() for c in d.get('class', []))]
print(f"  movie/film/poster classli div: {len(movie_divs)}")
for d in movie_divs[:5]:
    print(f"    class={d.get('class')}")
