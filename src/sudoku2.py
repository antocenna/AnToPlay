import copy
import numpy as np
import random
import hashlib
import os
from utils import *

chiave_segreta = os.environ.get("SUDOKU_UTENTE")


def genera_flag(id_partita):
    base = f"{id_partita}-{chiave_segreta}"
    return "UNINA{" + hashlib.sha256(base.encode()).hexdigest()[:10] + "}"


def crea_griglia_vuota():
    #griglia = np.zeros(shape = (9, 9), dtype = int)
    griglia = []
    for _ in range(9):
        griglia.append([0] * 9)
    #griglia = [[0 for _ in range(9)] for _ in range(9)]
    return griglia



def numero_valido(numero, riga, colonna, griglia):
    # Per controllare se il numero inserito è valido,
    # dobbiamo controllare:
    # 1. Se il numero inserito non si ripete nella riga
    # 2. Se il numero inserito non si ripete nella colonna
    # 3. Se il numero inserito non si ripete nella sottogriglia 3x3
    # Se una di queste condizioni fallisce, il numero non può essere inserito

    # Condizione 1. Riga
    if numero in griglia[riga]:
        return False
    
    # Condizione 2. Colonna
    for riga_variabile in range(9):
        if griglia[riga_variabile][colonna] == numero:
            return False
        
    # Condizione 3. Sottogriglia 3x3
    # Determiniamo a quale sottogriglia appartiene 
    # la casella che vogliamo riempire
    # Quest'operazione ci restituisce la riga iniziale della sottogriglia
    # Es. Riga = 7 -> (7 // 3) * 3 = 6
    riga_sottogriglia = (riga // 3) * 3
    # Es. Colonna = 5 -> (5 // 3) * 3 = 3
    colonna_sottogriglia = (colonna // 3) * 3
    for i in range(riga_sottogriglia, riga_sottogriglia + 3):
        for j in range(colonna_sottogriglia, colonna_sottogriglia + 3):
            if griglia[i][j] == numero:
                return False
    
    return True

        

def riempi_griglia(griglia):
    # Iteriamo con due cicli for, uno per le righe, uno per le colonne
    for riga in range(9):
        for colonna in range(9):
            # Troviamo la prima cella vuota
            if griglia[riga][colonna] == 0:
                # Definiamo i numeri possibili come una lista da 1 a 9
                print(f"Trovata cella vuota: ({riga}, {colonna})")
                numeri_possibili = list(range(1, 10))
                random.shuffle(numeri_possibili)
                # Finche la listà non è vuota 
                # (una lista vuota in python è valutata come False)
                for numero in numeri_possibili:
                    # Controlliamo che sia possibile inserire
                    # il numero tramite la funzione
                    # e in tal caso lo inseriamo
                    if numero_valido(numero, riga, colonna, griglia):
                        griglia[riga][colonna] = numero
                        print(f"Inserito {numero} in ({riga}, {colonna})")
                        # Effettuiamo una chiamata ricorsiva, per valutare se è
                        # possibile inserire QUEL numero in quella determinata casella
                        # passando alla casella successiva; se nella casella successiva
                        # non ci sono numeri validi, si ritorna alla cella precedente
                        # la si rimette a 0 e si riprova con un altro numero
                        if riempi_griglia(griglia):
                            return True  
                        else:
                            print(f"Backtracking su ({riga}, {colonna})")
                            griglia[riga][colonna] = 0   
                # Qui si arriva quando non ci sono più numeri nella lista
                # Quindi il numero inserito in precedenza non va bene, e si deve
                # tornare alla cella precedente
                return False  
    # Se non ci sono celle vuote, la griglia è completa, 
    # quindi possiamo anche caricarla nel DB
    '''db = get_database()
    sudoku_collection = db['sudoku']
    sudoku_collection.insert_one({'stato': 'soluzione', 'griglia' : griglia})'''
    return True  



def risolutore(griglia, soluzioni):
    # Risolutore per sudoku, serve per verificare se la rimozione dalla griglia funziona
    # Iteriamo con due cicli for, uno per le righe, uno per le colonne
    for riga in range(9):
        for colonna in range(9):
            # Troviamo la prima cella vuota
            if griglia[riga][colonna] == 0:
                for numero in range(1, 10):
                    # Controlliamo che sia possibile inserire
                    # il numero tramite la funzione
                    # e in tal caso lo inseriamo
                    if numero_valido(numero, riga, colonna, griglia):
                        griglia[riga][colonna] = numero 
                        # Effettuiamo una chiamata ricorsiva, per valutare se è
                        # possibile inserire QUEL numero in quella determinata casella
                        # passando alla casella successiva; se nella casella successiva
                        # non ci sono numeri validi, si ritorna alla cella precedente
                        # la si rimette a 0 e si riprova con un altro numero
                        soluzioni = risolutore(griglia, soluzioni)
                        griglia[riga][colonna] = 0   
                    # Qui si arriva quando non ci sono più numeri nella lista
                    # Quindi il numero inserito in precedenza non va bene, e si deve
                    # tornare alla cella precedente
                return soluzioni  
    # Se non ci sono celle vuote, la griglia è completa
    return soluzioni + 1  


def rimozione_numeri_griglia(griglia, numero_rimozioni):

    # Copiamo la griglia originale per non modificarla direttamente
    griglia_modificata = copy.deepcopy(griglia)

    # Scriviamo una lista che contiene tutte le celle
    # ((0, 1), (0, 2), (0, 3), ... , (7, 8), (8, 8))
    celle = []
    for riga in range(9):
        for colonna in range(9):
            celle.append((riga, colonna))

    # Le mescoliamo in maniera da rimuovere numeri casuali
    random.shuffle(celle)
    # Impostiamo un contatore per vedere quante rimozioni abbiamo effettuato
    # Se supera il numero di rimozioni prestabilito, la funzione deve terminare
    rimozioni = 0


    for riga, colonna in celle:

        if rimozioni >= numero_rimozioni:
            break
        
        # Effettuiamo una rimozione simmetrica
        # Es. se rimuoviamo (0, 1) toglieremo anche (8, 7)
        riga_simmetrica = 8 - riga
        colonna_simmetrica = 8 - colonna

        # Salviamo il valore delle celle in caso di ripristino 
        valore_originale_cella = griglia_modificata[riga][colonna]
        valore_originale_cella_simmetrica = griglia_modificata[riga_simmetrica][colonna_simmetrica]

        # Azzeriamo la cella
        griglia_modificata[riga][colonna] = 0
        griglia_modificata[riga_simmetrica][colonna_simmetrica] = 0
        

        # Avviamo il risolutore, per vedere se la cella che abbiamo tolto
        # ci garantisce comunque un'unica soluzione
        soluzioni = risolutore(griglia_modificata, soluzioni = 0)
        if soluzioni != 1:
            # Soluzione non attuabile, ripristiniamo i valori originali
            griglia_modificata[riga][colonna] = valore_originale_cella
            griglia_modificata[riga_simmetrica][colonna_simmetrica] = valore_originale_cella_simmetrica
        else:
            # Vuol dire che esiste un'unica soluzione, aumentiamo il contatore
            rimozioni += 2
            print(f"Rimosso numero da ({riga}, {colonna}) e ({riga_simmetrica}, {colonna_simmetrica}). Soluzioni trovate: {soluzioni}")
            print(f"Rimozioni effettuate: {rimozioni}")

    # Inserisco la griglia modificata nel database
    return griglia_modificata




if(__name__ == "__main__"):

    flag = genera_flag(12)
    print(flag)
    print("Generazione griglia sudoku...")
    griglia = crea_griglia_vuota()
    for riga in griglia: 
        print(riga)
    riempi_griglia(griglia = griglia)
    print("Generazione completata!")
    for riga in griglia:
        print(riga)

    griglia_modificata = rimozione_numeri_griglia(griglia, 70)
    print("Divertiti col tuo sudoku!") 
    for riga in griglia_modificata:
        print(riga)
