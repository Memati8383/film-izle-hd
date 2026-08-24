"""
Film İzle HD - Netflix Tarzi Web Sinema Platformu
- Netflix Intro Animasyonu (Ta-Dum)
- Dinamik & Kisisellestirilebilir "Kim Izliyor?" Profil Yoneticisi
- 1:1 Netflix Siyah/Kirmizi Temasi & Hero Billboard
- Akilli Arama (Spiderman, Batman, Hizli ve Ofkeli destegi)
- ThreadingTCPServer & Dahili HLS Segment Proxy (403/CORS ve Baglanti kopma korumasi)
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import mimetypes
import http.server
import socketserver
import urllib.parse
import json
import webbrowser
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from extractor import search_movies, get_movie_details
from common import (
    load_template, rewrite_m3u8, PROXY_HEADERS, sanitize_input, sanitize_url,
    RateLimiter, ThreadSafeCache, logger, get_cors_headers
)
from config import WEB_PORT as PORT, CACHE_TTL_SECONDS, RATE_LIMIT_PER_MINUTE, INITIAL_SEARCH_QUERIES, STATIC_DIR

movie_cache = ThreadSafeCache(ttl_seconds=CACHE_TTL_SECONDS)
rate_limiter = RateLimiter(max_per_minute=RATE_LIMIT_PER_MINUTE)
INDEX_HTML = load_template('index.html')


def _background_scrape():
    """Arka planda tum sayfalari tarar, bitince CACHE'e yazar."""
    movie_cache.scraping = True
    logger.info("Arka plan taramasi baslatildi")

    if not movie_cache.data:
        all_movies = []
        seen = set()
        for q in INITIAL_SEARCH_QUERIES:
            try:
                res = search_movies(q)
                for m in res:
                    if m['url'] not in seen:
                        seen.add(m['url'])
                        all_movies.append(m)
            except Exception as e:
                logger.warning("Arama hatasi '%s': %s", q, e)
        if all_movies:
            movie_cache.data = all_movies

    try:
        from extractor import get_movies_from_page, BASE_URL

        first_results, total_pages = get_movies_from_page(f"{BASE_URL}/")
        current = list(movie_cache.data) if movie_cache.data else []
        seen_urls = set(m['url'] for m in current)
        for m in first_results:
            if m['url'] not in seen_urls:
                seen_urls.add(m['url'])
                current.append(m)
        movie_cache.data = current

        def fetch_page(page_num):
            page_url = f"{BASE_URL}/page/{page_num}/"
            movies, _ = get_movies_from_page(page_url)
            return movies

        batch_size = 10
        for batch_start in range(2, total_pages + 1, batch_size):
            batch_end = min(batch_start + batch_size, total_pages + 1)
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(fetch_page, p): p for p in range(batch_start, batch_end)}
                for future in as_completed(futures):
                    try:
                        page_movies = future.result()
                        current = list(movie_cache.data)
                        seen_urls = set(m['url'] for m in current)
                        for m in page_movies:
                            if m['url'] not in seen_urls:
                                seen_urls.add(m['url'])
                                current.append(m)
                        movie_cache.data = current
                    except Exception as e:
                        logger.warning("Sayfa tarama hatasi: %s", e)
    except Exception as e:
        logger.error("Tarama hatasi: %s", e)
    finally:
        movie_cache.scraping = False
        logger.info("Arka plan taramasi tamamlandi. Toplam film: %d", len(movie_cache.data))


def get_cached_home_movies():
    if movie_cache.is_valid:
        return movie_cache.get_shuffled()

    if movie_cache.scraping and movie_cache.data:
        return movie_cache.data

    if not movie_cache.scraping:
        threading.Thread(target=_background_scrape, daemon=True).start()

    if not movie_cache.data:
        all_movies = []
        seen = set()
        for q in INITIAL_SEARCH_QUERIES:
            try:
                res = search_movies(q)
                for m in res:
                    if m['url'] not in seen:
                        seen.add(m['url'])
                        all_movies.append(m)
            except Exception as e:
                logger.warning("Baslangic arama hatasi '%s': %s", q, e)
        if all_movies:
            movie_cache.data = all_movies
            return all_movies

    return movie_cache.data or []


class WebAppHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.debug(format, *args)

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        origin = self.headers.get('Origin')
        cors = get_cors_headers(origin)
        for k, v in cors.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html_content, status=200):
        body = html_content.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(body)

    def _proxy_request(self, target_url, content_type, timeout=12):
        if not target_url:
            self.send_error(400, "Missing url")
            return
        if not sanitize_url(target_url):
            self.send_error(400, "Invalid URL scheme")
            return

        try:
            r = requests.get(target_url, headers=PROXY_HEADERS, timeout=timeout)
            self.send_response(r.status_code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(r.content)))
            origin = self.headers.get('Origin')
            cors = get_cors_headers(origin)
            for k, v in cors.items():
                self.send_header(k, v)
            if content_type == 'video/mp2t':
                self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
                self.send_header('Cache-Control', 'public, max-age=86400')
            self.end_headers()
            self.wfile.write(r.content)
        except requests.RequestException as e:
            logger.error("Proxy istek hatasi %s: %s", target_url[:80], e)
            self.send_error(502, "Bad Gateway")

    def _serve_static(self, path):
        """Statik dosyalari sunar (CSS, JS, vb.)."""
        file_path = os.path.join(STATIC_DIR, path[len('/static/'):])
        file_path = os.path.normpath(file_path)
        if not file_path.startswith(STATIC_DIR):
            self.send_error(403, "Forbidden")
            return
        if not os.path.isfile(file_path):
            self.send_error(404, "Not Found")
            return
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'public, max-age=3600')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            logger.error("Static dosya okuma hatasi %s: %s", file_path, e)
            self.send_error(500, "Internal Server Error")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        server_origin = f"http://localhost:{PORT}"

        try:
            if parsed.path == '/':
                if not rate_limiter.allow('html'):
                    self.send_error(429, "Too Many Requests")
                    return
                self._send_html(INDEX_HTML)

            elif parsed.path.startswith('/static/'):
                self._serve_static(parsed.path)

            elif parsed.path == '/robots.txt':
                robots_path = os.path.join(STATIC_DIR, 'robots.txt')
                try:
                    with open(robots_path, 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                except FileNotFoundError:
                    self.send_error(404)

            elif parsed.path == '/sitemap.xml':
                sitemap_path = os.path.join(STATIC_DIR, 'sitemap.xml')
                try:
                    with open(sitemap_path, 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/xml; charset=utf-8')
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                except FileNotFoundError:
                    self.send_error(404)

            elif parsed.path == '/api/home':
                if not rate_limiter.allow('api'):
                    self.send_error(429, "Too Many Requests")
                    return
                movies = get_cached_home_movies()
                self._send_json({
                    'movies': movies,
                    'total': len(movies),
                    'scraping': movie_cache.scraping
                })

            elif parsed.path == '/api/scrape-status':
                self._send_json({
                    'scraping': movie_cache.scraping,
                    'total': len(movie_cache.data)
                })

            elif parsed.path == '/api/search':
                if not rate_limiter.allow('search'):
                    self.send_error(429, "Too Many Requests")
                    return
                params = urllib.parse.parse_qs(parsed.query)
                q = sanitize_input(params.get('q', [''])[0])
                if not q:
                    self._send_json([])
                    return
                results = search_movies(q)
                self._send_json(results)

            elif parsed.path == '/api/details':
                params = urllib.parse.parse_qs(parsed.query)
                movie_url = sanitize_url(params.get('url', [''])[0])
                if not movie_url:
                    self._send_json({})
                    return
                details = get_movie_details(movie_url)
                self._send_json(details or {})

            elif parsed.path == '/hls/playlist.m3u8':
                params = urllib.parse.parse_qs(parsed.query)
                target_url = sanitize_url(params.get('url', [None])[0])
                if not target_url:
                    self.send_error(400, "Missing or invalid url")
                    return
                try:
                    r = requests.get(target_url, headers=PROXY_HEADERS, timeout=12)
                    if r.status_code == 200:
                        modified = rewrite_m3u8(r.text, target_url, server_origin)
                        data = modified.encode('utf-8')
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/vnd.apple.mpegurl; charset=utf-8')
                        self.send_header('Content-Length', str(len(data)))
                        origin = self.headers.get('Origin')
                        cors = get_cors_headers(origin)
                        for k, v in cors.items():
                            self.send_header(k, v)
                        self.end_headers()
                        self.wfile.write(data)
                    else:
                        self.send_error(r.status_code)
                except requests.RequestException as e:
                    logger.error("HLS playlist proxy hatasi: %s", e)
                    self.send_error(502, "Bad Gateway")

            elif parsed.path == '/hls/segment':
                params = urllib.parse.parse_qs(parsed.query)
                target_url = sanitize_url(params.get('url', [None])[0])
                self._proxy_request(target_url, 'video/mp2t', timeout=15)

            elif parsed.path == '/hls/subtitle.vtt':
                params = urllib.parse.parse_qs(parsed.query)
                target_url = sanitize_url(params.get('url', [None])[0])
                self._proxy_request(target_url, 'text/vtt; charset=utf-8', timeout=10)

            else:
                self.send_error(404)

        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, TimeoutError):
            pass
        except Exception as e:
            logger.error("Beklenmeyen hata %s: %s", parsed.path, e)
            try:
                self.send_error(500, "Internal Server Error")
            except Exception:
                pass


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def run_web_app():
    print("\n" + "=" * 65)
    print(" FILM IZLE HD - NETFLIX EDITION BASLATILDI")
    print(f" Tarayici Adresi: http://localhost:{PORT}")
    print("=" * 65 + "\n")

    # Render.com gibi production ortamlarinda tarayici acma
    is_production = os.environ.get('RENDER') or os.environ.get('PORT')
    if not is_production:
        webbrowser.open(f"http://localhost:{PORT}")
    
    with ThreadedHTTPServer(("", PORT), WebAppHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Sunucu kapatildi.")
            print("\nSunucu kapatildi.")


if __name__ == '__main__':
    run_web_app()
