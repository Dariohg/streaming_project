document.addEventListener('DOMContentLoaded', function() {
    // Registrar Service Worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/offline-sw.js')
        .then(registration => {
            console.log('Service Worker registrado con éxito');
        })
        .catch(error => {
            console.error('Error al registrar Service Worker:', error);
        });
    }

    const videoPlayer = document.getElementById('video-player');
    if (!videoPlayer) return;

    const videoId = videoPlayer.getAttribute('data-video-id');
    const savedTime = parseFloat(videoPlayer.getAttribute('data-current-time') || 0);

    const connectionStatus = document.getElementById('connection-status');
    const connectionText = document.getElementById('connection-text');

    let isOffline = !navigator.onLine;
    let bufferedEndTime = 0;
    let originalVideoSrc = null;

    // Guardar la fuente original del video
    const videoSource = videoPlayer.querySelector('source');
    if (videoSource) {
        originalVideoSrc = videoSource.src;
    }

    // Actualizar información del buffer
    function updateBufferInfo() {
        try {
            if (videoPlayer.buffered.length > 0) {
                bufferedEndTime = videoPlayer.buffered.end(videoPlayer.buffered.length - 1);
                console.log(`Buffer disponible: ${bufferedEndTime.toFixed(2)}s de ${videoPlayer.duration.toFixed(2)}s (${(bufferedEndTime/videoPlayer.duration*100).toFixed(1)}%)`);
            }
        } catch (e) {
            console.error("Error al leer buffer:", e);
        }
    }

    // Interceptar solicitudes de video cuando estamos offline
    function setupFetchInterceptor() {
        const originalFetch = window.fetch;
        window.fetch = function(resource, options) {
            if (isOffline && (typeof resource === 'string') && resource.includes('/video/')) {
                console.log('Interceptando fetch en modo offline:', resource);
                return Promise.reject(new Error('Offline mode active'));
            }
            return originalFetch(resource, options);
        };
    }

    // Configurar video para modo offline
    function enableOfflineMode() {
        console.log("Activando modo offline");

        // 1. Guardar el buffer actual
        updateBufferInfo();

        // 2. Modificar el comportamiento del video
        videoPlayer.addEventListener('waiting', handleWaiting);
        videoPlayer.addEventListener('timeupdate', handleTimeUpdate);

        // 3. Mostrar mensaje
        showOfflineMessage();
    }

    // Desactivar modo offline
    function disableOfflineMode() {
        console.log("Desactivando modo offline");

        videoPlayer.removeEventListener('waiting', handleWaiting);
        videoPlayer.removeEventListener('timeupdate', handleTimeUpdate);
    }

    // Manejar evento 'waiting' (buffering) en modo offline
    function handleWaiting() {
        if (isOffline && videoPlayer.currentTime >= bufferedEndTime - 1) {
            videoPlayer.pause();
            alert("Has llegado al final del buffer disponible. Necesitas conexión a internet para continuar.");
        }
    }

    // Prevenir que el usuario avance más allá del buffer en modo offline
    function handleTimeUpdate() {
        if (isOffline && videoPlayer.currentTime >= bufferedEndTime - 0.5) {
            videoPlayer.currentTime = bufferedEndTime - 1;
            videoPlayer.pause();
            alert("No puedes avanzar más allá del contenido cargado en modo sin conexión.");
        }
    }

    // Mostrar mensaje de modo offline
    function showOfflineMessage() {
        const secondsAvailable = Math.max(0, Math.floor(bufferedEndTime - videoPlayer.currentTime));

        const offlineAlert = document.createElement('div');
        offlineAlert.className = 'offline-message';
        offlineAlert.innerHTML = `
            <strong>Modo sin conexión</strong>
            <p>Puedes reproducir ${secondsAvailable} segundos más del video.</p>
        `;

        document.body.appendChild(offlineAlert);

        setTimeout(() => {
            offlineAlert.style.opacity = '0';
            setTimeout(() => offlineAlert.remove(), 500);
        }, 5000);
    }

    // Actualizar estado de conexión
    function updateConnectionStatus() {
        const wasOffline = isOffline;
        isOffline = !navigator.onLine;

        if (isOffline) {
            connectionStatus.style.backgroundColor = 'var(--danger-color)';
            connectionText.textContent = 'Sin conexión';
            document.body.classList.add('offline');

            if (!wasOffline) {
                enableOfflineMode();
            }
        } else {
            connectionStatus.style.backgroundColor = 'var(--success-color)';
            connectionText.textContent = 'Conectado';
            document.body.classList.remove('offline');

            if (wasOffline) {
                disableOfflineMode();
                syncOfflineProgress();

                // Opcionalmente, preguntar si desea recargar
                if (confirm("Se ha recuperado la conexión. ¿Deseas recargar el video para continuar normalmente?")) {
                    window.location.reload();
                }
            }
        }

        // Comunicar estado al Service Worker
        if (navigator.serviceWorker.controller) {
            navigator.serviceWorker.controller.postMessage({
                type: 'CONNECTION_STATUS',
                isOffline: isOffline
            });
        }
    }

    // Guardar progreso
    function saveProgress() {
        if (!videoId) return;

        const currentTime = videoPlayer.currentTime;
        const duration = videoPlayer.duration;
        const watched = (currentTime / duration) > 0.9;

        if (navigator.onLine) {
            fetch('/api/update-progress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    video_id: videoId,
                    current_time: currentTime,
                    watched: watched
                })
            }).catch(error => {
                console.error('Error al guardar progreso:', error);
                saveProgressOffline(currentTime, watched);
            });
        } else {
            saveProgressOffline(currentTime, watched);
        }
    }

    // Guardar progreso offline
    function saveProgressOffline(currentTime, watched) {
        const offlineProgress = JSON.parse(localStorage.getItem('offlineProgress') || '{}');
        offlineProgress[videoId] = {
            current_time: currentTime,
            watched: watched,
            timestamp: Date.now()
        };
        localStorage.setItem('offlineProgress', JSON.stringify(offlineProgress));
    }

    // Sincronizar progreso offline
    function syncOfflineProgress() {
        const offlineProgress = JSON.parse(localStorage.getItem('offlineProgress') || '{}');

        if (Object.keys(offlineProgress).length === 0) return;

        Object.keys(offlineProgress).forEach(id => {
            const progress = offlineProgress[id];

            fetch('/api/update-progress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    video_id: id,
                    current_time: progress.current_time,
                    watched: progress.watched
                })
            })
            .then(response => {
                if (response.ok) {
                    delete offlineProgress[id];
                    localStorage.setItem('offlineProgress', JSON.stringify(offlineProgress));
                }
            })
            .catch(error => console.error('Error al sincronizar progreso offline:', error));
        });
    }

    // Al cargar el video
    videoPlayer.addEventListener('loadedmetadata', function() {
        if (savedTime > 0 && savedTime < videoPlayer.duration) {
            videoPlayer.currentTime = savedTime;
        }
    });

    // Actualizar buffer en cada progreso
    videoPlayer.addEventListener('progress', updateBufferInfo);

    // Guardar progreso
    videoPlayer.addEventListener('pause', saveProgress);
    videoPlayer.addEventListener('ended', saveProgress);
    window.addEventListener('beforeunload', saveProgress);

    // Interceptar solicitudes de fetch
    setupFetchInterceptor();

    // Inicializar estado de conexión
    updateConnectionStatus();

    // Escuchar cambios en la conexión
    window.addEventListener('online', updateConnectionStatus);
    window.addEventListener('offline', updateConnectionStatus);

    // Agregar estilos CSS para la alerta
    const style = document.createElement('style');
    style.textContent = `
        .offline-message {
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: rgba(229, 9, 20, 0.9);
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 1000;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            transition: opacity 0.5s;
            opacity: 1;
            max-width: 350px;
            font-family: Arial, sans-serif;
        }
        .offline-message strong {
            display: block;
            margin-bottom: 5px;
            font-size: 16px;
        }
        .offline-message p {
            margin: 0;
            font-size: 14px;
        }
    `;
    document.head.appendChild(style);

    // Atajos de teclado
    document.addEventListener('keydown', function(e) {
        if (!videoPlayer) return;

        if (document.activeElement === videoPlayer || document.activeElement === document.body) {
            switch (e.key) {
                case ' ':
                    if (videoPlayer.paused) videoPlayer.play();
                    else videoPlayer.pause();
                    e.preventDefault();
                    break;
                case 'ArrowRight':
                    if (isOffline) {
                        const newTime = videoPlayer.currentTime + 10;
                        if (newTime <= bufferedEndTime - 1) {
                            videoPlayer.currentTime = newTime;
                        } else {
                            videoPlayer.currentTime = bufferedEndTime - 1;
                            alert("No puedes avanzar más allá del contenido cargado en modo sin conexión.");
                        }
                    } else {
                        videoPlayer.currentTime = Math.min(videoPlayer.duration, videoPlayer.currentTime + 10);
                    }
                    e.preventDefault();
                    break;
                case 'ArrowLeft':
                    videoPlayer.currentTime = Math.max(0, videoPlayer.currentTime - 10);
                    e.preventDefault();
                    break;
                case 'f':
                    if (videoPlayer.requestFullscreen) videoPlayer.requestFullscreen();
                    else if (videoPlayer.webkitRequestFullscreen) videoPlayer.webkitRequestFullscreen();
                    else if (videoPlayer.msRequestFullscreen) videoPlayer.msRequestFullscreen();
                    e.preventDefault();
                    break;
                case 'm':
                    videoPlayer.muted = !videoPlayer.muted;
                    e.preventDefault();
                    break;
            }
        }
    });
});