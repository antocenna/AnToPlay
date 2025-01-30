document.querySelectorAll('.sudoku-input').forEach(input => {
    input.addEventListener('keydown', function (event) {
        // Controlla se il tasto premuto è "Enter"
        if (event.key === 'Enter') {
            const row = this.parentElement.dataset.row; // Riga della cella
            const col = this.parentElement.dataset.col; // Colonna della cella
            const value = parseInt(this.value); // Valore inserito

            // Invia la richiesta POST al server
            sendUpdateToServer(row, col, value);
        }
    });
});


// Aggiungi l'evento di click al pulsante "Nuova Partita"
document.getElementById('new-game-button').addEventListener('click', function() {
    console.log('Pulsante "Nuova Partita" premuto'); // Log per tracciare il click
    sendUpdateToServer(null, null, null, 'nuova_partita');
});

function sendUpdateToServer(riga, colonna, numero, azione = null) {
    const payload = {
        riga,
        colonna,
        numero,
        azione, // Aggiungi azione "nuova_partita"
    };

    console.log('Invio la richiesta con payload:', payload); // Log per verificare il payload

    fetch('/sudoku', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Errore ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then((data) => {
            console.log('Risposta dal server:', data); // Log per la risposta dal server

            if (data.success_message) {
                console.log('Success message ricevuto: ', data.success_message); // Log per success message
                displayMessage('success', data.success_message);

                if (data.griglia_da_giocare) {
                    console.log('Nuova griglia ricevuta dal server:', data.griglia_da_giocare); // Verifica la griglia
                    updateSudokuGrid(data.griglia_da_giocare); // Aggiorna la griglia
                } else {
                    console.error('Nessuna griglia da giocare ricevuta dal server.');
                }
            } else if (data.error_message) {
                displayMessage('error', data.error_message);
            }
        })
        .catch((error) => {
            console.error('Errore durante la richiesta:', error);
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


function updateSudokuGrid(griglia_da_giocare) {
    console.log('Aggiornamento della griglia con i dati ricevuti:', griglia_da_giocare); // Log per tracciare la griglia

    // Supponiamo che tu abbia delle celle con una classe 'sudoku-input'
    const inputs = document.querySelectorAll('.sudoku-input');

    inputs.forEach((input) => {
        const row = input.parentElement.dataset.row;
        const col = input.parentElement.dataset.col;

        // Imposta il valore nella cella corrispondente
        input.value = griglia_da_giocare[row][col] !== 0 ? griglia_da_giocare[row][col] : '';
    });

    displayMessage('success', 'Una nuova partita è stata iniziata!');
}
