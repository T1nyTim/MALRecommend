from pathlib import Path

import yaml

TOP_DIR = Path(__file__).resolve().parent
config_file = TOP_DIR.joinpath('config.yaml')


def save_config():
    with open(config_file, 'w', encoding='UTF-8') as yaml_file:
        yaml.safe_dump(CONFIG, yaml_file)


if config_file.exists():
    with open(config_file, 'r', encoding='UTF-8') as yaml_file:
        CONFIG = yaml.safe_load(yaml_file) or {
            'Client ID': None,
            'Access Token': None,
            'Refresh Token': None
        }
else:
    config_file.touch()
    CONFIG = {
        'Client ID': None,
        'Access Token': None,
        'Refresh Token': None
    }
save_config()