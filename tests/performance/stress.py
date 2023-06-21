from uuid import uuid4

from locust import HttpUser, task


class TestWebhook(HttpUser):
    @task
    def sign_in(self):
        res = self.client.get(
            '/api/v1/user/all',
        )
        token = res.json()["access_token"]
        self.token = token
