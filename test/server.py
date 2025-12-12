# FastAPI server (server/main.py)
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join(VIDEO_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@app.get("/video/{filename}")
def get_video(filename: str):
    file_path = os.path.join(VIDEO_DIR, filename)
    return FileResponse(file_path, media_type="video/mp4")
