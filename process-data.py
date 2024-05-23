import ollama
import pandas as pd
import csv

filename = 'articles_list'

# Leggi il file CSV senza interpretare la prima riga come intestazioni
df = pd.read_csv('input/' + filename + '.csv', sep="\t", quoting=csv.QUOTE_NONE)

titles = df['TITOLO']

# Inizializza una lista vuota per memorizzare i messaggi

titles_output = []
# Cicla sui valori della colonna
for title in titles:
    chat_output = []
    # Avvia la chat
    stream = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': f'Parafrasa in italiano questo titolo "${title}". '
                                              f'Restituisci come output solo la stringa parafrasata, senza commenti '
                                              f'o altro output aggiuntivo. Se il titolo è troppo generico, restituisci il titolo originale'}],
        stream=True
    )

    # Itera attraverso i messaggi e accumula l'output nella lista
    for chunk in stream:
        chat_output.append(chunk['message']['content'])

    # Concatena tutti i messaggi nella lista in una singola stringa
    chat_output_str = ''.join(chat_output)
    titles_output.append(chat_output_str.strip('"'))
    # Restituisci l'output completo
    print(chat_output_str)

for title in titles_output:
    chat_output = []
    stream = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': f'Scrivi un articolo su questo argomento "${title}". '
                                              f'Resistiuisci come output solo l\'articolo scritto senza commenti '
                                              f'o altro output aggiuntivo. Cerca di scrivere in italiano corretto e con informazioni veritiere'}],
        stream=True
    )
    for chunk in stream:
        chat_output.append(chunk['message']['content'])

    # Concatena tutti i messaggi nella lista in una singola stringa
    chat_output_str = ''.join(chat_output)
    print(chat_output_str)
