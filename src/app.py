import time
from utils import *
from impiccato import *
from sudoku2 import *

#from Crypto.Cipher import AES
import bcrypt
from hashlib import md5


from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session

app = Flask(__name__)

app.secret_key = "daisy"


@app.context_processor
def utility_processor():
    return dict(enumerate=enumerate)



@app.route('/')
def home():
    '''if 'utente' in session:
        return redirect(url_for('console'))'''
    return render_template('home.html')



@app.route('/register', methods=['GET', 'POST'])
# Se il metodo è post, vuol dire che devo effettuare la registrazione,
# altrimenti, vuol dire che è get, e devo prenderne solo il template
def register():
    if request.method == 'POST': 
        utente = request.form['utente']
        password = request.form['password']

        # Controllo se la password o il nome_utente siano validi (ossia contengono solo lettere e numeri)
        # ev.modifica carattere speciale
        if not validate_string(utente) or not validate_string(password):
            return redirect(url_for('register', error_message = 'Il nome utente e/o la password non rispettano i criteri, riprova.'))
        
        # Otteniamo l'istanza del database
        db = get_database()

        # Otteniamo la collezione dal database
        users_collection = db['users']
        
        # Controlliamo se esiste gia un utente con tale username, e in tal caso vorrebbe dire che l'utente
        # è già registrato
        user = users_collection.find_one({'username' : utente})
        if user:
            return redirect(url_for('login', error_message = 'Utente già registrato, reindirizzamento alla pagina di login'))
        
        # Hashiamo la password tramite bcrypt
        #hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password = md5(password.encode('utf-8')).hexdigest()


        #Creiamo il nuovo utente in formato json per poterlo inserire nel db NoSQL
        new_user = {
            'username' : utente,
            'password' : hashed_password,                 
        }

        users_collection.insert_one(new_user)
        return redirect(url_for('login', success_message = 'Utente registrato correttamente! Accedi di nuovo con le credenziali'))
        
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
# Se il metodo è post, vuol dire che devo effettuare l'accesso,
# altrimenti, vuol dire che è get, e devo prenderne solo il template
def login():
    if request.method == 'POST':
        utente = request.form['utente']
        password = request.form['password']

        # Se non esiste un utente con l'username fornito vuol dire che 
        # non è registrato, e viene rimandato alla pagina di registrazione
        db = get_database()
        users_collections = db['users']
        user = users_collections.find_one({'username' : utente})
        if not user:
            return redirect(url_for('register', error_message = 'Utente non registrato, reindirizzamento alla pagina di registrazione' ))
        
        # Prendiamo la password dell'utente dal db
        # e hashiamo la password inserita per poterle confrontare
        db_password = user['password']  # La password memorizzata nel database, già hashata

        # Controlliamo la password inserita con quella nel database
        # Usiamo bcrypt.checkpw per confrontare la password inserita con quella memorizzata
        #if not bcrypt.checkpw(password.encode('utf-8'), db_password):
        if db_password != md5(password.encode('utf-8')).hexdigest():
            return redirect(url_for('login', error_message = 'Credenziali di accesso non corrette, riprovare'))

        # Convertiamo l'ObjectId in una stringa prima di salvare l'utente nella sessione
        user['_id'] = str(user['_id'])
        
        #Creiamo la sessione per l'utente attuale
        session['utente'] = user

        # Una volta completato l'accesso, si rimanda l'utente alla console
        return redirect(url_for('dashboard', succcess_message = 'Login completato con successo.'))
    
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('utente', None)
    return redirect(url_for('home', success_message = 'Logout effettuato con successo, verrai reindirizzato alla pagina di accesso'))



@app.route('/dashboard')
def dashboard():
    if 'utente' not in session:
        return redirect(url_for('login')) 
    
    # Definisco una lista di giochi con le route associate
    # da passare poi al template
    games = [
        {'name' : "Sasso, Carta, Forbice", 'route' : "scf"}, 
        {'name' : "Impiccato", 'route' : "impiccato"},
        {'name' : "Sudoku", 'route' : "sudoku"}
    ]


    user = session['utente']['username']

    if user == 'admin':
        flag = genera_flag(1)
        return render_template('dashboard.html', user = user, games = games, success_message = f"{flag}")

    return render_template('dashboard.html', user = user, games = games)



