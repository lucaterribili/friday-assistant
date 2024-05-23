import re
import csv
import pandas as pd
import ollama
import os
from config import BASE_DIR
from transformers import MarianMTModel, MarianTokenizer


def translate(file_path, request_id):
    # Percorso del file di output
    output_file_name = 'translations.csv'
    output_file_path = os.path.join(BASE_DIR, 'output', 'requests', str(request_id), output_file_name)
    # Se il file di output esiste già, carica i dati esistenti in un DataFrame
    if os.path.exists(output_file_path):
        df = pd.read_csv(output_file_path, sep='\t', quoting=csv.QUOTE_NONE)
    else:
        # Altrimenti, inizializza un DataFrame vuoto
        df = pd.DataFrame(columns=['SOURCE', 'TRANSLATION'])

    # Controlla se il file di testo esiste
    try:
        with open(file_path, 'r') as file:
            source_sentences = file.readlines()
    except FileNotFoundError:
        print("Il file di testo non esiste.")
        return

    # Inizializza una lista per le nuove traduzioni
    new_translations = []

    # Cicla attraverso le frasi di origine e le passa all'AI per la traduzione
    for sentence in source_sentences:
        # Estrai solo il testo della frase dopo la numerazione
        match = re.search(r'"([^"]+)"', sentence)
        if match:
            text = match.group(1)
            print(text)
            # Esegui la traduzione della frase utilizzando l'AI appropriato
            translated_sentence = translate_with_en_it_helsinki(text)

            # Aggiungi la coppia di frasi (originale e tradotta) alla lista delle nuove traduzioni
            new_translations.append({'SOURCE': text.strip(), 'TRANSLATION': translated_sentence.strip()})

    # Crea un nuovo DataFrame con le nuove traduzioni
    new_df = pd.DataFrame(new_translations)

    # Unisci il nuovo DataFrame con quello esistente, ignorando gli indici originali
    df = pd.concat([df, new_df], ignore_index=True)

    # Salva il DataFrame nel file di output
    df.to_csv(output_file_path, sep='\t', index=False, quoting=csv.QUOTE_NONE)


def translate_with_en_it_helsinki(text):
    model_name = "Helsinki-NLP/opus-mt-en-it"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    try:
        translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
        return tokenizer.decode(translated[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Error: {str(e)}")
        return "[ERROR_BATCH]"


def translate_with_ai(sentence):
    chat_output = []
    # Avvia la chat
    stream = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': f'Traduci in italiano questo titolo "${sentence}". '
                                              f'Restituisci come output solo la stringa tradotta, senza commenti '
                                              f'o altro output aggiuntivo. La traduzione deve essere di buon livello, '
                                              f'non essere troppo letterale se poi la frase non è leggibile nella lingua di destinazione.'
                                              f'Fai attenzione alle desinenze, se il soggetto è plurale anche i relativi aggettivi devono esserlo, così '
                                              f'come se il soggetto è maschile, anche gli aggettivi e i participi devono esserlo.'}],
        stream=True
    )

    # Itera attraverso i messaggi e accumula l'output nella lista
    for chunk in stream:
        chat_output.append(chunk['message']['content'])

    # Concatena tutti i messaggi nella lista in una singola stringa
    chat_output_str = ''.join(chat_output)
    return chat_output_str.strip('"')
