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

        const art = new Artplayer({
            container: '#artplayer',
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

                            // Kalite Secimi
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
                            } catch(err){}

                            // Ses Dili Secimi (Turkce Dublaj / Orijinal Ingilizce)
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
                            } catch(err){}
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
            theme: '#a855f7',
        });

        // Altyazi varsa ekle
        if (subtitleList.length > 0) {
            try {
                const turkishSub = subtitleList.find(s => s.html.toLowerCase().includes('türk') || s.html.toLowerCase().includes('turk'));
                const subUrl = turkishSub?.url || subtitleList[0].url;
                
                art.subtitle = {
                    url: subUrl,
                    type: 'vtt',
                    style: {
                        color: '#ffffff',
                        fontSize: '26px',
                        textShadow: '0 2px 4px rgba(0,0,0,0.95), 0 0 3px #000'
                    },
                    encoding: 'utf-8',
                };
            } catch(e){}
        }

        if (subtitleList.length > 0) {
            try {
                art.setting.add({
                    width: 200,
                    html: 'Altyazı',
                    tooltip: subtitleList[0].html,
                    selector: [
                        { html: 'Altyazı Kapat', url: '' },
                        ...subtitleList
                    ],
                    onSelect: function (item) {
                        if (item.url) {
                            art.subtitle.switch(item.url, { name: item.html });
                            art.subtitle.show = true;
                        } else {
                            art.subtitle.show = false;
                        }
                        return item.html;
                    },
                });
            } catch(e){}
        }

        function toggleCinema() {
            const body = document.body;
            if (body.style.background === 'rgb(0, 0, 0)') {
                body.style.background = 'var(--bg-main)';
                document.querySelector('.header').style.display = 'flex';
                document.querySelector('.info-bar').style.display = 'flex';
            } else {
                body.style.background = '#000000';
                document.querySelector('.header').style.display = 'none';
                document.querySelector('.info-bar').style.display = 'none';
            }
        }

        function copyStreamUrl() {
            navigator.clipboard.writeText(streamUrl).then(() => {
                alertSuccess('M3U8 Akış Linki panoya kopyalandı!');
            });
        }