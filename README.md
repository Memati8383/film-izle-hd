# Film İzle HD v2.2

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Deploy](https://img.shields.io/badge/Deploy-Render.com-purple?logo=render&logoColor=white)](https://film-izle-hd.onrender.com)

> **Full HD 1080p film izleme platformu.** Türkçe dublaj ve altyazılı binlerce filmi reklamsız, donmadan izle.

🔗 **Canlı Demo:** [https://film-izle-hd.onrender.com](https://film-izle-hd.onrender.com)

---

## Yenilikler ve Ozellikler

- **Netflix-kalitesinde UI/UX:** Intro animasyonu, "Kim Izliyor?" profil sistemi, hero billboard, Netflix satir sliderlari.
- **Dahili HLS & Segment Proxy:** 403 Forbidden ve CORS engellerini tamamen asan guclu arka plan proxy motoru.
- **Akilli Arama:** Query expansion, Turkce karakter donusumu, takma ad sozlugu (spiderman -> orumcek adam).
- **Sifir Reklam:** Pop-up reklamlar, yonlendirmeler ve video ici reklamlar tamamen temizlendi.
- **Turkce Dublaj & Orijinal Dil:** Tek tikla ses kanalini degistirme.
- **Turkce & Ingilizce Altyazi:** WebVTT altyazilari otomatik yuklenir.
- **Adaptive Bitrate Kalite:** 1080p Full HD, 720p veya Otomatik kalite.
- **Erisilebilirlik (a11y):** ARIA nitelikleri, keyboard navigasyonu, reduced-motion destegi.
- **Mobil Uyumluluk:** Responsive tasarim, mobil ve tablet cihazlarda calisir.
- **Guvenlik:** XSS korumasi, rate limiting, URL dogrulama, input sanitization.
- **Thread Guvenligi:** Thread-safe cache, locking mekanizmasi.
- **Logging:** Merkezi loglama sistemi, hata takibi.
- **Moduler Mimari:** CSS/JS harici dosyalara ayrildi, kod tekrari kaldirildi.
- **Toast Notification:** alert() yerine modern toast bildirim sistemi.
- **CORS Guvenligi:** Yalnizca izinli origin'ler icin Access-Control-Allow-Origin header'i.

---

## Proje Yapisi

```
film-izle-hd/
├── config.py          # Merkezi yapilandirma (tek kaynak)
├── common.py          # Ortak modul (proxy, guvenlik, cache, logging)
├── extractor.py       # Film arama ve stream extractor
├── web_app.py         # Netflix tarzi web arayuzu
├── player_server.py   # Bagimsiz oynatici sunucusu
├── main.py            # CLI arayuzu
├── start.py           # Baslatma scripti
├── render.yaml        # Render.com deploy ayarlari
├── requirements.txt   # Bagimliliklar
├── templates/
│   ├── index.html     # Ana sayfa template'i
│   └── player.html    # Oynatici template'i
└── static/
    ├── style.css      # Ana sayfa stilleri
    ├── app.js         # Ana sayfa JavaScript
    ├── common.js      # Ortak JS fonksiyonlari
    ├── player.css     # Oynatici stilleri
    └── player.js      # Oynatici JavaScript
```

---

## Canlı Demo

🔗 **https://film-izle-hd.onrender.com**

> ⚠️ Ücretsiz Render planında servis 15 dakika inaktiflik sonrası "sleep" moduna girer. İlk açılışta 30-60 saniye gecikme olabilir.

---

## Teknik Detaylar

- **Backend:** Python http.server + ThreadingTCPServer
- **Frontend:** Vanilla JS, CSS3 (harici dosyalar)
- **Video Oynatici:** Artplayer 5.1.1 + HLS.js 1.5.8
- **Proxy:** Dahili HLS Segment Proxy (403/CORS atlama)
- **Cache:** Thread-safe TTL cache (1 saat)
- **Rate Limiting:** Token bucket (60 istek/dakika)
- **Guvenlik:** XSS input sanitization, URL scheme dogrulama, CORS kontrolu
