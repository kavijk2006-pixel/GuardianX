import React, { useState, useEffect, useRef } from 'react'
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
  const [mode, setMode] = useState('select') // 'select' or 'custom'
  const [candidatesList, setCandidatesList] = useState([])
  const [selectedId, setSelectedId] = useState('')
  const [candidate, setCandidate] = useState(null)

  // Custom candidate resume state
  const [customName, setCustomName] = useState('Alex Rivera')
  const [customRole, setCustomRole] = useState('Senior Cloud Architect')
  const [customExp, setCustomExp] = useState('7')
  const [customEdu, setCustomEdu] = useState('M.S. Software Engineering')
  const [customSkills, setCustomSkills] = useState('Kubernetes, Terraform, AWS, Go, Microservices')
  const [customResume, setCustomResume] = useState(
    'Experienced Cloud Architect specializing in designing resilient distributed microservices, infrastructure as code (IaC), container orchestration with Kubernetes, and high-availability cloud security patterns.'
  )

  const [transcript, setTranscript] = useState([])
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [started, setStarted] = useState(false)
  const [done, setDone] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [status, setStatus] = useState('')

  const chatEndRef = useRef(null)

  useEffect(() => {
    async function loadCandidates() {
      try {
        const res = await fetch('/candidates.json')
        if (!res.ok) return
        const data = await res.json()
        const list = data.candidates || []
        setCandidatesList(list)
        if (list.length > 0) {
          setSelectedId(list[0].member?.id || '')
          setCandidate(list[0])
        }
      } catch (e) {
        // ignore
      }
    }
    loadCandidates()
  }, [])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [transcript, loading])

  const handleSelectCandidate = (id) => {
    setSelectedId(id)
    const found = candidatesList.find(c => c.member && c.member.id === id)
    if (found) {
      setCandidate(found)
    }
  }

  const getActiveCandidatePayload = () => {
    if (mode === 'select') {
      return candidate
    }
    const skillsArray = customSkills.split(',').map(s => s.trim()).filter(Boolean)
    return {
      member: {
        id: `CAND-CUSTOM-${Date.now().toString().slice(-4)}`,
        name: customName || 'New Candidate',
        jobRole: customRole || 'Software Engineer',
        yearsExperience: parseInt(customExp) || 3,
        education: customEdu || 'B.S. Computer Science',
        skills: skillsArray,
        resumeText: customResume,
        status: 'NEW_RESUME'
      },
      missions: [],
      signals: {}
    }
  }

  const append = (from, text) => {
    setTranscript(t => [...t, { from, text, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }])
  }

  const handleStart = async () => {
    if (!sessionId) {
      setStatus('Session ID required')
      return
    }
    const targetCandidate = getActiveCandidatePayload()
    if (!targetCandidate || !targetCandidate.member) {
      setStatus('Candidate information required')
      return
    }
    setCandidate(targetCandidate)
    setStatus('Initializing AI Interviewer session...')
    setLoading(true)
    try {
      const res = await startInterview(sessionId, targetCandidate)
      if (!res.ok) {
        const err = await res.json()
        setStatus(`Error: ${err.detail || res.statusText}`)
        setLoading(false)
        return
      }
      const data = await res.json()
      append('ai', data.reply)
      setStarted(true)
      setDone(!!data.done)
      if (data.done && data.feedback) {
        setFeedback(data.feedback)
      }
      setStatus('Interview active')
    } catch (err) {
      setStatus('Network error connecting to backend')
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async (e) => {
    if (e) e.preventDefault()
    if (!message.trim() || loading || done) return

    const userText = message.trim()
    append('candidate', userText)
    setMessage('')
    setLoading(true)
    setStatus('AI Interviewer is evaluating your response...')

    try {
      const res = await sendMessage(sessionId, userText)
      if (!res.ok) {
        const err = await res.json()
        setStatus(`Error: ${err.detail || res.statusText}`)
        setLoading(false)
        return
      }
      const data = await res.json()
      if (data.reply) append('ai', data.reply)
      setDone(!!data.done)
      if (data.done && data.feedback) {
        setFeedback(data.feedback)
        setStatus('Interview completed')
      } else {
        setStatus('Turn processed')
      }
    } catch (err) {
      setStatus('Network error processing response')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setTranscript([])
    setMessage('')
    setStarted(false)
    setDone(false)
    setFeedback(null)
    setStatus('')
    setSessionId(uuidv4())
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand">
          <div className="logo-badge">🤖</div>
          <div>
            <h1>GuardianX AI Interviewer</h1>
            <p className="subtitle">Build the interviewer, not the interview</p>
          </div>
        </div>
        <div className="session-chip">
          <span className={`status-dot ${started ? (done ? 'completed' : 'active') : 'idle'}`}></span>
          <span>{started ? (done ? 'Completed' : 'Interview Live') : 'Ready'}</span>
        </div>
      </header>

      {/* Main Grid */}
      <div className="app-layout">
        {/* Left Sidebar: Candidate Profile, Resume & Config */}
        <aside className="sidebar">
          <div className="card">
            <h3>Candidate Selection</h3>

            {/* Mode Switch Tabs */}
            <div className="tab-group">
              <button
                className={`tab-btn ${mode === 'select' ? 'active' : ''}`}
                onClick={() => setMode('select')}
                disabled={started}
              >
                📂 Existing List
              </button>
              <button
                className={`tab-btn ${mode === 'custom' ? 'active' : ''}`}
                onClick={() => setMode('custom')}
                disabled={started}
              >
                📄 New Resume
              </button>
            </div>

            {mode === 'select' ? (
              <div className="form-section">
                <label className="field-label">Select Candidate Profile</label>
                <select
                  className="select-input"
                  value={selectedId}
                  onChange={e => handleSelectCandidate(e.target.value)}
                  disabled={started}
                >
                  {candidatesList.map(c => (
                    <option key={c.member?.id} value={c.member?.id}>
                      {c.member?.id}: {c.member?.name} ({c.member?.jobRole})
                    </option>
                  ))}
                </select>

                {candidate && candidate.member && (
                  <div className="candidate-badge">
                    <div className="avatar">{candidate.member.name.charAt(0)}</div>
                    <div className="candidate-details">
                      <h4>{candidate.member.name}</h4>
                      <p className="role">{candidate.member.jobRole}</p>
                      <p className="meta">
                        ⏱️ {candidate.member.yearsExperience} YOE | 🎓 {candidate.member.education}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="form-section custom-resume-form">
                <div className="field-group">
                  <label className="field-label">Full Name</label>
                  <input className="text-input" value={customName} onChange={e => setCustomName(e.target.value)} disabled={started} placeholder="e.g. Sarah Connor" />
                </div>

                <div className="field-group">
                  <label className="field-label">Target Job Role</label>
                  <input className="text-input" value={customRole} onChange={e => setCustomRole(e.target.value)} disabled={started} placeholder="e.g. Lead DevOps Engineer" />
                </div>

                <div className="form-row">
                  <div className="field-group">
                    <label className="field-label">YOE</label>
                    <input className="text-input" value={customExp} onChange={e => setCustomExp(e.target.value)} disabled={started} placeholder="e.g. 5" />
                  </div>
                  <div className="field-group">
                    <label className="field-label">Education</label>
                    <input className="text-input" value={customEdu} onChange={e => setCustomEdu(e.target.value)} disabled={started} placeholder="e.g. B.S. CS" />
                  </div>
                </div>

                <div className="field-group">
                  <label className="field-label">Primary Skills (comma separated)</label>
                  <input className="text-input" value={customSkills} onChange={e => setCustomSkills(e.target.value)} disabled={started} placeholder="e.g. Docker, Terraform, Python" />
                </div>

                <div className="field-group">
                  <label className="field-label">Paste Candidate Resume / Bio</label>
                  <textarea
                    className="text-input resume-textarea"
                    value={customResume}
                    onChange={e => setCustomResume(e.target.value)}
                    disabled={started}
                    placeholder="Paste resume summary, work history, or project background..."
                  />
                </div>
              </div>
            )}

            <div className="field-group">
              <label className="field-label">Session ID</label>
              <input
                className="text-input"
                value={sessionId}
                onChange={e => setSessionId(e.target.value)}
                disabled={started}
              />
            </div>

            <div className="button-group">
              {!started ? (
                <button className="btn btn-primary" onClick={handleStart} disabled={loading}>
                  {loading ? 'Starting...' : (mode === 'custom' ? '📄 Start Resume Interview' : '🚀 Start AI Interview')}
                </button>
              ) : (
                <button className="btn btn-secondary" onClick={handleReset}>
                  🔄 New Session
                </button>
              )}
            </div>

            {status && <div className="status-banner">{status}</div>}
          </div>
        </aside>


  const handleSend = async (e) => {
    if (e) e.preventDefault()
    if (!message.trim() || loading || done) return

    const userText = message.trim()
    append('candidate', userText)
    setMessage('')
    setLoading(true)
    setStatus('AI Interviewer is evaluating your response...')

    try {
      const res = await sendMessage(sessionId, userText)
      if (!res.ok) {
        const err = await res.json()
        setStatus(`Error: ${err.detail || res.statusText}`)
        setLoading(false)
        return
      }
      const data = await res.json()
      if (data.reply) append('ai', data.reply)
      setDone(!!data.done)
      if (data.done && data.feedback) {
        setFeedback(data.feedback)
        setStatus('Interview completed')
      } else {
        setStatus('Turn processed')
      }
    } catch (err) {
      setStatus('Network error processing response')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setTranscript([])
    setMessage('')
    setStarted(false)
    setDone(false)
    setFeedback(null)
    setStatus('')
    setSessionId(uuidv4())
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand">
          <div className="logo-badge">🤖</div>
          <div>
            <h1>GuardianX AI Interviewer</h1>
            <p className="subtitle">Build the interviewer, not the interview</p>
          </div>
        </div>
        <div className="session-chip">
          <span className={`status-dot ${started ? (done ? 'completed' : 'active') : 'idle'}`}></span>
          <span>{started ? (done ? 'Completed' : 'Interview Live') : 'Ready'}</span>
        </div>
      </header>

      {/* Main Grid */}
      <div className="app-layout">
        {/* Left Sidebar: Candidate Profile & Config */}
        <aside className="sidebar">
          <div className="card">
            <h3>Candidate Selection</h3>
            <label className="field-label">Select Candidate Profile</label>
            <select
              className="select-input"
              value={selectedId}
              onChange={e => handleSelectCandidate(e.target.value)}
              disabled={started}
            >
              {candidatesList.map(c => (
                <option key={c.member?.id} value={c.member?.id}>
                  {c.member?.id}: {c.member?.name} ({c.member?.jobRole})
                </option>
              ))}
            </select>

            {candidate && candidate.member && (
              <div className="candidate-badge">
                <div className="avatar">{candidate.member.name.charAt(0)}</div>
                <div className="candidate-details">
                  <h4>{candidate.member.name}</h4>
                  <p className="role">{candidate.member.jobRole}</p>
                  <p className="meta">
                    ⏱️ {candidate.member.yearsExperience} YOE | 🎓 {candidate.member.education}
                  </p>
                </div>
              </div>
            )}

            <div className="field-group">
              <label className="field-label">Session ID</label>
              <input
                className="text-input"
                value={sessionId}
                onChange={e => setSessionId(e.target.value)}
                disabled={started}
              />
            </div>

            <div className="button-group">
              {!started ? (
                <button className="btn btn-primary" onClick={handleStart} disabled={loading || !candidate}>
                  {loading ? 'Starting...' : '🚀 Start AI Interview'}
                </button>
              ) : (
                <button className="btn btn-secondary" onClick={handleReset}>
                  🔄 New Session
                </button>
              )}
            </div>

            {status && <div className="status-banner">{status}</div>}
          </div>
        </aside>

        {/* Right Main Area: Chat & Feedback */}
        <main className="chat-section">
          <div className="chat-window">
            <div className="chat-messages">
              {transcript.length === 0 && !loading && (
                <div className="empty-state">
                  <div className="empty-icon">💬</div>
                  <h3>Ready to begin interview</h3>
                  <p>Select a candidate profile on the left and click <strong>Start AI Interview</strong>.</p>
                </div>
              )}

              {transcript.map((m, i) => (
                <div key={i} className={`chat-bubble-row ${m.from}`}>
                  <div className="avatar-icon">
                    {m.from === 'ai' ? '🤖' : '👤'}
                  </div>
                  <div className="bubble-content">
                    <div className="bubble-header">
                      <span className="author-name">{m.from === 'ai' ? 'AI Interviewer' : (candidate?.member?.name || 'Candidate')}</span>
                      <span className="timestamp">{m.timestamp}</span>
                    </div>
                    <div className="bubble-text">{m.text}</div>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="chat-bubble-row ai loading">
                  <div className="avatar-icon">🤖</div>
                  <div className="bubble-content">
                    <div className="typing-indicator">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input Composer */}
            <form className="composer-form" onSubmit={handleSend}>
              <textarea
                className="composer-textarea"
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder={done ? "Interview completed." : (started ? "Type your technical answer here..." : "Start the interview first...")}
                disabled={!started || done || loading}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSend()
                  }
                }}
              />
              <button
                type="submit"
                className="btn btn-send"
                disabled={!started || done || loading || !message.trim()}
              >
                Send Response ↵
              </button>
            </form>
          </div>

          {/* Feedback & Score Dashboard Card */}
          {done && feedback && (
            <div className="feedback-card">
              <div className="feedback-header">
                <h2>🏆 Interview Score & Assessment Dashboard</h2>
                <span className="badge-done">Completed</span>
              </div>

              {feedback.score && (
                <div className="score-dashboard">
                  <div className="score-hero">
                    <div className="score-circle">
                      <span className="score-value">{feedback.score.overall}%</span>
                      <span className="score-label">Overall Score</span>
                    </div>
                    <div className="grade-badge">{feedback.score.grade}</div>
                  </div>

                  <div className="score-metrics-grid">
                    <div className="metric-box">
                      <div className="metric-header">
                        <span>🎯 Technical Correctness</span>
                        <span className="metric-num">{feedback.score.correctness}%</span>
                      </div>
                      <div className="progress-bar"><div className="progress-fill" style={{ width: `${feedback.score.correctness}%` }}></div></div>
                    </div>

                    <div className="metric-box">
                      <div className="metric-header">
                        <span>🏗️ System Depth</span>
                        <span className="metric-num">{feedback.score.depth}%</span>
                      </div>
                      <div className="progress-bar"><div className="progress-fill" style={{ width: `${feedback.score.depth}%` }}></div></div>
                    </div>

                    <div className="metric-box">
                      <div className="metric-header">
                        <span>💻 Practical Implementation</span>
                        <span className="metric-num">{feedback.score.practical}%</span>
                      </div>
                      <div className="progress-bar"><div className="progress-fill" style={{ width: `${feedback.score.practical}%` }}></div></div>
                    </div>

                    <div className="metric-box">
                      <div className="metric-header">
                        <span>🧩 Problem Solving</span>
                        <span className="metric-num">{feedback.score.problem_solving}%</span>
                      </div>
                      <div className="progress-bar"><div className="progress-fill" style={{ width: `${feedback.score.problem_solving}%` }}></div></div>
                    </div>
                  </div>
                </div>
              )}

              <p className="summary-text"><strong>Executive Summary:</strong> {feedback.summary}</p>

              <div className="feedback-grid">
                <div className="feedback-box strengths">
                  <h4>✅ Demonstrated Strengths</h4>
                  <ul>
                    {(feedback.strengths || []).map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>

                <div className="feedback-box gaps">
                  <h4>⚠️ Focus / Growth Areas</h4>
                  <ul>
                    {(feedback.gaps || []).map((g, i) => (
                      <li key={i}>{g}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="feedback-box next-steps">
                <h4>🎯 Recommended Next Steps</h4>
                <ul>
                  {(feedback.next || []).map((n, i) => (
                    <li key={i}>{n}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  )
}

