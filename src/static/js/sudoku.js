// Codice per la gestione frontend del sudoku

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".sudoku-input").forEach((input) => {
        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                const row = this.parentElement.dataset.row;
                const col = this.parentElement.dataset.col;
                const value = parseInt(this.value);

                sendUpdateToServer(row, col, value);
            }
        });
    });

    gameContainer = document.getElementById("game-container");
    id_partita = gameContainer.dataset.id;
    console.log("ID PARTITA: ", id_partita)

    document.getElementById("new-game-button").addEventListener("click", function () {
        sendUpdateToServer(null, null, null, "nuova_partita");
    });
    
    document.getElementById("validate-sudoku").addEventListener("click", function () {
        if (!id_partita) {
            displayMessage("error", "Nessuna partita in corso!");
            return;
        }
        sendUpdateToServer(null, null, null, "controlla_validita");
    });
});

function sendUpdateToServer(riga, colonna, numero, azione = null) {
    const payload = {id_partita, riga, colonna, numero, azione };
    console.log("payload: ", payload)

    fetch("/sudoku", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Errore ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then((data) => {
            if (data.id_partita && !id_partita) {
                id_partita = data.id_partita; // Memorizza l'ID della partita solo se non è già stato impostato
                console.log("ID Partita aggiornato:", id_partita);
            }
        
            if (data.success_message) {
                displayMessage("success", data.success_message);
        
                if (data.flag) {
                    showFlag(data.flag);
                }
        
                if (data.griglia_da_giocare && !data.flag) {
                    updateSudokuGrid(data.griglia_da_giocare);
                }
            } else if (data.error_message) {
                displayMessage("error", data.error_message);
            }
        })
        

function updateSudokuGrid(griglia_da_giocare) {
    document.querySelectorAll(".sudoku-input").forEach((input) => {
        const row = input.parentElement.dataset.row;
        const col = input.parentElement.dataset.col;
        input.value = griglia_da_giocare[row][col] !== 0 ? griglia_da_giocare[row][col] : "";
    });

    displayMessage("success", "Una nuova partita è stata iniziata!");
}

function displayMessage(type, message) {
    const messageContainer = document.getElementById("message-container");
    messageContainer.innerHTML = `<div class="banner ${type === "success" ? "banner-success" : "banner-error"}">${message}</div>`;

    setTimeout(() => {
        messageContainer.innerHTML = "";
    }, 5000);
}

function showFlag(flag) {
    const flagContainer = document.getElementById("flag-container");
    flagContainer.style.display = "block";
    flagContainer.textContent = `🎉 Flag trovata: ${flag}`;
}

}