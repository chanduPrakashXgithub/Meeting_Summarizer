# app/db/crud.py
from app.db import models

def create_meeting(db, filename, file_path):
    meeting = models.Meeting(filename=filename, file_path=file_path)
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

def get_meeting(db, meeting_id):
    return db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()

def get_all_meetings(db):
    return db.query(models.Meeting).order_by(models.Meeting.id.desc()).all()

def update_meeting(db, meeting_id, transcript, summary_json):
    meeting = get_meeting(db, meeting_id)
    if meeting:
        meeting.transcript = transcript
        meeting.summary_json = summary_json
        db.commit()
        db.refresh(meeting)
    return meeting
