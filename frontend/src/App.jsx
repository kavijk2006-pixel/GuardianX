import React, { useState, useEffect } from 'react'
import { startInterview, sendMessage } from './api'

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = (Math.random() * 16) | 0,
      v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

export default function App() {
  const [sessionId, setSessionId] = useState(uuidv4())
  const [candidate, setCandidate] = useState(null)
  const [transcript, setTranscript] = useState([])
  const [message, setMessage] = useState('')
  const [done, setDone] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [status, setStatus] = useState('')

  useEffect(() => {
    // try to load candidate CAND-004 from /candidates.json via backend proxy
    async function loadCandidate() {
      try {
        const res = await fetch('/candidates.json')
        if (!res.ok) return
        const data = await res.json()
        const found = (data.candidates || []).find(c => c.member && c.member.id === 'CAND-004')
        if (found) setCandidate(found)
      } catch (e) {
        // ignore
      }
    }
    loadCandidate()
  }, [])

  const append = (from, text) => {
    setTranscript(t => [...t, { from, text }])
  }

  const handleStart = async () => {
    if (!sessionId) {
      setStatus('sessionId required')
      return
    }
    if (!candidate) {
      setStatus('candidate not set')
      return
    }
    setStatus('Starting interview...')
    try {
      const res = await startInterview(sessionId, candidate)
      if (!res.ok) {
        const err = await res.json()
        setStatus(`Error: ${err.detail || res.statusText}`)
        return
      }
      const data = await res.json()
      append('ai', data.reply)
      setDone(!!data.done)
      if (data.done && data.feedback) {
        setFeedback(data.feedback)
      }
      setStatus('Interview started')
    } catch (err) {
      setStatus('Network error')
    }
  }

  const handleSend = async () => {
    if (!message.trim()) {
      setStatus('Please enter a message')
      return
    }
    append('candidate', message)
    setStatus('Sending...')
    try {
      const res = await sendMessage(sessionId, message)
      if (!res.ok) {
        const err = await res.json()
        setStatus(`Error: ${err.detail || res.statusText}`)
        return
      }
      const data = await res.json()
      if (data.reply) append('ai', data.reply)
      setDone(!!data.done)
      if (data.done && data.feedback) {
        setFeedback(data.feedback)
      }
      setMessage('')
      setStatus('Turn processed')
    } catch (err) {
      setStatus('Network error')
    }
  }

  const handleLoadCandidate = async () => {
    try {
      const res = await fetch('/candidates.json')
      if (!res.ok) throw new Error('Failed to fetch')
      const data = await res.json()
      const found = (data.candidates || []).find(c => c.member && c.member.id === 'CAND-004')
      if (found) {
        setCandidate(found)
        setStatus('Loaded candidate CAND-004')
      } else setStatus('CAND-004 not found')
    } catch (e) {
      setStatus('Failed to load candidates.json')
    }
  }

  const handleReset = () => {
    setTranscript([])
    setMessage('')
    setDone(false)
    setFeedback(null)
    setStatus('')
    setSessionId(uuidv4())
  }

  return (
    <div className="container">
      <h1>GuardianX Interview</h1>
      <div className="controls">
        <label>Session ID:
          <input value={sessionId} onChange={e => setSessionId(e.target.value)} />
        </label>
        <div className="candidate-row">
          <button onClick={handleLoadCandidate}>Load CAND-004</button>
          <button onClick={handleStart} disabled={!candidate || done}>Start Interview</button>
          <button onClick={handleReset}>New Session</button>
        </div>
        <div className="status">{status}</div>
      </div>

      <div className="main">
        <div className="transcript">
          <h2>Transcript</h2>
          <div className="messages">
            {transcript.map((m, i) => (
              <div key={i} className={`message ${m.from}`}>
                <strong>{m.from}:</strong> {m.text}
              </div>
            ))}
          </div>
        </div>

        <div className="composer">
          <textarea value={message} onChange={e => setMessage(e.target.value)} placeholder="Your answer here..." />
          <button onClick={handleSend} disabled={done}>Send</button>

          {done && feedback && (
            <div className="feedback">
              <h3>Final feedback</h3>
              <p><strong>Summary:</strong> {feedback.summary}</p>
              <p><strong>Strengths:</strong></p>
              <ul>{(feedback.strengths||[]).map((s,i)=>(<li key={i}>{s}</li>))}</ul>
              <p><strong>Gaps:</strong></p>
              <ul>{(feedback.gaps||[]).map((g,i)=>(<li key={i}>{g}</li>))}</ul>
              <p><strong>Next:</strong></p>
              <ul>{(feedback.next||[]).map((n,i)=>(<li key={i}>{n}</li>))}</ul>
            </div>
          )}
        </div>
      </div>

      <div className="footer">
        <p>Candidate loaded: {candidate ? candidate.member?.id : 'none'}</p>
      </div>
    </div>
  )
}
