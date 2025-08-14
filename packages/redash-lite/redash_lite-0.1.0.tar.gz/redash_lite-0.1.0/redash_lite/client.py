# client.py
import json
import time
import requests

class RedashClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json"
        })

    def _poll_job(self, job_id):
        while True:
            r = self.session.get(f"{self.base_url}/api/jobs/{job_id}")
            job = r.json()["job"]
            if job["status"] in (3, 4):  # 3 = done, 4 = failed
                return job.get("query_result_id") if job["status"] == 3 else None
            time.sleep(1)

    def get_fresh_query_result(self, query_id, params):
        payload = {"max_age": 0, "parameters": params}
        r = self.session.post(
            f"{self.base_url}/api/queries/{query_id}/results",
            data=json.dumps(payload)
        )
        job = r.json()["job"]

        result_id = self._poll_job(job["id"])
        if not result_id:
            raise Exception("Query execution failed.")

        r = self.session.get(
            f"{self.base_url}/api/queries/{query_id}/results/{result_id}.json"
        )
        return r.json()["query_result"]["data"]["rows"]
