from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import uuid
import os
import shutil
import subprocess
import cv2
import numpy as np
import glob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.signal import savgol_filter
from pydantic import BaseModel

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

VIDEO_DIR      = os.path.join(ROOT_DIR, "video")
PROCESSED_DIR  = os.path.join(ROOT_DIR, "processed")
CHARTS_DIR     = os.path.join(ROOT_DIR, "charts")
FRAMES_DIR     = os.path.join(ROOT_DIR, "frames")
FFMPEG_PATH    = shutil.which("ffmpeg")

if FFMPEG_PATH is None:
    raise RuntimeError("FFmpeg not found. Please install ffmpeg.")

os.makedirs(VIDEO_DIR,     exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR,    exist_ok=True)
os.makedirs(FRAMES_DIR,    exist_ok=True)

JOBS = {}

model = YOLO("yolo11n-pose.pt")


# ──────────────────────────────────────────────────────────
# Pydantic models
# ──────────────────────────────────────────────────────────

class ROIBody(BaseModel):
    x: int
    y: int
    w: int
    h: int


# ──────────────────────────────────────────────────────────
# Job helpers
# ──────────────────────────────────────────────────────────

def _job_exists(job_id: str) -> bool:
    return job_id in JOBS

def _set_status(job_id: str, status: str):
    if _job_exists(job_id):
        JOBS[job_id]["status"] = status

def _set_progress(job_id: str, progress: float):
    if _job_exists(job_id):
        JOBS[job_id]["progress"] = round(progress, 1)

def _set_error(job_id: str, msg: str):
    if _job_exists(job_id):
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"]  = msg

def _is_cancelled(job_id: str) -> bool:
    return not _job_exists(job_id) or JOBS[job_id].get("status") == "cancelled"

def cleanup_job_files(job_id: str):
    patterns = [
        os.path.join(VIDEO_DIR,     f"{job_id}_*"),
        os.path.join(PROCESSED_DIR, f"{job_id}_*"),
        os.path.join(FRAMES_DIR,    f"{job_id}_*"),
        os.path.join(CHARTS_DIR,    f"{job_id}_*"),
    ]
    for pattern in patterns:
        for f in glob.glob(pattern):
            try:
                os.remove(f)
            except Exception as e:
                print(f"[Cleanup] {f}: {e}")


# ──────────────────────────────────────────────────────────
# Biomechanics helpers
# ──────────────────────────────────────────────────────────

def calc_angle(a, b, c) -> float:
    """Угол в точке b между лучами b→a и b→c (градусы)."""
    try:
        a = np.array(a, dtype=np.float32)
        b = np.array(b, dtype=np.float32)
        c = np.array(c, dtype=np.float32)
        ba = a - b
        bc = c - b
        cos = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        return float(np.degrees(np.arccos(np.clip(cos, -1.0, 1.0))))
    except Exception:
        return 0.0


def draw_skeleton_safe(frame, p1, p2, color, thickness=2):
    try:
        if p1 is None or p2 is None or len(p1) < 2 or len(p2) < 2:
            return
        pt1 = (int(p1[0]), int(p1[1]))
        pt2 = (int(p2[0]), int(p2[1]))
        h, w = frame.shape[:2]
        if 0 <= pt1[0] < w and 0 <= pt1[1] < h and 0 <= pt2[0] < w and 0 <= pt2[1] < h:
            cv2.line(frame, pt1, pt2, color, thickness)
    except Exception:
        pass


def smooth(arr: list, window: int = 7, poly: int = 2) -> np.ndarray:
    """
    Savitzky-Golay сглаживание.
    Если данных меньше чем окно — просто возвращаем массив без изменений.
    """
    a = np.array(arr, dtype=np.float32)
    if len(a) < window:
        return a
    # window должен быть нечётным
    w = window if window % 2 == 1 else window + 1
    w = min(w, len(a) if len(a) % 2 == 1 else len(a) - 1)
    if w < poly + 2:
        return a
    return savgol_filter(a, w, poly)


