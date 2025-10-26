from locust import HttpUser, task, between
import random
import string
import uuid
from pathlib import Path

API_BASE = "http://localhost:8000/api"
VIDEO_FILE = Path(__file__).parent / "flex_mini.mp4"


def random_email():
    return f"user_".join(random.choices(string.ascii_letters + string.digits, k=3)) + "@test.com"

def random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))


class VideoPlatformUser(HttpUser):
    wait_time = between(1, 3)  # pausa entre tareas

    def on_start(self):
        self.email = random_email()
        self.password = random_password()
        self.token = None

        signup_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
            "city": "Bogota",
            "country": "Colombia"
        }
        with self.client.post(f"{API_BASE}/auth/signup", json=signup_data, catch_response=True) as res:
            if res.status_code not in [200, 201]:
                res.failure(f"Signup failed: {res.text}")
                return
            
        login_data = {"email": self.email, "password": self.password}
        with self.client.post(f"{API_BASE}/auth/login", json=login_data, catch_response=True) as res:
            if res.status_code == 200:
                self.token = res.json()["access_token"]
            else:
                res.failure(f"Login failed: {res.text}")


    @task(3)
    def list_public_videos(self):
        self.client.get(f"{API_BASE}/public/videos", name="/videos")

    @task(2)
    def get_rankings(self):
        self.client.get(f"{API_BASE}/public/rankings", name="/rankings")

    #Simulación de publicación de videos y votacion 
    @task(1)
    def upload_and_publish_video(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        files = {"video_file": ("test.mp4", open(VIDEO_FILE, "rb"), "video/mp4")}
        data = {"title": f"Test video {uuid.uuid4().hex[:6]}"}
        with self.client.post(
            f"{API_BASE}/videos/upload",
            headers=headers,
            files=files,
            data=data,
            name="/videos/upload",
            catch_response=True
        ) as res:
            if res.status_code not in [200, 201]:
                res.failure(f"Upload failed: {res.text}")
                return

            video_id = res.json().get("task_id")

        if video_id:
            self.client.put(
                f"{API_BASE}/videos/{video_id}/publish",
                headers=headers,
                name="/videos/publish"
            )

        if video_id:
             self.client.post(
                f"{API_BASE}/public/videos/{video_id}/vote",
                headers=headers,
                name="/videos/vote"
            )
        
        if video_id:
            self.client.get(f"{API_BASE}/videos", name="/videos", headers=headers)





  