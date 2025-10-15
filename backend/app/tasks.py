
from celery import Celery
from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from app.utils import call_whisper_transcribe, call_llm_summarize
from app.db.database import SessionLocal
from app.db import crud
import json
celery_app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
@celery_app.task(bind=True, name='transcribe_and_summarize', queue='transcribe_queue')
def transcribe_and_summarize(self, meeting_id: int, file_path: str):
    db = SessionLocal()
    try:
        transcript = call_whisper_transcribe(file_path)
    except Exception as e:
        db.close(); raise self.retry(exc=e, countdown=10, max_retries=3)
    system_prompt = (
        "You are a meeting summarization assistant.\n"
        "Output strictly in JSON format with keys: summary, decisions, actions.\n"
        "Example:\n{\n  \"summary\": \"...\",\n  \"decisions\": [\"...\"],\n  \"actions\": [\"...\"]\n}\n"
        "Do not add any extra text."
    )
    user_prompt = "Summarize the following meeting transcript. Provide summary, decisions, and actions in JSON. Transcript:\n\n" + transcript
    try:
        raw = call_llm_summarize(transcript, system_prompt, user_prompt)
        try:
            parsed = json.loads(raw)
        except Exception:
            start = raw.find('{'); end = raw.rfind('}')
            if start != -1 and end != -1:
                parsed = json.loads(raw[start:end+1])
            else:
                parsed = {"summary":"", "decisions":[], "actions":[]}
    except Exception as e:
        db.close(); raise self.retry(exc=e, countdown=10, max_retries=3)
    try:
        crud.update_meeting(db, meeting_id, transcript=transcript, summary_json=parsed)
    finally:
        db.close()
    return parsed
