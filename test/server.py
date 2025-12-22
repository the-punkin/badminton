#что-то новое
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import uuid
import os
import shutil


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # Важно!
)


VIDEO_DIR = "video"
PROCESSED_DIR = "processed"


os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


JOBS = {}  # job_id → {status, output_path}



def convert_video_to_bw(job_id: str, input_path: str, output_path: str):
    try:
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print("ERROR: Cannot open video")
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = "Cannot open video file"
            return
       
        fourcc = cv2.VideoWriter_fourcc('H','2','6','4')
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            print("WARNING: FPS = 0, using fallback")
            fps = 25
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print("Video size:", w, h, "fps:", fps)


        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h), isColor=False)


        frame_count = 0


        while True:
            ret, frame = cap.read()
            if not ret:
                break


            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            out.write(gray)
           


            frame_count += 1
            if frame_count % 30 == 0:
                print(f"Processed {frame_count} frames...")


        cap.release()
        out.release()


        print("Finished processing:", job_id)
        JOBS[job_id]["status"] = "done"


    except Exception as e:
        print("EXCEPTION in job:", job_id, e)
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)



@app.post("/upload")
async def upload_video(background: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())


    input_path = os.path.join(VIDEO_DIR, job_id + "_" + file.filename)
    output_path = os.path.join(PROCESSED_DIR, job_id + "_bw.mp4")


    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


    JOBS[job_id] = {"status": "processing", "output": output_path}
    print("JOBS:", JOBS)



    background.add_task(convert_video_to_bw, job_id, input_path, output_path)
    print("UPLOAD CALLED")
    print("FILENAME:", file.filename)
    print("JOB CREATED:", job_id)
    return {"job_id": job_id}



@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = JOBS.get(job_id)
    if job is None:
        return JSONResponse({"error": "job not found"}, status_code=404)
    return job



@app.get("/video/{job_id}")
def get_processed_video(job_id: str):
    job = JOBS.get(job_id)
    if not job or job["status"] != "done":
        return JSONResponse({"error": "not ready"}, status_code=400)


    return FileResponse(job["output"], media_type="video/mp4")