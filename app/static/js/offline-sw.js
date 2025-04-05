// Service Worker para modo offline
self.addEventListener('install', function(event) {
    console.log('Service Worker instalado');
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    console.log('Service Worker activado');
    return self.clients.claim();
});

// Interceptar solicitudes de red
self.addEventListener('fetch', function(event) {
    const url = new URL(event.request.url);

    // Solo interceptar solicitudes de video
    if (url.pathname.includes('/video/')) {
        // Comprobar estado de conexión usando mensajes desde la página principal
        if (self.isOffline) {
            console.log('Modo offline: Bloqueando solicitud:', url.pathname);

            // Responder con un error para que el navegador detenga la carga
            event.respondWith(
                new Response('Offline mode', {
                    status: 503,
                    statusText: 'Service Unavailable'
                })
            );
            return;
        }
    }

    // Para otras solicitudes, comportamiento normal
    event.respondWith(fetch(event.request));
});

// Escuchar mensajes desde la página principal
self.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'CONNECTION_STATUS') {
        self.isOffline = event.data.isOffline;
        console.log('Service Worker: Modo offline =', self.isOffline);
    }
});