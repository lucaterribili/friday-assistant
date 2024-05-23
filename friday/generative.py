import ollama
import os
import time
from config import BASE_DIR
from friday.text_helper import translate
from friday.comunicator import send_communication, write_status_to_file
import logging


def setup_logging():
    log_folder = os.path.join(BASE_DIR, 'logs')
    os.makedirs(log_folder, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Livello generale del logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Livello di log per la console
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    file_handler = logging.FileHandler(os.path.join(log_folder, 'translations.log'))
    file_handler.setLevel(logging.ERROR)  # Livello di log per il file
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


# SEND RESPONSE
def save_multiple_translations(request_id, titles):
    setup_logging()
    output_folder = os.path.join(BASE_DIR, 'output', 'requests', str(request_id))
    os.makedirs(output_folder, exist_ok=True)
    try:
        for idx, title in enumerate(titles):
            time.sleep(60)
            generator_sentences(title, 20, request_id)
        send_communication(request_id, 'running', 'to_executed')
        write_status_to_file(output_folder, "translations")
    except Exception as e:
        print(f"Errore durante la generazione delle traduzioni: {str(e)}")
        logging.error(f"Errore durante la generazione delle traduzioni: {str(e)}")
        send_communication(request_id, 'running', 'to_failed')


# SEND RESPONSE
def save_multiple_articles(request_id, titles):
    setup_logging()
    output_folder = os.path.join(BASE_DIR, 'output', 'requests', str(request_id))
    os.makedirs(output_folder, exist_ok=True)
    try:
        for idx, title in enumerate(titles):
            time.sleep(60)
            article_content = generate_article(title)
            filename = f"article_{idx + 1}.txt"
            filepath = os.path.join(output_folder, filename)
            save_article_to_file(filepath, article_content)
        send_communication(request_id, 'running', 'to_executed')
        write_status_to_file(output_folder, "articles")
    except Exception as e:
        print(f"Errore durante la generazione o il salvataggio degli articoli: {str(e)}")
        logging.error(f"Errore durante la generazione o il salvataggio degli articoli: {str(e)}")
        send_communication(request_id, 'running', 'to_failed')


def save_article_to_file(filepath, content):
    with open(filepath, 'w') as file:
        file.write(content)


def generate_multiple_article(titles):
    articles = []
    for title in titles:
        article = generate_article(title)
        articles.append(article)
    return articles


def generate_article(title):
    chat_output = []
    stream = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': f'Scrivi un articolo su questo argomento "${title}". '
                                              f'Restituisci come output solo l\'articolo scritto senza commenti '
                                              f'o altro output aggiuntivo. Scrivi in italiano corretto e con informazioni veritiere. '
                                              f'L\'articolo deve essere lungo almeno 800 parole'}],
        stream=True
    )
    for chunk in stream:
        chat_output.append(chunk['message']['content'])
    chat_output_str = ''.join(chat_output)
    return chat_output_str


def generator_sentences(topic, number, request_id):
    cache_path = 'cache/sentences.txt'
    chat_output = []
    # Avvia la chat
    stream = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'user', 'content': f'Genera ${number} frasi in inglese riguardo questo argomento "${topic}". '
                                        f'Restituisci come output solo le frasi, senza commenti '
                                        f'o altro output aggiuntivo. Numera le righe e racchiudi le frasi tra apici ("), '
                                        f'racchiudi solo le frasi vere e proprie, non tutta la riga. La numerazione deve stare fuori gli apici.'}],
        stream=True
    )
    for chunk in stream:
        chat_output.append(chunk['message']['content'])

    # Concatena tutti i messaggi nella lista in una singola stringa
    chat_output_str = ''.join(chat_output)
    # Save cache file
    with open(cache_path, 'w') as file:
        file.write(chat_output_str)
    # WAIT
    time.sleep(2)
    # TRANSLATE
    translate(cache_path, request_id)
    # Controlla se il file esiste prima di eliminarlo
    if os.path.exists(cache_path):
        # Elimina il file
        os.remove(cache_path)
