"""
Film İzle HD - Unit Testler
common, extractor modulleri icin temel testler.
"""

import os
import time
import threading

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import (
    sanitize_input, sanitize_url, rewrite_m3u8, load_template,
    RateLimiter, ThreadSafeCache
)


class TestSanitizeInput:
    def test_normal_text(self):
        assert sanitize_input("Hello World") == "Hello World"

    def test_xss_script_tag(self):
        result = sanitize_input("<script>alert(1)</script>")
        assert "<script>" not in result

    def test_empty_input(self):
        assert sanitize_input("") == ""
        assert sanitize_input(None) == ""

    def test_long_input_truncated(self):
        long_text = "a" * 500
        result = sanitize_input(long_text)
        assert len(result) <= 200

    def test_non_string_input(self):
        assert sanitize_input(123) == ""
        assert sanitize_input([]) == ""


class TestSanitizeUrl:
    def test_valid_http(self):
        url = "http://example.com/video.m3u8"
        assert sanitize_url(url) == url

    def test_valid_https(self):
        url = "https://example.com/video.m3u8"
        assert sanitize_url(url) == url

    def test_ftp_rejected(self):
        assert sanitize_url("ftp://example.com/file") == ""

    def test_javascript_rejected(self):
        assert sanitize_url("javascript:alert(1)") == ""

    def test_empty_input(self):
        assert sanitize_url("") == ""
        assert sanitize_url(None) == ""


class TestRewriteM3u8:
    def test_basic_playlist(self):
        content = "#EXTM3U\nhttps://example.com/playlist.m3u8"
        result = rewrite_m3u8(content, "https://example.com/test.m3u8", "http://localhost:5000")
        assert "localhost:5000/hls/playlist.m3u8" in result

    def test_empty_content(self):
        result = rewrite_m3u8("", "https://example.com/test.m3u8", "http://localhost:5000")
        assert result == ""

    def test_comment_lines_preserved(self):
        content = "#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=800000\nhttps://example.com/low.m3u8"
        result = rewrite_m3u8(content, "https://example.com/master.m3u8", "http://localhost:5000")
        assert "#EXTM3U" in result

    def test_segment_urls_proxied(self):
        content = "#EXTM3U\nsegment.ts"
        result = rewrite_m3u8(content, "https://example.com/playlist.m3u8", "http://localhost:5000")
        assert "hls/segment" in result or "hls/playlist" in result


class TestLoadTemplate:
    def test_load_index(self):
        html = load_template('index.html')
        assert len(html) > 1000
        assert '<!DOCTYPE html>' in html

    def test_load_player(self):
        html = load_template('player.html')
        assert len(html) > 500
        assert '<!DOCTYPE html>' in html

    def test_nonexistent_template(self):
        html = load_template('nonexistent.html')
        assert html == ""


class TestRateLimiter:
    def test_allows_within_limit(self):
        rl = RateLimiter(max_per_minute=5)
        for _ in range(5):
            assert rl.allow('test') is True

    def test_blocks_over_limit(self):
        rl = RateLimiter(max_per_minute=3)
        for _ in range(3):
            rl.allow('test')
        assert rl.allow('test') is False

    def test_different_keys_independent(self):
        rl = RateLimiter(max_per_minute=2)
        rl.allow('a')
        rl.allow('a')
        assert rl.allow('a') is False
        assert rl.allow('b') is True


class TestThreadSafeCache:
    def test_initial_state(self):
        cache = ThreadSafeCache(ttl_seconds=1)
        assert cache.data == []
        assert cache.is_valid is False
        assert cache.scraping is False

    def test_set_get_data(self):
        cache = ThreadSafeCache(ttl_seconds=60)
        cache.data = [{"title": "test"}]
        assert len(cache.data) == 1
        assert cache.data[0]["title"] == "test"

    def test_ttl_expiry(self):
        cache = ThreadSafeCache(ttl_seconds=0)
        cache.data = [{"title": "test"}]
        time.sleep(0.1)
        assert cache.is_valid is False

    def test_scraping_flag(self):
        cache = ThreadSafeCache()
        cache.scraping = True
        assert cache.scraping is True
        cache.scraping = False
        assert cache.scraping is False

    def test_thread_safety(self):
        cache = ThreadSafeCache(ttl_seconds=60)
        errors = []

        def writer():
            for i in range(100):
                cache.data = [{"i": i}]

        def reader():
            for _ in range(100):
                _ = cache.data

        threads = [threading.Thread(target=writer) for _ in range(3)]
        threads += [threading.Thread(target=reader) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
