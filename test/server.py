from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from ultralytics import YOLO
import cv2
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
FRAMES_DIR = "frames"
PROCESSED_DIR = "processed"

for d in [VIDEO_DIR, FRAMES_DIR, PROCESSED_DIR]:
    os.makedirs(d, exist_ok=True)


model = YOLO("yolov8n-pose.pt")

JOBS = {}  # job_id -> status, output

def process_video_yolo(job_id: str, input_path: str, output_path: str):
    try:
        JOBS[job_id]["status"] = "processing"

        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise RuntimeError("Cannot open video")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25

        frame_dir = os.path.join(FRAMES_DIR, job_id)
        os.makedirs(frame_dir, exist_ok=True)

        idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame, verbose=False)
            annotated = results[0].plot()

            frame_path = os.path.join(frame_dir, f"{idx:05d}.png")
            cv2.imwrite(frame_path, annotated)
            idx += 1

        cap.release()

        cmd = [
            "ffmpeg",
            "-y",
            "-loglevel", "error",
            "-framerate", str(int(fps)),
            "-i", f"{frame_dir}/%05d.png",
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
    output_path = os.path.join(PROCESSED_DIR, f"{job_id}_pose.mp4")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    JOBS[job_id] = {
        "status": "queued",
        "output": output_path
    }

    background.add_task(process_video_yolo, job_id, input_path, output_path)

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
