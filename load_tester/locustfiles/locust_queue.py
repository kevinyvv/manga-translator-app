from locust import HttpUser, TaskSet, task, between
import os
import random
import glob
import time
import json

class QueueTranslationTasks(TaskSet):
    def on_start(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.image_dir = os.path.join(base_dir, "raw_scans", "jjk")
        
        image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp"]
        self.image_files = []
        
        for extension in image_extensions:
            self.image_files.extend(glob.glob(os.path.join(self.image_dir, extension)))
            self.image_files.extend(glob.glob(os.path.join(self.image_dir, extension.upper())))
        
        if not self.image_files:
            print(f"Warning: No image files found in {self.image_dir}")
        else:
            print(f"Found {len(self.image_files)} images for testing (queue mode)")

    @task
    def translate_manga_via_queue(self):
        """Test sending to queue and retrieving results"""
        if not self.image_files:
            return
        
        # pick 1-3 images
        num_images = min(random.randint(1, 3), len(self.image_files))
        selected_images = random.sample(self.image_files, num_images)

        try:
            files = []
            for image_path in selected_images:
                with open(image_path, 'rb') as image_file:
                    files.append(('image', (
                        os.path.basename(image_path),
                        image_file.read(),
                        'image/jpeg'
                    )))

            data = {
                'source_lang': 'ja',
                'target_lang': 'en'
            }

            # Step 1: Send job(s) to /process
            with self.client.post("/process",
                                  files=files,
                                  data=data,
                                  catch_response=True) as response:
                if response.status_code != 202:
                    response.failure(f"Process request failed: {response.status_code}")
                    return

                job_info = response.json()
                job_ids = job_info.get("job_ids", [])
                if not job_ids:
                    response.failure("No job IDs returned")
                    return
                
            # Step 2: Poll each job until complete
            for job_id in job_ids:
                done = False
                retries = 0
                while not done and retries < 25:
                    with self.client.get(f"/result/{job_id}",
                                         catch_response=True) as result_resp:
                        if result_resp.status_code == 200:
                            result_data = result_resp.json()
                            if result_data.get("status") == "done":
                                result_resp.success()
                                done = True
                            else:
                                # still pending
                                result_resp.failure("Result still pending")
                        elif result_resp.status_code == 202:
                            # pending state
                            pass
                        else:
                            result_resp.failure(f"Unexpected status {result_resp.status_code}")
                        
                    if not done:
                        time.sleep(10)  # wait before polling again
                        retries += 1

                if not done:
                    print(f"Job {job_id} did not complete in time.")

        except Exception as e:
            print(f"Error processing (queue mode): {e}")


class MangaTranslatorQueueUser(HttpUser):
    tasks = [QueueTranslationTasks]
    wait_time = between(1000000, float('inf'))
    host = "http://34.110.146.65"

    def on_start(self):
        print("Starting queue load test user")

    def on_stop(self):
        print("Stopping queue load test user")
