from flask import Flask
from friday.generative import save_multiple_articles, save_multiple_translations
from friday.routing import provider_response, provider_request
import threading
from queue import Queue

app = Flask(__name__)

# Coda delle richieste
request_queue = Queue()


@app.route('/request', methods=['POST'])
def handle_request():
    return provider_request(request_queue)


@app.route('/response/<request_id>', methods=['GET'])
def handle_response(request_id):
    return provider_response(request_id)


def process_requests():
    while True:
        try:
            # Ottieni una richiesta dalla coda
            request_id, task, items = request_queue.get()
            # Processa la richiesta in base al tipo di task
            if task == 'article':
                article_thread = threading.Thread(target=save_multiple_articles, args=(request_id, items))
                article_thread.start()
            elif task == 'libretranslate':
                generative_translate_thread = threading.Thread(target=save_multiple_translations,
                                                               args=(request_id, items))
                generative_translate_thread.start()
                pass
            else:
                # Task sconosciuto
                pass
        except Exception as e:
            # Gestisci qualsiasi eccezione qui
            print(f"An error occurred: {e}")


# Avvia un thread per elaborare le richieste dalla coda
processing_thread = threading.Thread(target=process_requests)
processing_thread.start()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
