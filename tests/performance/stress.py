from locust import HttpUser, task
from uuid import uuid4


class TestWebhook(HttpUser):
    @task
    def get_users(self):
        self.client.get(
            "/api/v1/user/all",
            headers={
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzA3NzUxNzMsImlkIjoiZjNhYmEzMjQtNDBjZS00ZWZhLWEzZjEtMWVhOTlmNTAyYTQxIiwicm9sZSI6IkFETUlOIn0.5FdpX0fdJQSAQ4xOvWvLt3PuXgBpIocBgi01Uyb4AWw"
            }
        )
