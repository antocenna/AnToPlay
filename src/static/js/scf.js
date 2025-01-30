//Funzione per l'invio della mossa al server
function inviaMossa(mossa) {
    fetch('/scf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'mossa' : mossa })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Errore nella richiesta');
        }
        return response.json();
    })
    .then(data => {
        const messageContainer = document.getElementById('message-container');
        if (data.success_message) {
            displayMessage('success', data.success_message);
        } else if (data.error_message) {
            displayMessage('error', data.error_message);
        }
    })
    .catch(error => {
        console.error('Errore:', error);
    });
}


// Funzione per visualizzare i messaggi (successo o errore)
function displayMessage(type, message) {
    // Rimuovi eventuali messaggi precedenti
    const existingBanner = document.querySelector('.banner');
    if (existingBanner) {
        existingBanner.remove();
    }

    // Crea un nuovo banner
    const banner = document.createElement('div');
    banner.className = `banner ${type === 'success' ? 'banner-success' : 'banner-error'}`;
    banner.textContent = message;
    document.body.prepend(banner); // Aggiunge il banner all'inizio della pagina

    // Imposta un timer per rimuovere il banner dopo un po'
    setTimeout(() => {
        banner.remove();
    }, 5000); // Rimuove il banner dopo 5 secondi
}
