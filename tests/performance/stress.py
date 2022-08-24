
import time
from locust import HttpUser, task, between


class TestWebhook(HttpUser):

    @task
    def send_webhook(self):
        self.client.post("/api/v1/webhook/instagram", json={
            "object": "instagram",
            "entry": [
                {
                    "time": 1660389485931,
                    "id": "17841449720273509",
                    "messaging": [
                        {
                            "sender": {
                                "id": "5638341022851855"
                            },
                            "recipient": {
                                "id": "17841449720273509"
                            },
                            "timestamp": 1660389485469,
                            "message": {
                                "mid": "aWdfZAG1faXRlbToxOklHTWVzc2FnZAUlEOjE3ODQxNDQ5NzIwMjczNTA5OjM0MDI4MjM2Njg0MTcxMDMwMDk0OTEyODE2NzY0MzU5Mjg5MDM5NzozMDYyODc3OTkwMTEzMjI1MDc3NTIzODIwMDE1OTg5NTU1MgZDZD",
                                "text": "Helloo babe"
                            }
                        }
                    ]
                }
            ]
        }



        )
