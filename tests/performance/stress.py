
import time
from locust import HttpUser, task, between


class TestWebhook(HttpUser):

    # @task
    # def send_webhook(self):
    #     self.client.post("/api/v1/webhook/instagram", json={
    #         "object": "instagram",
    #         "entry": [
    #             {
    #                 "time": 1660389485931,
    #                 "id": "17841449720273509",
    #                 "messaging": [
    #                     {
    #                         "sender": {
    #                             "id": "5638341022851855"
    #                         },
    #                         "recipient": {
    #                             "id": "17841449720273509"
    #                         },
    #                         "timestamp": 1660389485469,
    #                         "message": {
    #                             "mid": "aWdfZAG1faXRlbToxOklHTWVzc2FnZAUlEOjE3ODQxNDQ5NzIwMjczNTA5OjM0MDI4MjM2Njg0MTcxMDMwMDk0OTEyODE2NzY0MzU5Mjg5MDM5NzozMDYyODc3OTkwMTEzMjI1MDc3NTIzODIwMDE1OTg5NTU1MgZDZD",
    #                             "text": "Helloo babe"
    #                         }
    #                     }
    #                 ]
    #             }
    #         ]
    #     }

    #     )
    @task
    def send_webhook(self):
        self.client.post("/api/v1/webhook/instagram", json={
            "object": "instagram",
            "entry": [
                {
                    "time": 1660392271172,
                    "id": "17841449720273509",
                    "messaging": [
                        {
                            "sender": {
                                "id": "5638341022851855"
                            },
                            "recipient": {
                                "id": "17841449720273509"
                            },
                            "timestamp": 1660392270877,
                            "postback": {
                                "mid": "aWdfZAG1faXRlbToxOklHTWVzc2FnZAUlEOjE3ODQxNDQ5NzIwMjczNTA5OjM0MDI4MjM2Njg0MTcxMDMwMDk0OTEyODE2NzY0MzU5Mjg5MDM5NzozMDYyODgzMTI4Mjg0ODcxODE4NTEwODcxNjU5NTk3MDA0OAZDZD",
                                "title": "Good",
                                "payload": "02624e5d-cb6b-4f37-9c5c-e938486a3ec3"
                            }
                        }
                    ]
                }
            ]
        })
