from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    # Wait time between tasks for a single user (1 to 5 seconds)
    wait_time = between(1, 5)

    @task(3)
    def index_page(self):
        self.client.get("/")

    @task(1)
    def login_page(self):
        self.client.get("/login/")
        
    @task(2)
    def about_page(self):
        self.client.get("/about/")
