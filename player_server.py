"""
Film İzle HD - Yerel Web Oynatici Sunucusu
Artplayer ve HLS.js ile reklamsiz, hizli, dublaj/altyazi/kalite secimli modern video oynatici.
Dahili HLS Akis ve Segment Proxy motoru ile 403/CORS engellerini tamamen asar.
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

from common import (
    load_template, rewrite_m3u8, PROXY_HEADERS, sanitize_url, logger, get_cors_headers
)
from config import PLAYER_PORT, REQUEST_TIMEOUT, SEGMENT_TIMEOUT, SUBTITLE_TIMEOUT, STATIC_DIR

_lock = threading.Lock()
CURRENT_MOVIE = None
HTTPD = None

HTML_PAGE_TEMPLATE = load_template('player.html')


class MoviePlayerHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.debug(format, *args)

    def _serve_static(self, path):
        """Statik dosyalari sunar."""
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
        server_origin = f"http://localhost:{PLAYER_PORT}"

        try:
            if parsed.path.startswith('/static/'):
                self._serve_static(parsed.path)

            elif parsed.path in ('/', '/watch'):
                with _lock:
                    movie = CURRENT_MOVIE

                if not movie or not movie.get('streams'):
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write("<h2>Henuz bir film secilmedi. Lutfen terminalden film secin.</h2>".encode('utf-8'))
                    return

                hls_stream = None
                for s in movie['streams']:
                    if s.get('type') == 'hls':
                        hls_stream = s
                        break

                if not hls_stream:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write("<h2>Bu film icin dogrudan HLS akisi bulunamadi.</h2>".encode('utf-8'))
                    return

                proxied_m3u8 = f"/hls/playlist.m3u8?url={urllib.parse.quote(hls_stream.get('m3u8_url', ''))}"

                content = HTML_PAGE_TEMPLATE
                content = content.replace('{{TITLE}}', movie.get('title', 'Film'))
                content = content.replace('{{ORIG_TITLE}}', movie.get('orig_title', ''))
                content = content.replace('{{STREAM_URL}}', json.dumps(proxied_m3u8))
                content = content.replace('{{TRACKS}}', json.dumps(hls_stream.get('tracks', [])))

                body = content.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            elif parsed.path == '/hls/playlist.m3u8':
                params = urllib.parse.parse_qs(parsed.query)
                target_url = sanitize_url(params.get('url', [None])[0])
                if not target_url:
                    self.send_error(400, "Missing or invalid url")
                    return

                try:
                    r = requests.get(target_url, headers=PROXY_HEADERS, timeout=REQUEST_TIMEOUT)
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
                if not target_url:
                    self.send_error(400, "Missing or invalid url")
                    return

                try:
                    r = requests.get(target_url, headers=PROXY_HEADERS, timeout=SEGMENT_TIMEOUT)
                    self.send_response(r.status_code)
                    self.send_header('Content-Type', 'video/mp2t')
                    self.send_header('Content-Length', str(len(r.content)))
                    origin = self.headers.get('Origin')
                    cors = get_cors_headers(origin)
                    for k, v in cors.items():
                        self.send_header(k, v)
                    self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
                    self.send_header('Cache-Control', 'public, max-age=86400')
                    self.end_headers()
                    self.wfile.write(r.content)
                except requests.RequestException as e:
                    logger.error("HLS segment proxy hatasi: %s", e)
                    self.send_error(502, "Bad Gateway")

            elif parsed.path == '/hls/subtitle.vtt':
                params = urllib.parse.parse_qs(parsed.query)
                target_url = sanitize_url(params.get('url', [None])[0])
                if not target_url:
                    self.send_error(400, "Missing or invalid url")
                    return

                try:
                    r = requests.get(target_url, headers=PROXY_HEADERS, timeout=SUBTITLE_TIMEOUT)
                    self.send_response(r.status_code)
                    self.send_header('Content-Type', 'text/vtt; charset=utf-8')
                    origin = self.headers.get('Origin')
                    cors = get_cors_headers(origin)
                    for k, v in cors.items():
                        self.send_header(k, v)
                    self.end_headers()
                    self.wfile.write(r.content)
                except requests.RequestException as e:
                    logger.error("Subtitle proxy hatasi: %s", e)
                    self.send_error(502, "Bad Gateway")
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


def start_server_thread():
    global HTTPD

    with _lock:
        if HTTPD is not None:
            return

        class ReusableTCPServer(socketserver.TCPServer):
            allow_reuse_address = True

        try:
            HTTPD = ReusableTCPServer(("", PLAYER_PORT), MoviePlayerHandler)
            threading.Thread(target=HTTPD.serve_forever, daemon=True).start()
            logger.info("Oynatici sunucusu baslatildi: port %d", PLAYER_PORT)
        except Exception as e:
            logger.error("Sunucu baslatilamadi (port %d): %s", PLAYER_PORT, e)
            HTTPD = None


def play_movie(movie_details, open_browser=True):
    global CURRENT_MOVIE
    with _lock:
        CURRENT_MOVIE = movie_details
    start_server_thread()

    url = f"http://localhost:{PLAYER_PORT}/watch"
    if open_browser:
        webbrowser.open(url)
    return url
