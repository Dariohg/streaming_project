/**
 * Script principal para la aplicación de streaming
 */

document.addEventListener('DOMContentLoaded', function() {
    // Comprobar la conexión a internet y mostrar un mensaje si está offline
    function checkConnection() {
        if (!navigator.onLine) {
            showOfflineMessage();
        } else {
            hideOfflineMessage();
        }
    }

    function showOfflineMessage() {
        // Si no existe aún, crear el mensaje
        if (!document.getElementById('offline-alert')) {
            const offlineAlert = document.createElement('div');
            offlineAlert.id = 'offline-alert';
            offlineAlert.className = 'alert alert-warning';
            offlineAlert.style.position = 'fixed';
            offlineAlert.style.bottom = '20px';
            offlineAlert.style.right = '20px';
            offlineAlert.style.zIndex = '1000';
            offlineAlert.style.maxWidth = '300px';

            offlineAlert.innerHTML = `
                <strong>Modo sin conexión</strong>
                <p>Estás navegando sin conexión a Internet. Algunas funciones pueden no estar disponibles.</p>
            `;

            document.body.appendChild(offlineAlert);
        }
    }

    function hideOfflineMessage() {
        const offlineAlert = document.getElementById('offline-alert');
        if (offlineAlert) {
            offlineAlert.remove();
        }
    }

    // Comprobar conexión al cargar la página
    checkConnection();

    // Comprobar conexión cuando cambia el estado de la red
    window.addEventListener('online', checkConnection);
    window.addEventListener('offline', checkConnection);

    // Manejar mensajes flash para que desaparezcan después de un tiempo
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });

    // Manejar la barra de navegación en dispositivos móviles
    const toggleNavButton = document.getElementById('toggle-nav');
    if (toggleNavButton) {
        const navLinks = document.querySelector('.nav-links');
        toggleNavButton.addEventListener('click', function() {
            navLinks.classList.toggle('show');
        });
    }

    // Formatear fechas en formato local
    const dateElements = document.querySelectorAll('.format-date');
    dateElements.forEach(function(element) {
        const dateStr = element.getAttribute('data-date');
        if (dateStr) {
            const date = new Date(dateStr);
            element.textContent = date.toLocaleDateString();
        }
    });

    // Detectar preferencia de tema oscuro/claro
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        // El usuario prefiere tema claro, pero nuestra app usa tema oscuro por defecto
        // Podríamos agregar un toggle de tema en el futuro
    }
});