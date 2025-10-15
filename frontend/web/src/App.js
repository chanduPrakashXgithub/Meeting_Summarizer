
import React, { useState, useEffect } from 'react';
import { uploadFile, transcribeFile, summarizeTranscript, getMeetings } from './api';
import Header from './components/Header';
import Footer from './components/Footer';

function App() {
  const [file, setFile] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [meetings, setMeetings] = useState([]);

  useEffect(() => {
    fetchMeetings();
  }, []);

  const fetchMeetings = async () => {
    try {
      const resp = await getMeetings();
      setMeetings(resp.data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUploadAndTranscribe = async () => {
    if (!file) return alert('Choose file first');
    setLoading(true);
    try {
      await uploadFile(file);
      alert('File uploaded. Processing in background. Refresh meetings to see result.');
      fetchMeetings();
    } catch (err) {
      alert('Upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleTranscribeDirect = async () => {
    if (!file) return alert('Choose file first');
    setLoading(true);
    try {
      const resp = await transcribeFile(file);
      setTranscript(resp.data.transcript || '');
    } catch (err) {
      alert('Transcription failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    if (!transcript) return alert('No transcript to summarize');
    setLoading(true);
    try {
      const resp = await summarizeTranscript(transcript);
      setSummary(resp.data);
    } catch (err) {
      alert('Summarization failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Header />
      <div className="container py-4">
        <h1 className="mb-4">Meeting Summarizer</h1>

        <div className="mb-3">
          <label className="form-label">Upload audio (mp3/wav)</label>
          <input className="form-control" type="file" accept="audio/*" onChange={handleFileChange} />
        </div>
        <div className="mb-3 d-flex gap-2">
          <button className="btn btn-primary" onClick={handleUploadAndTranscribe} disabled={loading}>Upload & Background Process</button>
          <button className="btn btn-secondary" onClick={handleTranscribeDirect} disabled={loading}>Transcribe Now (sync)</button>
        </div>

        <div className="mb-3">
          <label className="form-label">Transcript</label>
          <textarea className="form-control" rows="8" value={transcript} onChange={(e)=>setTranscript(e.target.value)}></textarea>
        </div>
        <div className="mb-3">
          <button className="btn btn-success" onClick={handleSummarize} disabled={loading}>Generate Summary</button>
        </div>

        {summary && (
          <div className="row g-3">
            <div className="col-md-4">
              <div className="card card-summary">
                <div className="card-body">
                  <h5 className="card-title">Summary</h5>
                  <p className="card-text">{summary.summary}</p>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card">
                <div className="card-body">
                  <h5 className="card-title">Decisions</h5>
                  <ul>{summary.decisions.map((d,i)=><li key={i}>{d}</li>)}</ul>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card">
                <div className="card-body">
                  <h5 className="card-title">Actions</h5>
                  <ul>{summary.actions.map((a,i)=><li key={i}>{a}</li>)}</ul>
                </div>
              </div>
            </div>
          </div>
        )}

        <hr className="my-4" />
        <h3>Recent Meetings</h3>
        <ul className="list-group">
          {meetings.map(m=> (
            <li key={m.id} className="list-group-item d-flex justify-content-between align-items-start">
              <div>
                <div className="fw-bold">{m.filename}</div>
                <div><small>{new Date(m.created_at).toLocaleString()}</small></div>
              </div>
              <div>
                <button className="btn btn-sm btn-outline-primary me-2" onClick={()=>{ setTranscript(m.transcript || '') ; if (m.summary_json) setSummary(JSON.parse(m.summary_json)); }}>Load</button>
              </div>
            </li>
          ))}
        </ul>

      </div>
      <Footer />
    </div>
  );
}

export default App;
