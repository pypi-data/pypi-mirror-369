import requests

ENDPOINT = "https://tikolu.net/i/"

class TikoluUploader:
    def __init__(self, endpoint: str = ENDPOINT):
        self.endpoint = endpoint

    def upload(self, filepath: str) -> dict:
        with open(filepath, 'rb') as f:
            files = {
                "upload": (None, "true"),
                "file": (filepath, f, "image/png")
            }
            r = requests.post(self.endpoint, files=files)
        r.raise_for_status()
        return r.json()