def detect_strokes(
    times:      list,
    velocities: list,
    angles:     list,
    heights:    list,
    fps:        float,
) -> list[dict]:
    """
    Детектирует удары в бадминтоне по трём одновременным признакам:

      1. Локальный максимум сглаженной скорости запястья
         выше порога  vel_mean + 1.5 * vel_std
      2. В окне ±window_frames от пика скорости угол локтя
         падает ниже  angle_mean - 0.8 * angle_std  (рука выпрямляется)
      3. В том же окне высота запястья (Y) достигает минимума
         ниже  height_mean - 0.5 * height_std  (рука поднята высоко)

    Возвращает список словарей с временем и характеристиками каждого удара.
    """
    if len(times) < 10:
        return []

    t        = np.array(times,      dtype=np.float32)
    vel_raw  = np.array(velocities, dtype=np.float32)
    ang_raw  = np.array(angles,     dtype=np.float32)
    hei_raw  = np.array(heights,    dtype=np.float32)

    # ── Сглаживаем все три сигнала ──────────────────────
    vel = smooth(vel_raw.tolist(),  window=7)
    ang = smooth(ang_raw.tolist(),  window=7)
    hei = smooth(hei_raw.tolist(),  window=7)

    # ── Пороги ──────────────────────────────────────────
    vel_thresh = vel.mean() + 1.5 * vel.std()       # пик скорости
    ang_thresh = ang.mean() - 0.8 * ang.std()       # рука выпрямлена
    hei_thresh = hei.mean() - 0.5 * hei.std()       # рука поднята (Y мал)

    # Минимальный интервал между ударами (секунды → кадры)
    min_gap = int(fps * 0.4)
    # Ширина окна поиска вокруг пика скорости
    window_frames = max(3, int(fps * 0.15))

    strokes   = []
    last_peak = -min_gap - 1

    for i in range(1, len(vel) - 1):
        # Условие 1: локальный максимум скорости выше порога
        if not (vel[i] > vel_thresh and vel[i] >= vel[i-1] and vel[i] >= vel[i+1]):
            continue
        # Условие: минимальная дистанция между ударами
        if i - last_peak < min_gap:
            continue

        lo = max(0, i - window_frames)
        hi = min(len(vel) - 1, i + window_frames)

        # Условие 2: угол локтя падает (рука выпрямляется)
        ang_in_window = ang[lo:hi+1]
        if ang_in_window.min() >= ang_thresh:
            continue

        # Условие 3: рука поднята (Y-координата запястья мала)
        hei_in_window = hei[lo:hi+1]
        if hei_in_window.min() >= hei_thresh:
            continue

        # ── Удар подтверждён ────────────────────────────
        last_peak = i
        stroke_time = float(t[i])

        # Характеристики удара
        ang_at_stroke = float(ang[i])
        hei_at_stroke = float(hei[i])
        vel_at_stroke = float(vel[i])

        # Амплитуда изменения угла локтя до/после удара
        pre_ang  = float(ang[max(0, i - window_frames)])
        post_ang = float(ang[min(len(ang)-1, i + window_frames)])
        angle_delta = round(abs(pre_ang - post_ang), 1)

        strokes.append({
            "time":         round(stroke_time, 3),
            "frame_idx":    int(i),
            "velocity":     round(vel_at_stroke, 1),
            "elbow_angle":  round(ang_at_stroke, 1),
            "wrist_height": round(hei_at_stroke, 1),
            "angle_delta":  angle_delta,     # изменение угла локтя (размах)
        })

    return strokes


# ──────────────────────────────────────────────────────────
# Chart generation
# ──────────────────────────────────────────────────────────

