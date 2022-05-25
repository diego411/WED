import requests
import os

CONFIG_SERVICE_URL = os.environ.get("CONFIG_SERVER_URL")


def pull_config():
    try:
        response = requests.get(CONFIG_SERVICE_URL + "api/v1/channels")
        if response.ok:
            print("Sucessfully pulled config from config service")
            return response.json()
    except:
        print("Failed to pull config from config service")
        return None
