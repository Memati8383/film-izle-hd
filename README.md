# Film İzle HD v2.2

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Deploy](https://img.shields.io/badge/Deploy-Render.com-purple?logo=render&logoColor=white)](https://film-izle-hd.onrender.com)

> **Full HD 1080p film izleme platformu.** Türkçe dublaj ve altyazılı binlerce filmi reklamsız, donmadan izle.

🔗 **Canlı Demo:** [https://film-izle-hd.onrender.com](https://film-izle-hd.onrender.com)

---

## Hakkında

Film İzle HD, modern ve kullanıcı dostu bir film izleme platformudur. Netflix tarzı arayüzü ile binlerce filmi keşfetmenizi, aramanızı ve izlemenizi sağlar. Tamamen ücretsiz, reklamsız ve yüksek kaliteli (1080p Full HD) bir deneyim sunar.

### Neden Film İzle HD?

- **Reklamsız Deneyim:** Pop-up, yönlendirme veya video içi reklam yok
- **Yüksek Kalite:** 1080p Full HD, 720p veya otomatik kalite seçimi
- **Türkçe Dublaj & Altyazı:** Türkçe dublaj, orijinal dil ve WebVTT altyazı desteği
- **Modern Arayüz:** Netflix benzeri hero billboard, profil sistemi ve sliderlar
- **Mobil Uyumluluk:** Telefon, tablet ve masaüstü cihazlarda sorunsuz çalışır

---

## Filmler Nereden Geliyor?

Film İzle HD, film verilerini **dijital film platformlarından** çekmektedir. Uygulama, filmlerin başlık, poster, year, IMDb puanı ve stream bağlantılarını harici kaynaklardan alarak kullanıcıya sunar.

### Nasıl Çalışır?

1. **Arama:** Kullanıcı film adını girer
2. **Veri Çekme:** Sistem, harici kaynaktan film bilgilerini ve HLS (HTTP Live Streaming) stream bağlantılarını çözer
3. **Proxy Motoru:** Video akışları dahili proxy üzerinden sunulur (CORS ve 403 engellerini aşar)
4. **Oynatıcı:** Artplayer + HLS.js ile tarayıcıda doğrudan oynatılır

### Kaynak Bilgileri

- Film listeleri ve detayları harici web sitelerinden scrape edilmektedir
- HLS (m3u8) video akışları proxy üzerinden sunulur
- Altyazılar WebVTT formatında otomatik yüklenir
- Tüm işlemler sunucu tarafında yapılır, istemci doğrudan kaynak siteye bağlanmaz

> **Not:** Bu uygulama film içeriklerini barındırmaz, yalnızca harici kaynaklardan gelen stream bağlantılarını proxy'ler.

---

## Özellikler

### 🎬 Arayüz
- Netflix tarzı hero billboard ve film sliderları
- "Kim İzliyor?" profil yöneticisi
- Netflixintro animasyonu (Ta-Dum)
- Modern toast bildirim sistemi
- Responsive tasarım (mobil + masaüstü)

### 🔍 Arama
- Akıllı arama (query expansion)
- Türkçe karakter dönüşümü (ç→c, ı→i, ş→s, etc.)
- Takma ad sözlüğü (spiderman → Örümcek Adam)
- Çoklu varyasyon araması

### 🎥 Oynatıcı
- Artplayer 5.1.1 + HLS.js 1.5.8
- 1080p Full HD, 720p veya Otomatik kalite
- Türkçe dublaj & Orijinal dil seçimi
- WebVTT altyazı desteği (Türkçe & İngilizce)
- Tam ekran ve Picture-in-Picture (PiP)

### 🔒 Güvenlik
- XSS koruması (input sanitization)
- Rate limiting (60 istek/dakika)
- URL scheme doğrulama
- CORS kontrolü (yalnızca izinli origin'ler)
- Thread-safe cache (locking mekanizması)

---

## Teknik Detaylar

| Bileşen | Teknoloji |
|---------|-----------|
| **Backend** | Python http.server + ThreadingTCPServer |
| **Frontend** | Vanilla JS, CSS3 |
| **Video Oynatıcı** | Artplayer 5.1.1 + HLS.js 1.5.8 |
| **Web Scraping** | BeautifulSoup4 |
| **HTTP İstekleri** | requests |
| **Deploy** | Render.com (Ücretsiz Tier) |
| **Cache** | Thread-safe TTL cache (1 saat) |
| **Rate Limiting** | Token bucket (60 istek/dk) |

### Mimari

```
Kullanıcı → Tarayıcı → web_app.py (Port 5000/10000)
                            │
                            ├── / → index.html (Ana Sayfa)
                            ├── /api/home → Film Listesi (Cache'li)
                            ├── /api/search?q= → Arama Sonuçları
                            ├── /api/details?url= → Film Detayları
                            ├── /hls/playlist.m3u8 → HLS Proxy
                            ├── /hls/segment → Segment Proxy
                            └── /hls/subtitle.vtt → Altyazı Proxy
```

---

## Proje Yapısı

```
film-izle-hd/
├── config.py          # Merkezi yapılandırma (tek kaynak)
├── common.py          # Ortak modül (proxy, güvenlik, cache, logging)
├── extractor.py       # Film arama ve stream extractor
├── web_app.py         # Netflix tarzı web arayüzü
├── player_server.py   # Bağımsız oynatıcı sunucusu
├── main.py            # CLI arayüzü
├── start.py           # Başlatma scripti
├── render.yaml        # Render.com deploy ayarları
├── requirements.txt   # Bağımlılıklar
├── templates/
│   ├── index.html     # Ana sayfa template'i
│   └── player.html    # Oynatıcı template'i
└── static/
    ├── style.css      # Ana sayfa stilleri
    ├── app.js         # Ana sayfa JavaScript
    ├── common.js      # Ortak JS fonksiyonları
    ├── player.css     # Oynatıcı stilleri
    └── player.js      # Oynatıcı JavaScript
```

---

## Kurulum

### Yerelde (Local)

```bash
# 1. Repoyu klonlayın
git clone https://github.com/Memati8383/film-izle-hd.git
cd film-izle-hd

# 2. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 3. Uygulamayı başlatın
python web_app.py

# 4. Tarayıcıda açın
# Otomatik olarak http://localhost:5000 açılır
```

### Render.com'a Deploy

1. GitHub repo'yu fork/clone edin
2. [render.com](https://render.com) hesabınıza giriş yapın
3. **New + → Web Service** seçin
4. `Memati8383/film-izle-hd` repo'sunu seçin
5. Ayarlar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python web_app.py`
   - **Plan:** Free
6. **Deploy** butonuna basın

> `render.yaml` dosyası otomatik olarak ayarları yükler.

---

## Ekran Görüntüleri

| Ana Sayfa | Oynatıcı |
|-----------|----------|
| Netflix tarzı hero billboard + film sliderları | 1080p Full HD oynatıcı |
| Akıllı arama sistemi | Dublaj/Altyazı seçimi |
| Film kartları (IMDb puanı, yıl) | Tam ekran & PiP desteği |

---

## Sıkça Sorulan Sorular

### Film izlemek ücretsiz mi?
Evet! Film İzle HD tamamen ücretsizdir. Hiçbir abonelik veya kayıt gerektirmez.

### Reklam var mı?
Hayır! Pop-up, yönlendirme veya video içi reklam bulunmamaktadır.

### Mobilde çalışıyor mu?
Evet! Responsive tasarım ile telefon, tablet ve masaüstü cihazlarda sorunsuz çalışır.

### Türkçe dublaj destekleniyor mu?
Evet! Filmlerin çoğunda Türkçe dublaj ve altyazı seçenekleri mevcuttur.

### Neden ilk açılışta yavaş?
Render.com ücretsiz planında servis 15 dakika inaktiflik sonrası "sleep" moduna girer. İlk açılışta 30-60 saniye ısınma süresi olabilir.

---

## Katkıda Bulunma

1. Fork yapın
2. Branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Push yapın (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

---

## Lisans

Bu proje MIT lisansı altında dağıtılır. Detaylı bilgi için [LICENSE](LICENSE) dosyasına bakın.

---

## İletişim

- **Geliştirici:** [Memati8383](https://github.com/Memati8383)
- **Proje:** [film-izle-hd](https://github.com/Memati8383/film-izle-hd)
- **Canlı Demo:** [https://film-izle-hd.onrender.com](https://film-izle-hd.onrender.com)

---

## Teşekkürler

- [Artplayer](https://artplayer.org/) - Video oynatıcı kütüphanesi
- [HLS.js](https://github.com/video-dev/hls.js/) - HLS streaming desteği
- [Render.com](https://render.com) - Ücretsiz hosting
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping
