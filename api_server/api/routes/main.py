from quart import Blueprint, request, jsonify
import base64
import json
import logging
import uuid

from shared.redis_client import redis_client

logger = logging.getLogger(__name__)
test_bp = Blueprint('test', __name__)

@test_bp.route('/test')
def test():
    return jsonify(message="API Server is running!")

@test_bp.route('/process', methods=['POST'])
async def process_endpoint():
    files = (await request.files).getlist('image')
    if not files:
        return jsonify({"error": "No image file provided"}), 400
        
    form = await request.form
    source_lang = form.get("source_lang", "ja")
    target_lang = form.get("target_lang", "en")

    jobs = []
    for file in files:
        image_bytes = file.read()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        job_id = str(uuid.uuid4())
        job = {
            "job_id": job_id,
            "image_b64": image_b64,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        job_json = json.dumps(job)
        redis_client.lpush("job_queue", job_json)
        jobs.append(job_id)

    logger.info(f"Queued {len(jobs)} translation job(s).")
    return jsonify({
        "status": "accepted",
        "job_ids": jobs,
        "message": f"Translation job has been queued for {len(jobs)} image(s)."
    }), 202

# Async Redis client
# redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)

# @test_bp.route("/process", methods=["POST"])
# async def process_endpoint():
#     files = (await request.files).getlist("image")
#     if not files:
#         return jsonify({"error": "No image file provided"}), 400

#     form = await request.form
#     source_lang = form.get("source_lang", "ja")
#     target_lang = form.get("target_lang", "en")

#     jobs = []
#     for file in files:
#         job_id = str(uuid.uuid4())

#         job = {
#             "job_id": job_id,
#             "filename": file.filename,
#             "source_lang": source_lang,
#             "target_lang": target_lang,
#         }
#         job_json = json.dumps(job)

#         # Async LPUSH 
#         await redis_client.lpush("job_queue", job_json)

#         jobs.append(job_id)

#     logger.info(f"Queued {len(jobs)} translation job(s).")
#     return (
#         jsonify(
#             {
#                 "status": "accepted",
#                 "job_ids": jobs,
#                 "message": f"Queued {len(jobs)} image(s) (non-blocking test).",
#             }
#         ),
#         202,
#     )

@test_bp.route('/result/<job_id>', methods=['GET'])
async def get_result(job_id):
    result_json = redis_client.get(f"job_result:{job_id}")
    if not result_json:
        return jsonify({"status": "pending", "message": "Result not ready"}), 202
    result = json.loads(result_json)
    
    logger.info("Completed Job")
    return jsonify({"status": "done", "result": result}), 200