@app.route('/scf', methods = ['GET', 'POST'])
def scf():
    
    if 'utente' not in session:
        return redirect(url_for('login'))
    
    if request.method == "GET":
        return render_template('scf.html')


    if request.method == 'POST':
        
        # La logica dietro al gioco è che definisco prima le mosse possibili
        # Poi definisco le regole come un dizionario: la chiave del dizionario vince contro il suo valore

        mosse_possibili = ['sasso', 'carta', 'forbice']
        regole = {
            'carta' : 'sasso',
            'forbice' : 'carta',
            'sasso' : 'forbice'
        }
        mossa_computer = random.choice(mosse_possibili)
        data = request.get_json()
        mossa_utente = data['mossa']

        # Se la mossa dell'utente corrisponde a quella del computer, è un pareggio
        if mossa_utente == mossa_computer:
            return jsonify(success_message = f"Pareggio. La mossa del computer era: {mossa_computer}")
        # Se invece la mossa del computer è pari al valore associato alla chiave (mossa_utente)
        # cio significa che il computer ha perso
        elif regole[mossa_utente] == mossa_computer:
            return jsonify(success_message = f"Vittoria! La mossa del computer era: {mossa_computer}")
        # Se invece non rientra in questi due casi, vuol dire che il computer avrà vinto
        else:
            return jsonify(error_message = f"Sconfitta :( La mossa del computer era: {mossa_computer}")




@app.route('/impiccato', methods = ['GET', 'POST'])
def impiccato():
    if 'utente' not in session:
        return redirect(url_for('login'))

    # Inizializzo il gioco (vedi funzione in impiccato.py)
    game = inizializza_gioco()

    # Se la richiesta è di tipo POST e il gioco non è finito
    if request.method == 'POST' and not game['game_over']:
        # Si prende la lettera dalla richiesta
        guess = request.form.get('lettera')

        if game['game_over']:
            return redirect(url_for('impiccato'))

        # Se la parola è presente tra le lettere della parola da indovinare
        if guess in game['lettere_parola']:
            # Ciò significa che possiamo sostituire la lettera
            # nella parola indovinata, trovando prima la posizione nella parola
            for i in range(len(game['parola'])):
                if game['lettere_parola'][i] == guess:
                    game['parola_indovinata'][i] = guess
            
            # Se non sono presenti trattini bassi
            # vuol dire che la parola da indovinare è stata
            # indovinata, e quindi il gioco si conclude con una vittoria
            if '_' not in game['parola_indovinata']:
                game['game_over'] = True
                game['esito'] = 'Vittoria!'
        
        # Se la lettera non fa parte della parola
        # si deve togliere un tentativo 
        else: 
            game['tentativi'] -= 1

        # e se i tentativi sono finiti il gioco si conclude con una sconfitta
        if game['tentativi'] == 0:
            game['game_over'] = True
            game['esito'] = 'Sconfitta :('
        
        aggiorna_gioco(game)


    return render_template(
        'impiccato.html',
        parola_indovinata=" ".join(game['parola_indovinata']),
        tentativi = game['tentativi'],
        game_over = game['game_over'],
        esito = game['esito'],
        parola = game['parola'] if game['game_over'] else None
    )





