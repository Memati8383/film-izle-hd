"""
Film İzle HD - Film Izleyici (CLI + Web Player)
Kullanici istedigi filmi aratir, secip reklamsiz olarak aninda izler.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import time
import subprocess
import shutil
import os
from extractor import search_movies, get_movie_details
from player_server import play_movie, SERVER_PORT


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    banner = r"""
======================================================================
   ____ _                _        _       _           _ 
  / ___| |__   ___  __ _| |_ __ _| | ___ | |__   __ _| |
 | |   | '_ \ / _ \/ _` | __/ _` | |/ _ \| '_ \ / _` | |
 | |___| | | |  __/ (_| | || (_| | | (_) | |_) | (_| | |
  \____|_| |_|\___|\__,_|\__\__, |_|\___/|_.__/ \__,_|_|
                            |___/                       
       ______      _                                _ 
      / ___|___ | |__   ___ _ __  _ __   ___ _ __(_)
     | |   / _ \| '_ \ / _ \ '_ \| '_ \ / _ \ '__| |
     | |__|  __/| | | |  __/ | | | | | |  __/ |  | |
      \____\___||_| |_|\___|_| |_|_| |_|\___|_|  |_|
======================================================================
          🔥 FILM IZLE HD v2.2 - FULL HD 🔥
     🎬 Reklamsız, Donmasız & Full HD (1080p) Film Platformu
======================================================================
"""
    print(banner)


def open_with_external_player(m3u8_url):
    vlc_paths = [
        shutil.which('vlc'),
        r'C:\Program Files\VideoLAN\VLC\vlc.exe',
        r'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe',
    ]
    mpv_path = shutil.which('mpv')
    pot_paths = [
        shutil.which('PotPlayerMini64.exe'),
        r'C:\Program Files\DAUM\PotPlayer\PotPlayerMini64.exe',
    ]

    players = []
    for p in vlc_paths:
        if p and os.path.exists(p):
            players.append(('vlc', p))
            break
    if mpv_path and os.path.exists(mpv_path):
        players.append(('mpv', mpv_path))
    for p in pot_paths:
        if p and os.path.exists(p):
            players.append(('potplayer', p))
            break

    found_player = players[0] if players else None
            
    if found_player:
        name, path = found_player
        print(f"\n[+] {name.upper()} oynatıcısı ile başlatılıyor...")
        subprocess.Popen([path, m3u8_url, "--http-header-fields=Referer: https://ksdpictures.site/\r\nOrigin: https://ksdpictures.site/"])
        return True
    else:
        print("\n[!] Sisteminizde VLC veya MPV bulunamadı. Tarayıcı oynatıcısı önerilir.")
        return False


def main():
    clear_console()
    print_banner()
    
    while True:
        try:
            print("\n" + "-"*68)
            query = input("🔍 İzlemek istediğiniz film adını yazın (Çıkış için 'q'): ").strip()
            
            if not query:
                continue
            if query.lower() in ['q', 'exit', 'quit', 'cikis', 'çıkış']:
                print("\nİyi seyirler! Film İzle HD kapatılıyor...")
                break
                
            print(f"\n⏳ '{query}' aranıyor...")
            results = search_movies(query)
            
            if not results:
                print(f"[!] '{query}' için sonuç bulunamadı. Farklı bir arama deneyin.")
                continue
                
            print(f"\n🎯 Bulunan Filmler ({len(results)} sonuç):")
            print("="*68)
            for idx, movie in enumerate(results[:15], start=1):
                year_info = f" ({movie['year']})" if movie['year'] else ""
                rating_info = f" [⭐ IMDb: {movie['rating']}]" if movie['rating'] else ""
                print(f"  [{idx:2d}] {movie['title']}{year_info}{rating_info}")
            print("="*68)
            
            while True:
                choice = input(f"\nİzlemek istediğiniz film numarasını seçin (1-{min(len(results), 15)}) veya (0: Yeni Arama): ").strip()
                if choice == '0':
                    break
                if not choice.isdigit() or int(choice) < 1 or int(choice) > min(len(results), 15):
                    print("[!] Geçersiz numara. Lütfen listedeki bir numarayı girin.")
                    continue
                    
                selected_movie = results[int(choice) - 1]
                print(f"\n⏳ '{selected_movie['title']}' akışları çözümleniyor...")
                details = get_movie_details(selected_movie['url'])
                
                if not details or not details.get('streams'):
                    print("[!] Bu film için video akışı bulunamadı (Film henüz eklenmemiş olabilir).")
                    break
                    
                hls_stream = None
                for s in details['streams']:
                    if s.get('type') == 'hls':
                        hls_stream = s
                        break
                        
                if not hls_stream:
                    print("[!] Doğrudan HLS akışı bulunamadı.")
                    break
                    
                print("\n✅ Film Başarıyla Çözümlendi!")
                print(f"🎬 Başlık: {details['title']}")
                if details.get('orig_title'):
                    print(f"📌 Orijinal Ad: {details['orig_title']}")
                print(f"📡 Kaynak: {hls_stream['source_name']}")
                print(f"🔊 Ses & Altyazı: Türkçe Dublaj / Orijinal & Altyazı seçenekleri mevcut")
                
                print("\n" + "="*68)
                print("1. Tarayıcıda İzle (Önerilen - Reklamsız Dahili Web Oynatıcı)")
                print("2. Harici Oynatıcı ile Aç (VLC / MPV)")
                print("3. M3U8 ve Altyazı Linklerini Göster")
                print("0. Ana Menüye Dön")
                print("="*68)
                
                action = input("Seçiminiz (1/2/3/0): ").strip()
                if action == '1' or action == '':
                    watch_url = play_movie(details, open_browser=True)
                    print(f"\n🍿 Film Film İzle HD oynatıcısında açılıyor: {watch_url}")
                    print("📌 Oynatıcı ayarlarından Dublaj/Altyazı ve Kalite (1080p) seçebilirsiniz.")
                    print("💡 Bu pencereyi açık tutun (Oynatıcı sunucusu çalışıyor).")
                elif action == '2':
                    success = open_with_external_player(hls_stream['m3u8_url'])
                    if not success:
                        play_movie(details, open_browser=True)
                elif action == '3':
                    print(f"\n🔗 M3U8 Master Playlist:\n{hls_stream['m3u8_url']}")
                    print("\n📝 Altyazılar:")
                    for t in hls_stream.get('tracks', []):
                        print(f"  - {t.get('label')}: {t.get('file')}")
                        
                input("\n[Devam etmek için Enter'a basın...]")
                break
                
        except KeyboardInterrupt:
            print("\nProgram sonlandırıldı.")
            break
        except Exception as e:
            print(f"\n[!] Bir hata oluştu: {e}")


if __name__ == '__main__':
    main()
