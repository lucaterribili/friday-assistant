import os
import json
import pandas as pd
from flask import request, jsonify


def provider_request(request_queue):
    # Verifica che la richiesta sia di tipo POST
    if request.method == 'POST':
        # Ottieni i dati dal corpo della richiesta
        data = request.json

        # Verifica se sono presenti i parametri 'request_id', 'task' e 'items'
        if 'request_id' in data and 'task' in data and 'items' in data:
            request_id = data['request_id']
            task = data['task']
            items = data['items']
            # Inserisci la richiesta nella coda
            request_queue.put((request_id, task, items))

            # Invia un messaggio di conferma
            message = 'Richiesta ricevuta e inserita nella coda'

            response = {
                'message': message,
                'task': task,
                'items': items
            }
            return jsonify(response), 200
        else:
            # Se i parametri richiesti non sono presenti, restituisci un errore
            return jsonify({'error': 'Missing parameters: request_id, task, and/or items'}), 400
    else:
        # Se la richiesta non è di tipo POST, restituisci un errore
        return jsonify({'error': 'Only POST requests are allowed'}), 405


def provider_response(request_id):
    try:
        # Percorso della cartella che contiene i file
        folder_path = f"output/requests/{request_id}"

        # Verifica se la cartella esiste
        if not os.path.exists(folder_path):
            return f"La cartella {request_id} non esiste", 404

        # Controlla se il file status.json esiste nella cartella
        status_file_path = os.path.join(folder_path, "status.json")
        if not os.path.exists(status_file_path):
            return "File status.json non trovato nella cartella", 404

        # Leggi il contenuto di status.json per verificare se contiene la proprietà request_type
        with open(status_file_path, "r") as status_file:
            status_data = json.load(status_file)
            if "request_type" not in status_data:
                return "La proprietà 'request_type' non è presente nel file status.json", 500

        # Inizializza un array per contenere il contenuto di ogni file
        file_contents = []

        # Scansiona tutti i file nella cartella
        # Se il tipo di richiesta è "translations"
        if status_data["request_type"] == "translations":
            translations_df = process_translations(folder_path)
            # Converti il DataFrame in un array multidimensionale
            translations_array = translations_df.values.tolist()
            # Aggiungi l'array alla lista dei contenuti
            file_contents = translations_array
        # Se il tipo di richiesta è "articles"
        elif status_data["request_type"] == "articles":
            # Scansiona tutti i file nella cartella
            for filename in os.listdir(folder_path):
                if filename.endswith('.txt'):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'r') as file:
                        # Leggi il contenuto del file di testo e aggiungilo all'array
                        file_content = file.read()
                        file_contents.append(file_content)
        else:
            return "Tipo di richiesta non supportato", 500

        # Struttura la risposta come un dizionario JSON con l'array di contenuti
        response_data = {
            "contents": file_contents
        }

        # Restituisci la risposta come JSON
        return json.dumps(response_data)
    except Exception as e:
        # Restituisci un messaggio di errore amichevole in caso di eccezione
        return f"Si è verificato un errore: {str(e)}", 500


def process_translations(folder_path):
    translations_csv_path = os.path.join(folder_path, "translations.csv")
    if not os.path.exists(translations_csv_path):
        raise FileNotFoundError("Il file translations.csv non è presente nella cartella")
    df = pd.read_csv(translations_csv_path, sep='\t')
    return df
