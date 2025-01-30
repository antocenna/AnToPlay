import random
from utils import *
from flask import Flask, session


def inizializza_gioco():
    db = get_database()
    impiccato_collection = db['impiccato']

    game = impiccato_collection.find_one({'utente_id' : session['utente'], 'game_over' : False})

    # Inizializza il gioco solo se è la prima visita
    if game is None:
        lista_parole = []
        words_collection = db['words']
        for word in words_collection.find():
            lista_parole.append(word['word'])

        parola = random.choice(lista_parole)
        while len(parola) < 3:
            parola = random.choice(lista_parole)

        game = {
            'utente_id' : session['utente'],
            'parola' : parola,
            'lettere_parola' : list(parola),
            'parola_indovinata' : ["_"] * len(parola),
            'tentativi' : 5,
            'game_over' : False,
            'esito' : None
        }

        impiccato_collection.insert_one(game)

    return game



def aggiorna_gioco(game):
    db = get_database()
    impiccato_collection = db['impiccato']

    impiccato_collection.update_one(
            {'_id': game['_id']},  # Condizione di ricerca (trova il gioco giusto usando l'_id)
            {'$set': {  # Specifica che vuoi aggiornare determinati campi
            'parola_indovinata': game['parola_indovinata'],
            'tentativi': game['tentativi'],
            'game_over': game['game_over'],
            'esito': game['esito']
            }}
        )



def impiccato():
    
    parole = []
    with open('file_giochi/lista_parole_impiccato.txt', mode = 'r') as file:
        for line in file:
            parole.append(line.strip())

    parola = random.choice(parole)
    while len(parola) < 3:
        parola = random.choice(parola)
    
    lettere_parola = list(parola)
    parola_indovinata = ["_"] * len(parola)

    tentativi = 5
    vinto = False

    while tentativi > 0 and not vinto :
        guess = input(f"Inserisci la lettera che vuoi provare (rimasti {tentativi} tentativi): ").lower()

        if guess in lettere_parola:
            print("La lettera inserita è corretta!")

            for i in range(len(parola)):
                if lettere_parola[i] == guess:
                    parola_indovinata[i] = guess 
            
            print(f"Parola attuale:", " ".join(parola_indovinata))
            
            if '_' not in parola_indovinata:
                print("Complimenti, hai vinto!")
                vinto = True
            
        else:
            print("La lettera inserita non è corretta!")
            print(f"Parola attuale:", " ".join(parola_indovinata))   
            tentativi -= 1

        print("-" * 20)

    
    if tentativi == 0:
        print("Mi dispiace, hai  finito i tentativi!")
        print(f"La parola era: {parola}")


if(__name__ == "__main__"):
    print("Benvenuto al gioco dell'impiccato!")
    impiccato()
