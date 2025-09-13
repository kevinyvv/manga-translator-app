from locust import HttpUser, TaskSet, task, between
import os
import random
import glob

class TranslationTasks(TaskSet):
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
            print(f"Found {len(self.image_files)} images for testing")

    @task
    def translate_manga(self):
        """Test translating multiple manga images in one request"""
        if not self.image_files:
            return
            
        # 1-5 random images
        num_images = min(random.randint(1, 5), len(self.image_files))
        #selected_images = random.sample(self.image_files, num_images)
        selected_images = self.image_files[0:3]
        
        try:
            files = []
            for image_path in selected_images:
                with open(image_path, 'rb') as image_file:
                    files.append(('image', (os.path.basename(image_path), 
                                          image_file.read(), 'image/jpeg')))
            
            data = {
                'source_lang': 'ja',
                'target_lang': 'en'
            }
            
            with self.client.post("/process", 
                                      files=files, 
                                      data=data,
                                      catch_response=True) as response:
            
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Got status code {response.status_code}")
                
        except Exception as e:
            print(f"Error processing: {e}")


class MangaTranslatorUser(HttpUser):
    tasks = [TranslationTasks]
    wait_time = between(1, 5)  
    host = "http://127.0.0.1:5000"  

    def on_start(self):
        """Called when a user starts"""
        print(f"Starting load test user")

    def on_stop(self):
        """Called when a user stops"""
        print(f"Stopping load test user")