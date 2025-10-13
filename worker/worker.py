import numpy as np
import cv2
import json
import base64
import logging

from shared.redis_client import redis_client
import asyncio

from dotenv import load_dotenv
load_dotenv()

from process.text_extraction import MangaTextExtractor
from process.translator import MangaTranslator
from process.text_render import MangaTextRenderer
from process.inpaint import Inpainter
from process.test import process_image

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """
    The main function for the ML worker. It loads models once and then enters
    an infinite loop to process jobs from the Redis queue.
    """
    logger.info("Initializing ML components...")
    text_extractor = MangaTextExtractor()
    translator = MangaTranslator()
    renderer = MangaTextRenderer(font_path="fonts/Anime.otf")
    inpainter = Inpainter()
    logger.info("Initialization complete. Worker is ready.")
    
    logger.info("Waiting for jobs in 'job_queue'...")

    while True:
        try:
            _ , job_json = redis_client.blpop("job_queue", 0)
            job = json.loads(job_json)
            logger.info(f"Dequeued job for source_lang='{job['source_lang']}'")
            image_bytes = base64.b64decode(job['image_b64'])
            npimg = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
            
            result = await process_image(
                image,
                text_extractor=text_extractor,
                translator=translator,
                renderer=renderer,
                inpainter=inpainter,
                source_lang=job['source_lang'],
                target_lang=job['target_lang']
            )
            
            # Store result in Redis using job_id
            redis_client.set(f"job_result:{job['job_id']}", json.dumps(result))
            logger.info(f"Job {job['job_id']} processing complete.")
        except Exception as e:
            logger.error(f"ERROR processing job: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
