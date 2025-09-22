from locust import HttpUser, task, between

class SimpleUser(HttpUser):
    wait_time = between(1, 3)  # wait time between requests
    host = "http://34.110.146.65"  # replace with your target if needed

    @task
    def hit_test_endpoint(self):
        self.client.get("/test")
