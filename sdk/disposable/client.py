import requests
import time
import os

DEFAULT_API_URL = os.getenv("DISPOSABLE_API_URL", "http://localhost:8000")
DEFAULT_TOKEN = os.getenv("DISPOSABLE_API_KEY", None)


class DisposableClient:

    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or DEFAULT_TOKEN
        self.base_url = base_url or DEFAULT_API_URL

        self.run_url = f"{self.base_url}/run"
        self.result_url = f"{self.base_url}/result/"

        if not self.api_key:
            raise Exception("API key required")

    def run(self, script, poll_interval=1):

        r = requests.post(
            self.run_url,
            json={"script": script},
            headers={"x-token": self.api_key},
            timeout=30
        )

        data = r.json()

        if "status" not in data:
            return data

        if data["status"] != "queued":
            return data

        job_id = data["job_id"]

        while True:

            r = requests.get(
                self.result_url + job_id,
                headers={"x-token": self.api_key},
                timeout=30
            )

            result = r.json()

            if result["status"] != "running":
                return result

            time.sleep(poll_interval)


def run(script, api_key=None, base_url=None):
    client = DisposableClient(api_key=api_key, base_url=base_url)
    return client.run(script)
