from locust import HttpUser, task
from uuid import uuid4

class TestWebhook(HttpUser):
    @task
    def create_user(self):
        email = f"{uuid4()}@gmail.com"
        self.client.post("/api/v1/user/register", json={
            "email" : email,
            "password" :"F@123asjddhas@#$%A"
        })
