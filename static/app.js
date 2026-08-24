        let currentArt = null;
        let allHomeMovies = [];
        let allMoviesScrapeInterval = null;

        // PROFILE SYSTEM (LocalStorage + Dynamic)
        const DEFAULT_PROFILES = [
            { id: 'fi', name: 'Film İzle HD', color: 'avatar-purple', icon: 'fas fa-fire' }
        ];

        function getSavedProfiles() {
            try {
                const data = localStorage.getItem('cg_profiles');
                return data ? JSON.parse(data) : DEFAULT_PROFILES;
            } catch(e) {
                return DEFAULT_PROFILES;
            }
        }

        function saveProfiles(profiles) {
            localStorage.setItem('cg_profiles', JSON.stringify(profiles));
            renderProfiles();
        }

        function renderProfiles() {
            const container = document.getElementById('profileListContainer');
            const profiles = getSavedProfiles();
            container.innerHTML = '';

            profiles.forEach(p => {
                const card = document.createElement('div');
                card.className = 'profile-card';
                card.onclick = () => selectProfile(p.name, p.color, p.icon);

                card.innerHTML = `
                    <div class="profile-avatar ${p.color}">
                        <i class="${p.icon}"></i>
                    </div>
                    <span class="profile-name">${p.name}</span>
                `;
                container.appendChild(card);
            });

            // Add Profile Button
            const addCard = document.createElement('div');
            addCard.className = 'profile-card';
            addCard.onclick = openProfileModal;
            addCard.innerHTML = `
                <div class="profile-avatar avatar-add">
                    <i class="fas fa-plus"></i>
                </div>
                <span class="profile-name">Profil Ekle</span>
            `;
            container.appendChild(addCard);
        }

        function openProfileModal() {
            document.getElementById('profileDropdown').classList.remove('show');
            document.getElementById('profileModal').classList.add('show');
            document.getElementById('profileNameInput').value = '';
            document.getElementById('profileNameInput').focus();
        }

        function closeProfileModal() {
            document.getElementById('profileModal').classList.remove('show');
        }

        // Avatar selector inside modal
        let selectedAvatarColor = 'avatar-purple';
        let selectedAvatarIcon = 'fas fa-fire';

        document.querySelectorAll('.avatar-choice').forEach(el => {
            el.onclick = () => {
                document.querySelectorAll('.avatar-choice').forEach(c => c.classList.remove('selected'));
                el.classList.add('selected');
                selectedAvatarColor = el.getAttribute('data-color');
                selectedAvatarIcon = el.getAttribute('data-icon');
            };
        });

        function saveNewProfile() {
            const nameInput = document.getElementById('profileNameInput').value.trim();
            if (!nameInput) {
                alertWarning('Lütfen bir profil adı girin!');
                return;
            }

            const profiles = getSavedProfiles();
            const newProfile = {
                id: 'p_' + Date.now(),
                name: nameInput,
                color: selectedAvatarColor,
                icon: selectedAvatarIcon
            };
            profiles.push(newProfile);
            saveProfiles(profiles);
            closeProfileModal();
            selectProfile(newProfile.name, newProfile.color, newProfile.icon);
        }

        // Synthesize Netflix Ta-Dum sound using Web Audio API
        function playTaDum() {
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const now = ctx.currentTime;
                
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(80, now);
                osc.frequency.exponentialRampToValueAtTime(30, now + 1.2);
                gain.gain.setValueAtTime(0.5, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 1.4);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(now);
                osc.stop(now + 1.4);

                const osc2 = ctx.createOscillator();
                const gain2 = ctx.createGain();
                osc2.type = 'sine';
                osc2.frequency.setValueAtTime(260, now + 0.1);
                osc2.frequency.exponentialRampToValueAtTime(130, now + 1.8);
                gain2.gain.setValueAtTime(0.4, now + 0.1);
                gain2.gain.exponentialRampToValueAtTime(0.001, now + 2.0);
                osc2.connect(gain2);
                gain2.connect(ctx.destination);
                osc2.start(now + 0.1);
                osc2.stop(now + 2.0);
            } catch(e){}
        }

        // Intro transition
        window.addEventListener('DOMContentLoaded', () => {
            renderProfiles();
            // AudioContext polyfill - tarayici izin vermiyorsa sessiz gec
            setTimeout(() => {
                skipIntro();
            }, 2200);
            loadHomeMovies();
        });

        function skipIntro() {
            const intro = document.getElementById('introScreen');
            if (intro) {
                intro.style.opacity = '0';
                setTimeout(() => intro.style.display = 'none', 800);
            }
        }

        // Profile selection
        function selectProfile(name, avatarClass, iconClass) {
            const navAvatar = document.getElementById('navAvatar');
            const navIcon = document.getElementById('navAvatarIcon');
            
            navAvatar.className = 'nav-avatar ' + avatarClass;
            navIcon.className = iconClass;

            const profileScreen = document.getElementById('profileScreen');
            profileScreen.style.opacity = '0';
            profileScreen.style.transform = 'scale(1.1)';
            setTimeout(() => {
                profileScreen.style.display = 'none';
                const app = document.getElementById('appContainer');
                app.style.opacity = '1';
            }, 500);
        }

        function switchProfileScreen() {
            document.getElementById('profileDropdown').classList.remove('show');
            const profileScreen = document.getElementById('profileScreen');
            const app = document.getElementById('appContainer');
            
            app.style.opacity = '0';
            profileScreen.style.display = 'flex';
            setTimeout(() => {
                profileScreen.style.opacity = '1';
                profileScreen.style.transform = 'scale(1)';
            }, 50);
        }

        function toggleProfileDropdown() {
            document.getElementById('profileDropdown').classList.toggle('show');
        }

        // Navbar scroll effect
        window.addEventListener('scroll', () => {
            const nav = document.getElementById('navbar');
            if (window.scrollY > 40) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }
        });

        // Search Bar Toggle
        function toggleSearch() {
            const box = document.getElementById('searchBox');
            const input = document.getElementById('searchInput');
            box.classList.toggle('open');
            if (box.classList.contains('open')) {
                input.focus();
            }
        }

        document.getElementById('searchInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                doSearch(e.target.value.trim());
            }
        });

        // Load & Render Home Movies
        async function loadHomeMovies() {
            try {
                const res = await fetch('/api/home');
                const data = await res.json();
                const movies = data.movies || data;
                allHomeMovies = movies;

                // Tarama durumunu goster
                if (data.scraping) {
                    showScrapingBanner(data.total || 0);
                }

                if (movies && movies.length > 0) {
                    const featured = movies[0];
                    document.getElementById('heroTitle').innerText = featured.title;
                    if (featured.year) document.getElementById('heroYear').innerText = featured.year;
                    if (featured.rating) document.getElementById('heroRating').innerText = featured.rating;
                    if (featured.img) {
                        document.getElementById('billboard').style.backgroundImage = `
                            linear-gradient(77deg,rgba(0,0,0,.9) 0,rgba(0,0,0,.6) 40%,transparent 85%),
                            linear-gradient(180deg,transparent 0,rgba(20,20,20,.6) 70%,#141414 100%),
                            url('${featured.img}')
                        `;
                    }
                    document.getElementById('heroPlayBtn').onclick = () => playMovieUrl(featured.url, featured.title);

                    // Row 1: Random 15 movies
                    renderMovieCards('rowPopular', movies.slice(0, 15));

                    // Row 2: 2026 movies
                    const m2026 = movies.filter(m => {
                        if (!m.year) return false;
                        const y = m.year.toString();
                        return y.includes('2026') || y.includes('(2026)');
                    });
                    // Fallback: yeterli film varsa goster, yoksa genel listeyi kullan
                    const row2026Movies = m2026.length > 0 ? m2026 : movies.slice(0, 15);
                    renderMovieCards('row2026', row2026Movies);

                    // Row 3: Action / Other
                    renderMovieCards('rowAction', movies.slice(10, 25));
                }
            } catch(e) {
                console.error('Home load error:', e);
            }
        }

        function renderMovieCards(containerId, list) {
            const el = document.getElementById(containerId);
            if (!el) return;
            el.innerHTML = '';

            list.forEach(m => {
                const card = document.createElement('div');
                card.className = 'movie-card';
                card.onclick = () => playMovieUrl(m.url, m.title);

                card.innerHTML = `
                    <img src="${m.img || 'https://via.placeholder.com/300x450?text=Afiş+Yok'}" alt="${m.title}" loading="lazy" />
                    ${m.rating ? `<div class="card-rating"><i class="fas fa-star"></i> ${m.rating}</div>` : ''}
                    ${m.year ? `<div class="card-year">${m.year}</div>` : ''}
                    <div class="card-overlay">
                        <div class="overlay-title">${m.title}</div>
                        <div class="overlay-actions">
                            <div class="btn-circle-play"><i class="fas fa-play"></i></div>
                            <span style="font-size: 11px; font-weight: 700; color: #46d369;">%98 Eşleşme</span>
                            <span style="font-size: 11px; font-weight: 600; color: #aaa;">1080p</span>
                        </div>
                    </div>
                `;
                el.appendChild(card);
            });
        }

        // Scraping Banner
        let scrapeInterval = null;
        function showScrapingBanner(initialCount) {
            const banner = document.getElementById('scrapeBanner');
            const countEl = document.getElementById('scrapeCount');
            banner.classList.add('show');
            countEl.textContent = initialCount;

            if (scrapeInterval) clearInterval(scrapeInterval);
            scrapeInterval = setInterval(async () => {
                try {
                    const res = await fetch('/api/scrape-status');
                    const data = await res.json();
                    countEl.textContent = data.total;
                    if (!data.scraping) {
                        banner.classList.remove('show');
                        clearInterval(scrapeInterval);
                        // Yeniden yukle
                        loadHomeMovies();
                    }
                } catch(e) {}
            }, 3000);
        }

        // Search Handlers
        async function doSearch(query) {
            if (!query) return;
            document.getElementById('homeSection').style.display = 'none';
            document.getElementById('allMoviesSection').style.display = 'none';
            const searchSec = document.getElementById('searchSection');
            searchSec.style.display = 'block';
            document.getElementById('searchResultsTitle').innerText = `'${query}' için Sonuçlar`;
            document.getElementById('loader').style.display = 'block';
            document.getElementById('searchGrid').innerHTML = '';

            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await res.json();
                renderMovieCards('searchGrid', data);
            } catch(err) {
                alertError('Arama hatası');
            } finally {
                document.getElementById('loader').style.display = 'none';
            }
        }

        function doQuickSearch(term) {
            document.getElementById('searchInput').value = term;
            doSearch(term);
        }

        function showHome() {
            document.getElementById('searchSection').style.display = 'none';
            document.getElementById('allMoviesSection').style.display = 'none';
            document.getElementById('homeSection').style.display = 'block';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // ALL MOVIES
        let allMoviesCurrentIndex = 0;
        let allMoviesFiltered = [];
        const ALL_MOVIES_PER_PAGE = 100;

        async function showAllMovies() {
            document.getElementById('homeSection').style.display = 'none';
            document.getElementById('searchSection').style.display = 'none';
            document.getElementById('allMoviesSection').style.display = 'block';
            window.scrollTo({ top: 0, behavior: 'smooth' });

            // Guncel veriyi sunucudan cek
            try {
                const res = await fetch('/api/home');
                const data = await res.json();
                allHomeMovies = data.movies || data;
            } catch(e) {}

            allMoviesFiltered = [...allHomeMovies];
            allMoviesCurrentIndex = 0;
            document.getElementById('allMoviesGrid').innerHTML = '';
            document.getElementById('allMoviesTitle').innerText = `Tüm Filmler (${allMoviesFiltered.length})`;
            loadMoreAllMovies();

            // Tarama devam ediyorsa periyodik guncelle
            if (allMoviesScrapeInterval) clearInterval(allMoviesScrapeInterval);
            allMoviesScrapeInterval = setInterval(async () => {
                try {
                    const r = await fetch('/api/scrape-status');
                    const s = await r.json();
                    document.getElementById('allMoviesTitle').innerText = `Tüm Filmler (${s.total} - Taranıyor...)`;
                    if (!s.scraping) {
                        clearInterval(allMoviesScrapeInterval);
                        allMoviesScrapeInterval = null;
                        // Son veriyi cek
                        const r2 = await fetch('/api/home');
                        const d2 = await r2.json();
                        allHomeMovies = d2.movies || d2;
                        allMoviesFiltered = [...allHomeMovies];
                        allMoviesCurrentIndex = 0;
                        document.getElementById('allMoviesGrid').innerHTML = '';
                        document.getElementById('allMoviesTitle').innerText = `Tüm Filmler (${allMoviesFiltered.length})`;
                        loadMoreAllMovies();
                    }
                } catch(e) {}
            }, 5000);
        }

        function loadMoreAllMovies() {
            const grid = document.getElementById('allMoviesGrid');
            const end = Math.min(allMoviesCurrentIndex + ALL_MOVIES_PER_PAGE, allMoviesFiltered.length);
            const slice = allMoviesFiltered.slice(allMoviesCurrentIndex, end);

            slice.forEach(m => {
                const card = document.createElement('div');
                card.className = 'movie-card';
                card.onclick = () => playMovieUrl(m.url, m.title);
                card.innerHTML = `
                    <img src="${m.img || 'https://via.placeholder.com/300x450?text=Film'}" alt="${m.title}" loading="lazy" />
                    ${m.rating ? '<div class="card-rating"><i class="fas fa-star"></i> ' + m.rating + '</div>' : ''}
                    ${m.year ? '<div class="card-year">' + m.year + '</div>' : ''}
                    <div class="card-overlay">
                        <div class="overlay-title">${m.title}</div>
                        <div class="overlay-actions">
                            <div class="btn-circle-play"><i class="fas fa-play"></i></div>
                            ${m.rating ? '<span style="font-size:11px;color:#fbbf24;"><i class="fas fa-star"></i> ' + m.rating + '</span>' : ''}
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });

            allMoviesCurrentIndex = end;
            const remaining = allMoviesFiltered.length - allMoviesCurrentIndex;
            document.getElementById('allMoviesCount').innerText = `${allMoviesCurrentIndex} / ${allMoviesFiltered.length} film gösteriliyor`;
            document.getElementById('allMoviesLoadMore').style.display = remaining > 0 ? 'block' : 'none';
        }

        // Filter & Sort
        document.getElementById('allMoviesFilter').addEventListener('input', function() {
            filterAllMovies();
        });
        document.getElementById('allMoviesSort').addEventListener('change', function() {
            filterAllMovies();
        });

        function filterAllMovies() {
            const query = document.getElementById('allMoviesFilter').value.toLowerCase().trim();
            const sortBy = document.getElementById('allMoviesSort').value;

            let filtered = allHomeMovies.filter(m => {
                if (!query) return true;
                return m.title.toLowerCase().includes(query) ||
                       (m.year && m.year.includes(query)) ||
                       (m.rating && m.rating.includes(query));
            });

            switch(sortBy) {
                case 'year-desc':
                    filtered.sort((a,b) => (b.year||'0').localeCompare(a.year||'0'));
                    break;
                case 'year-asc':
                    filtered.sort((a,b) => (a.year||'9999').localeCompare(b.year||'9999'));
                    break;
                case 'rating-desc':
                    filtered.sort((a,b) => parseFloat(b.rating||'0') - parseFloat(a.rating||'0'));
                    break;
                case 'rating-asc':
                    filtered.sort((a,b) => parseFloat(a.rating||'0') - parseFloat(b.rating||'0'));
                    break;
                case 'title-asc':
                    filtered.sort((a,b) => a.title.localeCompare(b.title, 'tr'));
                    break;
                case 'title-desc':
                    filtered.sort((a,b) => b.title.localeCompare(a.title, 'tr'));
                    break;
            }

            allMoviesFiltered = filtered;
            allMoviesCurrentIndex = 0;
            document.getElementById('allMoviesGrid').innerHTML = '';
            document.getElementById('allMoviesTitle').innerText = `Tüm Filmler (${filtered.length})`;
            loadMoreAllMovies();
        }

        // Movie Playback
        async function playMovieUrl(movieUrl, title) {
            const modal = document.getElementById('videoModal');
            document.getElementById('modalTitle').innerHTML = `<span>${title}</span> &bull; <small style="color:#808080; font-size:14px;">Akış Başlatılıyor...</small>`;
            modal.classList.add('active');

            try {
                const res = await fetch(`/api/details?url=${encodeURIComponent(movieUrl)}`);
                const data = await res.json();

                if (!data || !data.streams || data.streams.length === 0) {
                    alertWarning('Bu film için henüz yayın akışı eklenmemiş.');
                    closeModal();
                    return;
                }

                const hlsStream = data.streams.find(s => s.type === 'hls');
                if (!hlsStream) {
                    alertError('HLS akışı bulunamadı.');
                    closeModal();
                    return;
                }

                document.getElementById('modalTitle').innerHTML = `<span>${data.title}</span>`;
                const proxiedUrl = `/hls/playlist.m3u8?url=${encodeURIComponent(hlsStream.m3u8_url)}`;
                
                setTimeout(() => {
                    setupPlayer(proxiedUrl, hlsStream.tracks);
                }, 100);
            } catch (err) {
                alertError('Film yüklenirken hata oluştu: ' + err.message);
                closeModal();
            }
        }

        function setupPlayer(streamUrl, tracks) {
            if (currentArt) {
                currentArt.destroy();
                currentArt = null;
            }

            let subtitleList = [];
            if (tracks && tracks.length > 0) {
                tracks.forEach((t, i) => {
                    subtitleList.push({
                        default: t.default || false,
                        html: t.label || ('Altyazı ' + (i+1)),
                        url: '/hls/subtitle.vtt?url=' + encodeURIComponent(t.file),
                    });
                });
            }

            currentArt = new Artplayer({
                container: '#modalArtplayer',
                url: streamUrl,
                type: 'm3u8',
                customType: {
                    m3u8: function(video, url, artInstance) {
                        if (Hls.isSupported()) {
                            if (artInstance.hls) artInstance.hls.destroy();
                            const hls = new Hls({
                                maxBufferLength: 60,
                                maxMaxBufferLength: 180,
                                enableWorker: true,
                                backBufferLength: 60
                            });
                            hls.loadSource(url);
                            hls.attachMedia(video);
                            artInstance.hls = hls;

                            hls.on(Hls.Events.MANIFEST_PARSED, function (event, data) {
                                try {
                                    video.play().catch(function(){});
                                } catch(e){}

                                // Kalite
                                try {
                                    if (hls.levels && hls.levels.length > 1) {
                                        const levels = hls.levels.map((level, index) => ({
                                            html: (level.height ? level.height + 'p' : 'Seviye ' + (index+1)),
                                            index: index,
                                            default: index === hls.currentLevel
                                        }));
                                        levels.unshift({ html: 'Otomatik', index: -1, default: true });

                                        artInstance.setting.add({
                                            width: 200,
                                            html: 'Kalite',
                                            tooltip: 'Otomatik',
                                            selector: levels,
                                            onSelect: function (item) {
                                                artInstance.hls.currentLevel = item.index;
                                                return item.html;
                                            },
                                        });
                                    }
                                } catch(e){}

                                // Ses
                                try {
                                    if (hls.audioTracks && hls.audioTracks.length > 1) {
                                        const audioOptions = hls.audioTracks.map((track, index) => ({
                                            html: track.name || track.lang || ('Ses ' + (index+1)),
                                            index: index,
                                            default: index === hls.audioTrack
                                        }));

                                        artInstance.setting.add({
                                            width: 200,
                                            html: 'Ses Dili',
                                            tooltip: audioOptions[0].html,
                                            selector: audioOptions,
                                            onSelect: function (item) {
                                                artInstance.hls.audioTrack = item.index;
                                                return item.html;
                                            },
                                        });
                                    }
                                } catch(e){}
                            });

                            hls.on(Hls.Events.ERROR, function (event, data) {
                                if (data.fatal) {
                                    switch (data.type) {
                                        case Hls.ErrorTypes.NETWORK_ERROR:
                                            hls.startLoad();
                                            break;
                                        case Hls.ErrorTypes.MEDIA_ERROR:
                                            hls.recoverMediaError();
                                            break;
                                        default:
                                            hls.destroy();
                                            break;
                                    }
                                }
                            });

                            artInstance.on('destroy', () => hls.destroy());
                        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                            video.src = url;
                            video.play().catch(function(){});
                        }
                    }
                },
                volume: 0.8,
                autoplay: true,
                pip: true,
                screenshot: true,
                setting: true,
                playbackRate: true,
                aspectRatio: true,
                fullscreen: true,
                fullscreenWeb: true,
                theme: '#e50914',
                subtitle: subtitleList.length > 0 ? {
                    url: subtitleList.find(s => s.html.toLowerCase().includes('türk') || s.html.toLowerCase().includes('turk'))?.url || subtitleList[0].url,
                    type: 'vtt',
                    style: {
                        color: '#ffffff',
                        fontSize: '26px',
                        textShadow: '0 2px 4px rgba(0,0,0,0.95), 0 0 3px #000'
                    },
                } : undefined,
            });

            if (subtitleList.length > 0) {
                try {
                    currentArt.setting.add({
                        width: 200,
                        html: 'Altyazı',
                        tooltip: subtitleList[0].html,
                        selector: [
                            { html: 'Altyazı Kapat', url: '' },
                            ...subtitleList
                        ],
                        onSelect: function (item) {
                            if (item.url) {
                                currentArt.subtitle.switch(item.url, { name: item.html });
                                currentArt.subtitle.show = true;
                            } else {
                                currentArt.subtitle.show = false;
                            }
                            return item.html;
                        },
                    });
                } catch(e){}
            }
        }

        function closeModal() {
            if (currentArt) {
                currentArt.destroy();
                currentArt = null;
            }
            document.getElementById('videoModal').classList.remove('active');
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });