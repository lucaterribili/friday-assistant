from config import BACKOFFICE_URL
import requests
import os
import json


def send_communication(request_id, current_status, transaction):
    url = BACKOFFICE_URL + '/api/response/handShake'
    payload = {'request_id': request_id, 'request_current_status': current_status, 'request_transaction': transaction}
    response = requests.post(url, json=payload)

    # Controlla lo stato della risposta
    if response.status_code == 200:
        print(f'Request {request_id} processed and POST request sent successfully')
    else:
        print(f'Failed to send POST request for request {request_id}. Status code: {response.status_code}')


def write_status_to_file(folder_path, request_type):
    status = {"request_type": request_type}
    with open(os.path.join(folder_path, "status.json"), "w") as json_file:
        json.dump(status, json_file)
