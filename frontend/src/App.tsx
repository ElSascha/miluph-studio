import { useState } from 'react'

type Page = 'setup' | 'run' | 'visualize'

function App() {
  const [page, setPage] = useState<Page>('run')

  return (
    <div style={{ fontFamily: 'monospace', maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      
      <h1>miluph-studio</h1>

      <nav style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
        <button onClick={() => setPage('setup')}>⚙️ Setup</button>
        <button onClick={() => setPage('run')}>▶️ Run</button>
        <button onClick={() => setPage('visualize')}>🔭 Visualize</button>
      </nav>

      {page === 'setup' && <div>Setup coming soon...</div>}
      {page === 'run' && <Run />}
      {page === 'visualize' && <div>Visualize coming soon...</div>}

    </div>
  )
}

function Run() {
  const [status, setStatus] = useState('idle')
  const [logs, setLogs] = useState<string[]>([])

  const start = async () => {
    await fetch('/api/simulation/start', { method: 'POST' })
    setStatus('running')

    const source = new EventSource('/api/simulation/logs')
    source.onmessage = (e) => {
      setLogs(prev => [...prev, e.data])
    }
    source.onerror = () => {
      setStatus('finished')
      source.close()
    }
  }

  const stop = async () => {
    await fetch('/api/simulation/stop', { method: 'POST' })
    setStatus('idle')
  }

  return (
    <div>
      <h2>Run Simulation</h2>
      <p>Status: <strong>{status}</strong></p>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button onClick={start} disabled={status === 'running'}>▶ Start</button>
        <button onClick={stop} disabled={status !== 'running'}>⏹ Stop</button>
      </div>

      <div style={{
        background: '#111',
        color: '#0f0',
        padding: '15px',
        height: '400px',
        overflowY: 'scroll',
        borderRadius: '6px'
      }}>
        {logs.map((line, i) => <div key={i}>{line}</div>)}
      </div>
    </div>
  )
}

export default App