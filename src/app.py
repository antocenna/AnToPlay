import time
from utils import *
from impiccato import *
from sudoku2 import *

from Crypto.Cipher import AES
import bcrypt


from flask import Flask, jsonify, render_template, request, redirect, url_for, session

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
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

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
        if not bcrypt.checkpw(password.encode('utf-8'), db_password):
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
    
    games = [
        {'name' : "Sasso, Carta, Forbice", 'route' : "scf"}, 
        {'name' : "Impiccato", 'route' : "impiccato"},
        {'name' : "Sudoku", 'route' : "sudoku"}
    ]


    user = session['utente']['username']
    return render_template('dashboard.html', user = user, games = games)




@app.route('/scf', methods = ['GET', 'POST'])
def scf():
    
    if 'utente' not in session:
        return redirect(url_for('login'))
    
    if request.method == "GET":
        return render_template('scf.html')


    if request.method == 'POST':
        
        mosse_possibili = ['sasso', 'carta', 'forbice']
        regole = {
            'carta' : 'sasso',
            'forbice' : 'carta',
            'sasso' : 'forbice'
        }
        mossa_computer = random.choice(mosse_possibili)
        data = request.get_json()
        mossa_utente = data['mossa']

        if mossa_utente == mossa_computer:
            return jsonify(success_message = f"Pareggio. La mossa del computer era: {mossa_computer}")
        elif regole[mossa_utente] == mossa_computer:
            return jsonify(success_message = f"Vittoria! La mossa del computer era: {mossa_computer}")
        else:
            return jsonify(error_message = f"Sconfitta :( La mossa del computer era: {mossa_computer}")




@app.route('/impiccato', methods = ['GET', 'POST'])
def impiccato():
    if 'utente' not in session:
        return redirect(url_for('login'))

    game = inizializza_gioco()

    if request.method == 'POST' and not game['game_over']:
        guess = request.form.get('lettera')

        if game['game_over']:
            return redirect(url_for('impiccato'))

            
        if guess in game['lettere_parola']:

            for i in range(len(game['parola'])):
                if game['lettere_parola'][i] == guess:
                    game['parola_indovinata'][i] = guess
            
            if '_' not in game['parola_indovinata']:
                game['game_over'] = True
                game['esito'] = 'Vittoria!'
            
        else: 
            game['tentativi'] -= 1
            
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
        redirect(url_for('login'))

    user = session['utente']
    db = get_database()
    sudoku_collection = db['sudoku']
    sudoku_utente = sudoku_collection.find_one({'utente' : user['username']})

    if request.method == 'GET':
        if sudoku_utente:
            app.logger.debug(f"Griglia della soluzione (else): {sudoku_utente['griglia_soluzione']}")
            app.logger.debug(f"Griglia da giocare (else): {sudoku_utente['griglia_da_giocare']}")
            return render_template('sudoku.html', griglia = sudoku_utente['griglia_da_giocare'])
        else:
            #Creiamo la griglia vuota, e poi la riempiamo
            griglia = crea_griglia_vuota()
            riempi_griglia(griglia)
            app.logger.debug(f"Griglia della soluzione: {griglia}")

            griglia_modificata = rimozione_numeri_griglia(griglia, 70)
            app.logger.debug(f"Griglia da giocare: {griglia_modificata}")

            sudoku_collection.insert_one({
                'utente': user['username'],
                'griglia_soluzione': griglia,
                'griglia_da_giocare': griglia_modificata,
                'stato': 'pronto_per_giocare',
                'vite' : 10})
            
            return render_template('sudoku.html', griglia = griglia_modificata, vite = 10)
            
            
    if request.method == 'POST':

        data = request.get_json()
        azione = data.get('azione')


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
                }}
            )
            return render_template('sudoku.html', griglia = griglia_modificata, vite = 10)


        riga = int(data['riga'])
        app.logger.debug(f"Riga numero inserito: {riga}")
        colonna = int(data['colonna'])
        app.logger.debug(f"Colonna numero inserito: {colonna}")
        numero = int(data['numero'])
        app.logger.debug(f"Numero inserito: {numero}")

            
        if sudoku_utente:
            if 1 <= numero <= 9:
                vite = sudoku_utente['vite']
                if vite > 0:
                    griglia_da_giocare = sudoku_utente['griglia_da_giocare']
                    griglia_soluzione = sudoku_utente['griglia_soluzione']
                    if griglia_da_giocare == griglia_soluzione:
                        return jsonify(success_message = 'Hai completato il sudoku!')
                    
                    app.logger.debug(f"Griglia soluzione (recuperata): {griglia_soluzione}")
                    app.logger.debug(f"Griglia da giocare (recuperata): {griglia_da_giocare}")
                    app.logger.debug(f"Riga griglia: {riga}")
                    app.logger.debug(f"Colonna Griglia: {colonna}")
                    app.logger.debug(f"Numero della soluzione: {griglia_soluzione[riga][colonna]}")
                    if numero == griglia_soluzione[riga][colonna]:
                        griglia_da_giocare[riga][colonna] = numero
                        sudoku_collection.update_one(
                            {'utente': user['username']},
                            {'$set': {'griglia_da_giocare': griglia_da_giocare, 'vite' : vite}}
                        )
                        return jsonify(success_message = 'Numero corretto!', vite = vite)
                        #return redirect(url_for('sudoku', success_message = "Numero corretto!"))
                    else:
                            # Numero non corretto
                        vite -= 1
                        sudoku_collection.update_one(
                        {'utente': user['username']},
                        {'$set': {'vite' : vite}}
                        )
                        return jsonify(error_message = 'Numero incorretto, una vita in meno', vite = vite)
                        #return redirect(url_for("sudoku", error_message = "Numero incorretto, una vita in meno"))
                else:
                    sudoku_collection.update_one(
                        {'utente': user['username']},
                        {'$set': {'vite' : 3}}
                        )
                    return jsonify(error_message = 'Errore, vite terminate!', vite = 0)
                    #return redirect(url_for('sudoku', error_message = "Errore, vite terminate!"))
            else:
                return jsonify(error_message = 'Errore, inserire un numero tra 1 e 9.')
                #return redirect(url_for('sudoku', error_message = "Errore, inserire un numero tra 1 e 9."))



if __name__ == '__main__':
    salva_parole()
    app.run(debug=True, host='0.0.0.0', port=8000)