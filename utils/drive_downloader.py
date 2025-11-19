import requests

def download_drive_to_bytes(url):
    r = requests.get(url)
    return r.content
