import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings("ignore",category=InsecureRequestWarning)
from typing import Dict, Any, Optional

API_URL = "https://bilibili-dideng.github.io/API/info.json"

class DidengAPI:
    def __init__(self, base_url: str = "", headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def get(self,url):
        return requests.get(url)

    def post(self,url):
        return requests.post(url)

    def close(self):
        self.session.close()

    def get_info(self):
        return requests.get(API_URL, verify=False).json()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()