@app.route('/sudoku', methods = ['GET', 'POST'])
def sudoku():
    if 'utente' not in session:
        return redirect(url_for('login'))

    user = session['utente']
    db = get_database()
    sudoku_collection = db['sudoku']

    # Per proteggere da attacchi IDOR, basta controllare che l'utente possa vedere solo le proprie partite
    # sudoku_utente = sudoku_collection.find_one({'utente' : user['username']})

    # Recuperiamo il game_id dal database delle partite
    # La condizione importante è che la partita viene cercata
    # in base all'id della partita e non in base a quali sono 
    # i sudoku dell'utente; 
    # Un utente malintenzionato può modificare i parametri dell'url
    # e accedere alle partite di altri giocatori --> Vulnerabilità IDOR
    game_id = request.args.get('id', type = int)
    if game_id:
        sudoku_utente = sudoku_collection.find_one({'id' : game_id})
        if not sudoku_utente:
            return redirect(url_for('dashboard', error_message="Partita non trovata."))  
            # Evita di creare un nuovo Sudoku se l'ID non esiste
    else:
        sudoku_utente = sudoku_collection.find_one({'utente' : user['username']})


    if request.method == 'GET':
        # Se è stato trovato un sudoku, allora si renderizza il template
        if sudoku_utente:
            app.logger.debug(f"Griglia della soluzione (else): {sudoku_utente['griglia_soluzione']}")
            app.logger.debug(f"Griglia da giocare (else): {sudoku_utente['griglia_da_giocare']}")
            return render_template('sudoku.html', 
                                   griglia = sudoku_utente['griglia_da_giocare'], 
                                   vite = sudoku_utente['vite'], 
                                   id_partita = sudoku_utente['id'])
        
        else:
            # Se non è stata trovata partita, dobbiamo crearla
            # Prima però recuperiamo l'ultimo id utilizzato per una partita dal db
            ultima_partita = sudoku_collection.find_one({'id' : {'$ne' : 99}}, sort = [('id', -1)])
            if ultima_partita: 
                id_partita = ultima_partita['id'] + 1
            # Se la partita è quella dell'admin, l'id è fissato a 99
            elif user['username'] == 'admin':
                id_partita = 99
            else:
                id_partita = 1


            #Creiamo la griglia vuota, e poi la riempiamo
            griglia = crea_griglia_vuota()
            riempi_griglia(griglia)
            app.logger.debug(f"Griglia della soluzione: {griglia}")

            # Dopo aver riempito la griglia, rimuoviamo i numeri
            # e la inseriamo poi nel DB
            griglia_modificata = rimozione_numeri_griglia(griglia, 70)
            app.logger.debug(f"Griglia da giocare: {griglia_modificata}")

            sudoku_collection.insert_one({
                'id' : id_partita,
                'utente': user['username'],
                'griglia_soluzione': griglia,
                'griglia_da_giocare': griglia_modificata,
                'stato': 'pronto_per_giocare',
                'vite' : 10})
            

            return render_template('sudoku.html', 
                                   griglia = griglia_modificata, 
                                   vite = 10,
                                   id_partita = id_partita) 
            
            
    if request.method == 'POST':
        # Quando la request è di tipo post, ci sono 3 possibili azioni
        # 1. Inserimento del numero, e vengono passati al backend, 
        #    numero, riga e colonna dove inserire il numero
        # 2. Controllo validità, quando si termina il sudoku,
        #    per controllare se il sudoku è stato completato correttamente
        # 3. Nuova partita, per cominciare una nuova partita dopo averne finita una
        data = request.get_json()
        azione = data.get('azione')
        app.logger.debug(f"Azione: {azione}")

        # Recuperiamo l'id ad ogni richiesta post in quanto
        # ciò ci servirà per poter ricercare la partita, 
        # poiché altrimenti per la vulnerabilità IDOR non si 
        # potrebbe aggiornare la partita a cui si sta cercando di accedere
        id_partita = data.get('id_partita')
        if not id_partita:
            return jsonify(error_message = "Id partita mancante")
        id_partita = int(id_partita)
        app.logger.debug(f"ID Partita ricevuto: {id_partita}")


        # 2. Controllo validita del sudoku rispetto alla soluzione
        if azione == "controlla_validita":

            # Ricarichiamo la partita dal DB per garantire che IDOR funzioni
            sudoku_utente = sudoku_collection.find_one({'id': id_partita})
            if not sudoku_utente:
                return jsonify(error_message="Partita non trovata!")

            app.logger.debug(f"ID partita recuperato: {id_partita}")
            app.logger.debug(f"Griglia soluzione (recuperata): {sudoku_utente.get('griglia_soluzione')}")
            app.logger.debug(f"Griglia da giocare (recuperata): {sudoku_utente.get('griglia_da_giocare')}")

            if sudoku_utente['griglia_da_giocare'] == sudoku_utente['griglia_soluzione']:
                sudoku_collection.update_one(
                    {'id': id_partita},
                    {'$set': {'stato': 'completato'}}
                )
                if id_partita == 99:
                    flag = genera_flag(id_partita)
                    return jsonify(success_message='Hai completato il sudoku!', flag=flag, id_partita = id_partita)
                else:
                    return jsonify(success_message=f"Complimenti {user['username']}, sudoku completato", id_partita = id_partita)

            return jsonify(error_message="Il sudoku non è ancora completo!", id_partita = id_partita)


        # 3. Creazione di una nuova partita
        if azione == "nuova_partita":
            griglia = crea_griglia_vuota()
            riempi_griglia(griglia)
            griglia_modificata = rimozione_numeri_griglia(griglia, 70)

            sudoku_collection.update_one(
                {'utente': user['username']},
                {'$set': {
                    'griglia_soluzione': griglia,
                    'griglia_da_giocare': griglia_modificata,
                    'vite': 10
                }},
                upsert = True
            )
            return render_template('sudoku.html', 
                                   griglia = griglia_modificata, 
                                   vite = 10,
                                   id_partita = id_partita ) 
            
        # 1. Inserimento del numero nel sudoku, 
        # recuperiamo riga, colonna e numero da inserire
        riga = data.get('riga')
        app.logger.debug(f"Riga numero inserito: {riga}")
        colonna = data.get('colonna')
        app.logger.debug(f"Colonna numero inserito: {colonna}")
        numero = data.get('numero')
        app.logger.debug(f"Numero inserito: {numero}")


        if riga is not None and colonna is not None and numero is not None:
            try:
                riga = int(riga)
                colonna = int(colonna)
                numero = int(numero)
            except:
                return jsonify(error_message = "Formato non valido", id_partita = id_partita)
            
            # Recuperiamo ogni volta il sudoku da controllare (perchè l'id potrebbe cambiare)
            sudoku_utente = sudoku_collection.find_one({'id': id_partita})
            if not sudoku_utente:
                return jsonify(error_message="Partita non trovata!", id_partita = id_partita)

            # Il numero del sudoku deve essere compreso tra 1 e 9
            if 1 <= numero <= 9:
                vite = sudoku_utente['vite']

                if vite > 0:
                    # Recuperiamo la griglia completa e la griglia da riempire
                    griglia_da_giocare = sudoku_utente['griglia_da_giocare']
                    griglia_soluzione = sudoku_utente['griglia_soluzione']

                    app.logger.debug(f"Griglia soluzione (recuperata): {griglia_soluzione}")
                    app.logger.debug(f"Griglia da giocare (recuperata): {griglia_da_giocare}")
                    app.logger.debug(f"Riga griglia: {riga}")
                    app.logger.debug(f"Colonna Griglia: {colonna}")
                    app.logger.debug(f"Numero della soluzione: {griglia_soluzione[riga][colonna]}")

                    # Se il numero che vorremmo inserire è quello corretto allora lo inseriamo   
                    if numero == griglia_soluzione[riga][colonna]:
                        griglia_da_giocare[riga][colonna] = numero
                        sudoku_collection.update_one(
                            {'id': id_partita},
                            {'$set': {'griglia_da_giocare': griglia_da_giocare, 'vite' : vite}}
                        )
                        return jsonify(success_message = 'Numero corretto!', vite = vite, id_partita = id_partita)

                    else:
                        # Numero non corretto
                        vite -= 1
                        sudoku_collection.update_one(
                        {'id': id_partita},
                        {'$set': {'vite' : vite}}
                        )
                        return jsonify(error_message = 'Numero incorretto, una vita in meno', vite = vite, id_partita = id_partita)
                
                # In questo ramo si va quando si terminano le vite
                else:
                    sudoku_collection.update_one(
                        {'id': id_partita},
                        {'$set': {'vite' : 3}}
                        )
                    return jsonify(error_message = 'Errore, vite terminate!', vite = 0, id_partita = id_partita)

            else:
                return jsonify(error_message = 'Errore, inserire un numero tra 1 e 9.', id_partita = id_partita)

        return jsonify(error_message = "Richiesta non valida", id_partita = id_partita)


if __name__ == '__main__':
    salva_parole()
    app.run(debug=True, host='0.0.0.0', port=8000)