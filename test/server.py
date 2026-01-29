from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import shutil
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VIDEO_DIR = "video"
PROCESSED_DIR = "processed"

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

JOBS = {}  # job_id -> status


def convert_video_to_bw(job_id: str, input_path: str, output_path: str):
    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-loglevel", "error",
            "-i", input_path,
            "-vf", "format=gray",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_path
        ]

        subprocess.run(cmd, check=True)

        JOBS[job_id]["status"] = "done"

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)


@app.post("/upload")
async def upload_video(background: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    input_path = os.path.join(VIDEO_DIR, f"{job_id}_{file.filename}")
    output_path = os.path.join(PROCESSED_DIR, f"{job_id}_bw.mp4")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    JOBS[job_id] = {
        "status": "processing",
        "output": output_path
    }

    background.add_task(convert_video_to_bw, job_id, input_path, output_path)

    return {"job_id": job_id}


@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({"error": "not found"}, status_code=404)
    return job


@app.get("/video/{job_id}")
def get_video(job_id: str):
    job = JOBS.get(job_id)
    if not job or job["status"] != "done":
        return JSONResponse({"error": "not ready"}, status_code=400)

    return FileResponse(job["output"], media_type="video/mp4")
