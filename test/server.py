from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import uuid
import os
import shutil
import subprocess
import cv2
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

VIDEO_DIR = os.path.join(ROOT_DIR, "video")
PROCESSED_DIR = os.path.join(ROOT_DIR, "processed")
FFMPEG_PATH = shutil.which("ffmpeg")

if FFMPEG_PATH is None:
    raise RuntimeError("FFmpeg not found. Please install ffmpeg.")


os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

JOBS = {}

# Загружаем YOLO один раз
model = YOLO("yolov8n-pose.pt")


def process_video(job_id: str, input_path: str, output_path: str):
    try:
        temp_output = os.path.join(PROCESSED_DIR, f"{job_id}_temp.mp4")

        cap = cv2.VideoCapture(input_path)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(temp_output, fourcc, 30.0,
                              (int(cap.get(3)), int(cap.get(4))))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame, verbose=False)
            annotated = results[0].plot()

            out.write(annotated)

        cap.release()
        out.release()

        # Конвертация через локальный ffmpeg
        cmd = [
            FFMPEG_PATH,
            "-y",
            "-loglevel", "error",
            "-i", temp_output,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_path
        ]

        subprocess.run(cmd, check=True)

        os.remove(temp_output)

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
        "status": "processing",
        "output": output_path
    }

    background.add_task(process_video, job_id, input_path, output_path)

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