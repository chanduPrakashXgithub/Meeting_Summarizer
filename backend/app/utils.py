
from pathlib import Path
import shutil, uuid, json
from fastapi import UploadFile
from app.config import UPLOAD_DIR, OPENAI_API_KEY, OPENAI_TIMEOUT, OPENAI_TRANSCRIBE_MODEL, OPENAI_SUMMARY_MODEL
import openai
openai.api_key = OPENAI_API_KEY
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
def save_upload_file_tmp(upload_file: UploadFile) -> str:
    ext = Path(upload_file.filename).suffix or ".wav"
    dest_filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = Path(UPLOAD_DIR) / dest_filename
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return str(dest_path)
def call_whisper_transcribe(file_path: str) -> str:
    with open(file_path, "rb") as f:
        resp = openai.Audio.transcribe(model=OPENAI_TRANSCRIBE_MODEL, file=f, timeout=OPENAI_TIMEOUT)
        if isinstance(resp, dict):
            return resp.get("text", str(resp))
        if hasattr(resp, "text"):
            return resp.text
        return str(resp)
def call_llm_summarize(transcript: str, system_prompt: str, user_prompt: str) -> str:
    resp = openai.ChatCompletion.create(
        model=OPENAI_SUMMARY_MODEL,
        messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],
        temperature=0.0,
        max_tokens=1000,
        timeout=OPENAI_TIMEOUT
    )
    return resp["choices"][0]["message"]["content"]
def extract_json(text: str) -> dict:
    start = text.find('{'); end = text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model output")
    return json.loads(text[start:end+1])
