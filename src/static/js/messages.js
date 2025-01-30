// Funzione per ottenere il valore di un parametro dall'URL
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param); // Restituisce il valore del parametro
}

// Recupera i messaggi dall'URL
const successMessage = getQueryParam('success_message');
const errorMessage = getQueryParam('error_message');

// Mostra il banner di successo
if (successMessage) {
    const banner = document.createElement('div');
    banner.className = 'banner-success'; // Classe per il banner di successo
    banner.textContent = successMessage;
    document.body.prepend(banner); // Aggiunge il banner all'inizio della pagina
}

// Mostra il banner di errore
if (errorMessage) {
    const banner = document.createElement('div');
    banner.className = 'banner-error'; // Classe per il banner di errore
    banner.textContent = errorMessage;
    document.body.prepend(banner); // Aggiunge il banner all'inizio della pagina
}