def generate_charts(
    job_id:     str,
    times:      list,
    angles:     list,
    heights:    list,
    velocities: list,
    strokes:    list,
) -> str | None:
    if not times:
        return None

    t   = np.array(times,      dtype=np.float32)
    vel = smooth(velocities,   window=7)
    ang = smooth(angles,       window=7)
    hei = smooth(heights,      window=7)

    stroke_times = [s["time"] for s in strokes]

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.patch.set_facecolor("#f8f8fc")

    styles = [
        ("Скорость запястья (px/s)",        vel, "#5c6ef8", "#ededfc"),
        ("Высота запястья (Y, px, ↑=выше)", hei, "#9b8ef8", "#f3f0ff"),
        ("Угол локтя (°)",                  ang, "#3dd68c", "#e8faf0"),
    ]

    for ax, (title, data, color, bg) in zip(axes, styles):
        ax.set_facecolor(bg)
        ax.plot(t, data, color=color, linewidth=1.8, zorder=3)
        ax.fill_between(t, data, data.min(), alpha=0.15, color=color, zorder=2)

        # Отмечаем удары вертикальными линиями
        for st in stroke_times:
            ax.axvline(x=st, color="#f04a6e", linewidth=1.5,
                       linestyle="--", alpha=0.8, zorder=4)

        ax.set_ylabel(title, fontsize=9, color="#444")
        ax.grid(True, alpha=0.3, color="#ccc")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8)

    # Легенда
    stroke_patch = mpatches.Patch(color="#f04a6e", label=f"Удар ({len(strokes)} шт.)")
    axes[0].legend(handles=[stroke_patch], fontsize=8, loc="upper right")

    axes[2].set_xlabel("Время (с)", fontsize=9)

    fig.suptitle(
        f"Биомеханический анализ удара · {len(strokes)} удара(ов) обнаружено",
        fontsize=13, fontweight="bold", color="#1a1a2e", y=1.01,
    )
    plt.tight_layout()

    chart_path = os.path.join(CHARTS_DIR, f"{job_id}_charts.png")
    fig.savefig(chart_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return chart_path


# ──────────────────────────────────────────────────────────
# Main processing task
# ──────────────────────────────────────────────────────────

def process_video_task(job_id: str, input_path: str, output_path: str):
    temp_output = None
    try:
        if not _job_exists(job_id):
            return

        roi = JOBS[job_id].get("roi")
        if not roi:
            _set_error(job_id, "ROI not set")
            return

        rx, ry, rw, rh = roi["x"], roi["y"], roi["w"], roi["h"]

        cap = cv2.VideoCapture(input_path)
        fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        temp_output = os.path.join(PROCESSED_DIR, f"{job_id}_temp.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out    = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))

        # Сырые данные (несглаженные — сглаживаем потом)
        times_raw:      list[float] = []
        angles_raw:     list[float] = []
        heights_raw:    list[float] = []
        velocities_raw: list[float] = []

        frame_idx  = 0
        prev_wrist = None
        prev_time  = 0.0

        # ── Буфер для сглаживания скорости на лету (rolling avg) ──
        vel_buf: list[float] = []
        VEL_BUF = 5   # сколько кадров усредняем для отображения на видео

        print(f"[{job_id}] Старт. ROI: {rx},{ry} {rw}×{rh}  fps={fps:.1f}")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if _is_cancelled(job_id):
                print(f"[{job_id}] Отменено.")
                break

            current_time = frame_idx / fps

            # ── Клип ROI с проверкой границ ──────────────────
            y1 = max(ry, 0);          y2 = min(ry + rh, frame.shape[0])
            x1 = max(rx, 0);          x2 = min(rx + rw, frame.shape[1])
            roi_frame = frame[y1:y2, x1:x2]

            angle    = 0.0
            velocity = 0.0
            wrist_g  = elbow_g = shoulder_g = None

            if roi_frame.size > 0:
                try:
                    results = model(roi_frame, verbose=False, conf=0.3)
                except Exception:
                    results = []

                if results and results[0].keypoints is not None:
                    kps = results[0].keypoints.xy.cpu().numpy()
                    if len(kps) > 0 and len(kps[0]) > 12:
                        kp = kps[0]
                        if not np.any(np.isnan(kp)):
                            # Глобальные координаты
                            g = kp.copy()
                            g[:, 0] += x1
                            g[:, 1] += y1

                            sh, el, wr = g[6], g[8], g[10]   # COCO right arm

                            if not any(np.any(np.isnan(p)) for p in (sh, el, wr)):
                                angle    = calc_angle(sh, el, wr)
                                wrist_g  = wr
                                elbow_g  = el
                                shoulder_g = sh

                                # ── Скорость: евклидово расстояние / dt ──
                                if prev_wrist is not None:
                                    dt = current_time - prev_time
                                    if dt > 0:
                                        velocity = float(
                                            np.linalg.norm(wr - prev_wrist) / dt
                                        )
                                    # else velocity = 0 (первый кадр)
                                prev_wrist = wr
                                prev_time  = current_time

                                # Скользящее среднее скорости (уменьшает шум на лету)
                                vel_buf.append(velocity)
                                if len(vel_buf) > VEL_BUF:
                                    vel_buf.pop(0)
                                velocity_display = float(np.mean(vel_buf))

                                times_raw.append(current_time)
                                angles_raw.append(angle)
                                heights_raw.append(float(wr[1]))   # Y пикселей
                                velocities_raw.append(velocity)    # сырая скорость

            # ── Отрисовка ─────────────────────────────────────
            annotated = frame.copy()

            # ROI рамка
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 255), 2)

            if wrist_g is not None:
                # Скелет
                draw_skeleton_safe(annotated, shoulder_g, elbow_g, (0, 255, 0), 3)
                draw_skeleton_safe(annotated, elbow_g,    wrist_g,  (0, 255, 0), 3)

                # Суставы
                for pt, col in [
                    (shoulder_g, (255, 80,  80)),
                    (elbow_g,    (80,  255, 255)),
                    (wrist_g,    (80,  80,  255)),
                ]:
                    try:
                        cv2.circle(annotated,
                                   (int(pt[0]), int(pt[1])), 6, col, -1)
                    except Exception:
                        pass

                # Угол у локтя
                try:
                    ex, ey = int(elbow_g[0]), int(elbow_g[1])
                    cv2.putText(annotated, f"{int(angle)}°",
                                (ex - 30, ey - 14),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                                (0, 255, 100), 2)
                except Exception:
                    pass

            # HUD (полупрозрачный фон)
            overlay = annotated.copy()
            cv2.rectangle(overlay, (0, 0), (310, 130), (0, 0, 0), -1)
            annotated = cv2.addWeighted(annotated, 1.0, overlay, 0.55, 0)

            vel_disp = velocity_display if wrist_g is not None else 0.0
            hei_disp = wrist_g[1] if wrist_g is not None else 0.0

            for i, (label, value, col) in enumerate([
                (f"Frame {frame_idx}/{total_frames}",           "",           (220, 220, 220)),
                (f"Time  {current_time:.2f}s",                  "",           (220, 220, 220)),
                (f"Speed {vel_disp:.0f} px/s",                  "",           (255, 230,  80)),
                (f"Wrist Y {hei_disp:.0f} px",                  "",           (255, 230,  80)),
                (f"Elbow  {angle:.0f} deg",                     "",           (80,  255, 180)),
            ]):
                cv2.putText(annotated, label,
                            (10, 22 + i * 22),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.58, col, 1)

            out.write(annotated)
            frame_idx += 1

            # Прогресс каждые 10 кадров
            if frame_idx % 10 == 0:
                _set_progress(job_id, frame_idx / total_frames * 90)

        cap.release()
        out.release()

        if _is_cancelled(job_id):
            if temp_output and os.path.exists(temp_output):
                os.remove(temp_output)
            return

        # ── ffmpeg re-encode ──────────────────────────────────
        cmd = [
            FFMPEG_PATH, "-y", "-loglevel", "error",
            "-i", temp_output,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            output_path,
        ]
        subprocess.run(cmd, check=True)
        if os.path.exists(temp_output):
            os.remove(temp_output)

        _set_progress(job_id, 95)

        # ── Детекция ударов ───────────────────────────────────
        strokes = detect_strokes(
            times_raw, velocities_raw, angles_raw, heights_raw, fps
        )

        # ── Графики ───────────────────────────────────────────
        chart_path = generate_charts(
            job_id,
            times_raw, angles_raw, heights_raw, velocities_raw,
            strokes,
        )

        # ── Сводные метрики ───────────────────────────────────
        ang_arr = np.array(angles_raw,     dtype=np.float32)
        vel_arr = np.array(velocities_raw, dtype=np.float32)

        metrics = {
            # Общее
            "total_frames":     frame_idx,
            "processed_points": len(times_raw),
            "duration_sec":     round(times_raw[-1], 2) if times_raw else 0,

            # Угол локтя (исправлено: avg — реальное среднее, range — диапазон)
            "avg_angle":        round(float(ang_arr.mean()), 1)  if len(ang_arr) else 0,
            "min_angle":        round(float(ang_arr.min()),  1)  if len(ang_arr) else 0,
            "max_angle":        round(float(ang_arr.max()),  1)  if len(ang_arr) else 0,
            "angle_range":      round(float(ang_arr.max() - ang_arr.min()), 1) if len(ang_arr) else 0,

            # Скорость
            "avg_velocity":     round(float(vel_arr.mean()), 1)  if len(vel_arr) else 0,
            "max_velocity":     round(float(vel_arr.max()),  1)  if len(vel_arr) else 0,

            # Удары
            "stroke_count":     len(strokes),
            "strokes":          strokes,
        }

        if _job_exists(job_id):
            JOBS[job_id]["metrics"]    = metrics
            JOBS[job_id]["chart_path"] = chart_path
            _set_status(job_id, "done")
            _set_progress(job_id, 100)

        print(f"[{job_id}] Готово. Кадров: {frame_idx}, ударов: {len(strokes)}")

    except Exception as e:
        import traceback
        print(f"[{job_id}] Ошибка: {e}\n{traceback.format_exc()}")
        _set_error(job_id, str(e))
        if temp_output and os.path.exists(temp_output):
            try:
                os.remove(temp_output)
            except Exception:
                pass


