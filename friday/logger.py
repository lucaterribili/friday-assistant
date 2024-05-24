import logging
import logging.config
import os
import yaml
from config import BASE_DIR


def setup_logging():
    log_folder = os.path.join(BASE_DIR, 'logs')
    os.makedirs(log_folder, exist_ok=True)

    config_file = os.path.join(BASE_DIR, 'logging_config.yaml')
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f.read())
        config['handlers']['info_file']['filename'] = os.path.join(log_folder, 'info.log')
        config['handlers']['error_file']['filename'] = os.path.join(log_folder, 'error.log')
        logging.config.dictConfig(config)
