from locust import HttpUser, TaskSet, task, between
import os
import glob
import random

class EnqueueOnlyTasks(TaskSet):
    def on_start(self):
        # Locate test images
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.image_dir = os.path.join(base_dir, "samples")

        image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp"]
        self.image_files = []

        for ext in image_extensions:
            self.image_files.extend(glob.glob(os.path.join(self.image_dir, ext)))
            self.image_files.extend(glob.glob(os.path.join(self.image_dir, ext.upper())))

        if not self.image_files:
            print(f"⚠️  No image files found in {self.image_dir}")
        else:
            print(f"✅ Found {len(self.image_files)} images for enqueue test")

    @task
    def enqueue_only(self):
        """Send image(s) to /process without polling results"""
        if not self.image_files:
            return

        # choose 1–3 random images
        num_images = min(random.randint(1, 3), len(self.image_files))
        selected = random.sample(self.image_files, num_images)

        files = []
        for image_path in selected:
            with open(image_path, "rb") as f:
                files.append((
                    "image",
                    (os.path.basename(image_path), f.read(), "image/jpeg")
                ))

        data = {
            "source_lang": "ja",
            "target_lang": "en"
        }

        # Only measure enqueue response time
        with self.client.post("/process", files=files, data=data, catch_response=True) as resp:
            if resp.status_code != 202:
                resp.failure(f"Unexpected status {resp.status_code}")
            else:
                resp.success()  # don't parse JSON, discard body

class WebsiteUser(HttpUser):
    tasks = [EnqueueOnlyTasks]
    wait_time = between(0.1, 1)  # small random think time