# ──────────────────────────────────────────────────────────
# API endpoints
# ──────────────────────────────────────────────────────────

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    job_id     = str(uuid.uuid4())
    input_path = os.path.join(VIDEO_DIR, f"{job_id}_{file.filename}")

    with open(input_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    JOBS[job_id] = {
        "status":   "uploaded",
        "input":    input_path,
        "output":   os.path.join(PROCESSED_DIR, f"{job_id}_pose.mp4"),
        "roi":      None,
        "progress": 0,
        "metrics":  {},
    }
    return {"job_id": job_id}


@app.get("/first_frame/{job_id}")
def get_first_frame(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({"error": "not found"}, status_code=404)

    frame_path = os.path.join(FRAMES_DIR, f"{job_id}_first_frame.png")
    if not os.path.exists(frame_path):
        cap = cv2.VideoCapture(job["input"])
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return JSONResponse({"error": "cannot read frame"}, status_code=500)
        cv2.imwrite(frame_path, frame)

    return FileResponse(frame_path, media_type="image/png")


@app.post("/roi/{job_id}")
def set_roi(job_id: str, body: ROIBody):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({"error": "not found"}, status_code=404)
    job["roi"]    = {"x": body.x, "y": body.y, "w": body.w, "h": body.h}
    job["status"] = "roi_set"
    return {"status": "roi_set", "roi": job["roi"]}


@app.post("/process/{job_id}")
def start_processing(job_id: str, background: BackgroundTasks):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({"error": "not found"}, status_code=404)
    if not job.get("roi"):
        return JSONResponse({"error": "ROI not set"}, status_code=400)
    if job["status"] == "processing":
        return JSONResponse({"error": "already processing"}, status_code=400)

    job["status"] = "processing"
    background.add_task(process_video_task, job_id, job["input"], job["output"])
    return {"status": "processing", "job_id": job_id}


@app.post("/cancel/{job_id}")
def cancel_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({"error": "not found"}, status_code=404)

    job["status"] = "cancelled"

    import time
    time.sleep(0.25)

    cleanup_job_files(job_id)
    del JOBS[job_id]
    return {"status": "cancelled", "job_id": job_id}


@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({"error": "not found"}, status_code=404)

    resp = {
        "status":   job["status"],
        "progress": job.get("progress", 0),
    }
    if job.get("metrics"):
        resp["metrics"] = job["metrics"]
    if job.get("error"):
        resp["error"] = job["error"]
    return resp


@app.get("/video/{job_id}")
def get_video(job_id: str):
    job = JOBS.get(job_id)
    if not job or job["status"] != "done":
        return JSONResponse({"error": "not ready"}, status_code=400)
    return FileResponse(job["output"], media_type="video/mp4")


@app.get("/charts/{job_id}")
def get_charts(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({"error": "not found"}, status_code=404)
    chart_path = job.get("chart_path")
    if not chart_path or not os.path.exists(chart_path):
        return JSONResponse({"error": "not available"}, status_code=400)
    return FileResponse(chart_path, media_type="image/png")


@app.get("/metrics/{job_id}")
def get_metrics(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({"error": "not found"}, status_code=404)
    return job.get("metrics", {})