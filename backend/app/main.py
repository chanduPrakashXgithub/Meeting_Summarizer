from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.config import UPLOAD_DIR
from app.utils import save_upload_file_tmp
from app.tasks import transcribe_and_summarize
from app.db.database import SessionLocal
from app.db import crud

from pathlib import Path
import os
from app.db.database import Base, engine
from app.db import models

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


app = FastAPI()

# ✅ Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"msg": "Backend running successfully!"}


# ✅ GET meetings list for frontend dashboard
@app.get("/api/meetings")
def get_meetings():
    db = SessionLocal()
    try:
        meetings = crud.get_all_meetings(db)
        return {"meetings": meetings}
    finally:
        db.close()


# ✅ POST upload endpoint
@app.post("/api/upload")
async def upload_meeting(file: UploadFile = File(...)):
    # Save file temporarily
    file_path = save_upload_file_tmp(file)
    # Create meeting entry in DB
    db = SessionLocal()
    meeting = crud.create_meeting(db, filename=file.filename, file_path=file_path)
    db.close()
    return {"meeting_id": meeting.id, "filename": file.filename, "status": "uploaded"}


# ✅ POST transcribe endpoint (trigger Celery background task)
@app.post("/api/transcribe")
async def transcribe(background_tasks: BackgroundTasks, meeting_id: int, file_path: str):
    # Kick off Celery async task
    background_tasks.add_task(transcribe_and_summarize.delay, meeting_id, file_path)
    return {"status": "processing", "meeting_id": meeting_id}


# ✅ GET meeting by ID (to check transcription/summary result)
@app.get("/api/meetings/{meeting_id}")
def get_meeting(meeting_id: int):
    db = SessionLocal()
    try:
        meeting = crud.get_meeting(db, meeting_id)
        if not meeting:
            return {"error": "Meeting not found"}
        return {
            "id": meeting.id,
            "filename": meeting.filename,
            "transcript": meeting.transcript,
            "summary": meeting.summary_json
        }
    finally:
        db.close()
