import string
from pymongo import MongoClient
import numpy as np

user_path = "users"
data_path = "polls"
server_key = b"16_r4ndom_bytes!"

def validate_string(inp, lb=5, ub=64):
    valid_charset = string.ascii_letters + string.digits  # Caratteri validi: lettere e numeri
    if isinstance(inp, str):
        return lb <= len(inp) <= ub and all(c in valid_charset for c in inp)
    elif isinstance(inp, bytes):
        return lb <= len(inp) <= ub and all(c in valid_charset.encode() for c in inp)
    return False



def get_database():
    # Usa 'mongodb' come hostname, che è il nome del servizio MongoDB nel docker-compose.yml
    client = MongoClient("mongodb://mongodb:27017")  
    return client['GamesDatabase']  # Nome del tuo database



def salva_parole():
    db = get_database()
    words_collection = db['words']
    with open('file_giochi/lista_parole_impiccato.txt', mode='r') as file:
            for line in file:
                parola = line.strip()
                if len(parola) > 3:
                    words_collection.insert_one({'word' : parola})


def exit_service(*args):
    exit()