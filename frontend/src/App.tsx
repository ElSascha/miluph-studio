import { useEffect, useState } from 'react'

type Page = 'setup' | 'run' | 'parameter' | 'config' | 'visualize'
type InstanceMode = 'local' | 'remote_ssh'
type Executor = 'direct' | 'slurm'

type InstancePayload = {
  name: string
  mode: InstanceMode
  path?: string
  host?: string
  user?: string
  remote_path?: string
  executor?: Executor
  slurm_partition?: string
}

type InstanceStatus = {
  reachable: boolean
  binary_exists: boolean
  makefile_exists: boolean
}

type InstanceEntry = {
  instance: InstancePayload
  status: InstanceStatus
}

const initialForm: InstancePayload = {
  name: '',
  mode: 'local',
  path: '',
  host: '',
  user: '',
  remote_path: '',
  executor: 'direct',
  slurm_partition: '',
}

function App() {
  const [page, setPage] = useState<Page>('setup')
  const [instances, setInstances] = useState<InstanceEntry[]>([])
  const [selectedInstanceName, setSelectedInstanceName] = useState('')
  const [form, setForm] = useState<InstancePayload>(initialForm)
  const [message, setMessage] = useState('')

  const loadInstances = async () => {
    const res = await fetch('/api/instances')
    const data = await res.json()
    setInstances(data)
    if (data.length > 0 && !data.some((entry: InstanceEntry) => entry.instance.name === selectedInstanceName)) {
      setSelectedInstanceName(data[0].instance.name)
    }
  }

  useEffect(() => {
    void loadInstances()
  }, [])

  const saveInstance = async (event: React.FormEvent) => {
    event.preventDefault()
    const payload: InstancePayload = {
      name: form.name.trim(),
      mode: form.mode,
      executor: form.executor,
      ...(form.mode === 'local'
        ? { path: form.path?.trim() }
        : {
            host: form.host?.trim(),
            user: form.user?.trim(),
            remote_path: form.remote_path?.trim(),
          }),
    }

    if (form.executor === 'slurm' && form.slurm_partition?.trim()) {
      payload.slurm_partition = form.slurm_partition.trim()
    }

    const res = await fetch('/api/instances', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    const data = await res.json()
    if (!res.ok) {
      setMessage(data.detail || 'Could not save installation')
      return
    }

    setMessage(`Saved ${payload.name}`)
    setForm(initialForm)
    await loadInstances()
  }

  return (
    <div style={{ fontFamily: 'monospace', maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <h1>miluph-studio</h1>

      <nav style={{ display: 'flex', gap: '10px', marginBottom: '30px', flexWrap: 'wrap' }}>
        <button onClick={() => setPage('setup')}>⚙️ Setup</button>
        <button onClick={() => setPage('run')}>▶️ Run</button>
        <button onClick={() => setPage('parameter')}>🧩 Parameters</button>
        <button onClick={() => setPage('config')}>📝 Config</button>
        <button onClick={() => setPage('visualize')}>🔭 Visualize</button>
      </nav>

      {page === 'setup' && (
        <div>
          <h2>MiluphCUDA installations</h2>
          <p>Select the installation you want to use for runs.</p>

          <label style={{ display: 'block', marginBottom: '12px' }}>
            <span style={{ display: 'block', marginBottom: '6px' }}>Active installation</span>
            <select
              value={selectedInstanceName}
              onChange={(event) => setSelectedInstanceName(event.target.value)}
              style={{ padding: '8px', width: '100%', maxWidth: '320px' }}
            >
              {instances.map((entry) => (
                <option key={entry.instance.name} value={entry.instance.name}>
                  {entry.instance.name}
                </option>
              ))}
            </select>
          </label>

          <div style={{ display: 'grid', gap: '12px', marginBottom: '24px' }}>
            {instances.map((entry) => (
              <div key={entry.instance.name} style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '12px' }}>
                <strong>{entry.instance.name}</strong>
                <div>Mode: {entry.instance.mode === 'local' ? 'Local' : 'Remote via SSH'}</div>
                <div>Status: {entry.status.reachable ? 'reachable' : 'unreachable'}</div>
                {entry.instance.mode === 'local' ? <div>Path: {entry.instance.path}</div> : <div>Host: {entry.instance.host}</div>}
              </div>
            ))}
          </div>

          <form onSubmit={saveInstance} style={{ display: 'grid', gap: '10px', maxWidth: '500px' }}>
            <input
              placeholder="Name"
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              required
            />

            <select
              value={form.mode}
              onChange={(event) => setForm({ ...form, mode: event.target.value as InstanceMode })}
            >
              <option value="local">Local installation</option>
              <option value="remote_ssh">Remote via SSH</option>
            </select>

            <select
              value={form.executor}
              onChange={(event) => setForm({ ...form, executor: event.target.value as Executor })}
            >
              <option value="direct">Direct execution</option>
              <option value="slurm">Slurm</option>
            </select>

            {form.mode === 'local' ? (
              <input
                placeholder="Local path"
                value={form.path || ''}
                onChange={(event) => setForm({ ...form, path: event.target.value })}
                required
              />
            ) : (
              <>
                <input
                  placeholder="SSH host"
                  value={form.host || ''}
                  onChange={(event) => setForm({ ...form, host: event.target.value })}
                  required
                />
                <input
                  placeholder="SSH user"
                  value={form.user || ''}
                  onChange={(event) => setForm({ ...form, user: event.target.value })}
                  required
                />
                <input
                  placeholder="Remote path"
                  value={form.remote_path || ''}
                  onChange={(event) => setForm({ ...form, remote_path: event.target.value })}
                  required
                />
              </>
            )}

            {form.executor === 'slurm' && (
              <input
                placeholder="Slurm partition"
                value={form.slurm_partition || ''}
                onChange={(event) => setForm({ ...form, slurm_partition: event.target.value })}
              />
            )}

            <button type="submit">Save installation</button>
            {message && <div>{message}</div>}
          </form>
        </div>
      )}

      {page === 'run' && <Run selectedInstanceName={selectedInstanceName} />}
      {page === 'parameter' && <ParameterPage selectedInstanceName={selectedInstanceName} />}
      {page === 'config' && <ConfigPage selectedInstanceName={selectedInstanceName} />}
      {page === 'visualize' && <div>Visualize coming soon...</div>}
    </div>
  )
}

function ParameterPage({ selectedInstanceName }: { selectedInstanceName: string }) {
  const [values, setValues] = useState<Record<string, string>>({
    DIM: '3',
    SOLID: '1',
    HYDRO: '0',
    REAL_HYDRO: '0',
    GRAVITATING_POINT_MASSES: '0',
    PARTICLE_ACCRETION: '0',
    UPDATE_SINK_VALUES: '0',
    INTEGRATE_ENERGY: '1',
    INTEGRATE_DENSITY: '1',
    NAVIER_STOKES: '0',
    SHAKURA_SUNYAEV_ALPHA: '0',
    CONSTANT_KINEMATIC_VISCOSITY: '0',
    KLEY_VISCOSITY: '0',
    FRAGMENTATION: '0',
    DAMAGE_ACTS_ON_S: '0',
    ANEOS_VAPOR_NO_STRENGTH: '0',
    SPH_EQU_VERSION: '1',
    ARTIFICIAL_STRESS: '0',
    ARTIFICIAL_VISCOSITY: '1',
    BALSARA_SWITCH: '0',
    INVISCID_SPH: '0',
    SHEPARD_CORRECTION: '0',
    TENSORIAL_CORRECTION: '1',
    VON_MISES_PLASTICITY: '0',
    DRUCKER_PRAGER_PLASTICITY: '0',
    MOHR_COULOMB_PLASTICITY: '0',
    COLLINS_PLASTICITY: '0',
    COLLINS_PLASTICITY_INCLUDE_MELT_ENERGY: '0',
    COLLINS_PLASTICITY_SIMPLE: '1',
    LOW_DENSITY_WEAKENING: '0',
    VISCOUS_REGOLITH: '0',
    PURE_REGOLITH: '0',
    JC_PLASTICITY: '0',
    PALPHA_POROSITY: '0',
    STRESS_PALPHA_POROSITY: '0',
    SIRONO_POROSITY: '0',
    EPSALPHA_POROSITY: '0',
    MAX_NUM_FLAWS: '1',
    MAX_NUM_INTERACTIONS: '512',
    VARIABLE_SML: '1',
    FIXED_NOI: '0',
    INTEGRATE_SML: '1',
    READ_INITIAL_SML_FROM_PARTICLE_FILE: '0',
    SML_CORRECTION: '0',
    AVERAGE_KERNELS: '0',
    TOO_MANY_INTERACTIONS_KILL_PARTICLE: '0',
    DEAL_WITH_TOO_MANY_INTERACTIONS: '0',
    XSPH: '0',
    BOUNDARY_PARTICLE_ID: '-1',
    GHOST_BOUNDARIES: '0',
    HDF5IO: '1',
    MORE_OUTPUT: '1',
    MORE_ANEOS_OUTPUT: '1',
    OUTPUT_GRAV_ENERGY: '0',
    BINARY_INFO: '0',
  })
  const [message, setMessage] = useState('')

  const save = async (event: React.FormEvent) => {
    event.preventDefault()
    const payload = {
      ...(Object.fromEntries(
        Object.entries(values).map(([key, value]) => [key, Number.isNaN(Number(value)) ? value : Number(value)]),
      )),
      instance_name: selectedInstanceName || undefined,
    }
    const res = await fetch('/api/templates/parameter-h', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await res.json()
    setMessage(res.ok ? `Updated ${selectedInstanceName || 'parameter.h'}` : data.detail || 'Could not update parameter header')
  }

  return (
    <div>
      <h2>Parameter Header</h2>
      <p>Update the values in the selected MiluphCUDA installation.</p>
      <form onSubmit={save} style={{ display: 'grid', gap: '10px', maxWidth: '640px' }}>
        {Object.entries(values).map(([key, value]) => (
          <label key={key} style={{ display: 'grid', gap: '6px' }}>
            <span style={{ fontWeight: 600 }}>{key}</span>
            <input
              value={value}
              onChange={(event) => setValues({ ...values, [key]: event.target.value })}
              placeholder={key}
            />
          </label>
        ))}
        <button type="submit">Save parameter header</button>
        {message && <div>{message}</div>}
      </form>
    </div>
  )
}

function ConfigPage({ selectedInstanceName }: { selectedInstanceName: string }) {
  const [values, setValues] = useState<Record<string, string>>({
    simulation_name: 'demo',
    rho_0: '3000.0',
    bulk_modulus: '1.0e10',
    n: '1.0',
    alpha: '1.0',
    beta: '2.0',
    c_gravity: '6.67408e-11',
  })
  const [message, setMessage] = useState('')

  useEffect(() => {
    const load = async () => {
      const res = await fetch(`/api/templates/miluphcuda-config${selectedInstanceName ? `?instance_name=${encodeURIComponent(selectedInstanceName)}` : ''}`)
      const data = await res.json()
      setValues((prev) => ({ ...prev, ...data.values }))
      setMessage(`Target: ${data.target || 'workspace'}`)
    }
    void load()
  }, [selectedInstanceName])

  const save = async (event: React.FormEvent) => {
    event.preventDefault()
    const payload = {
      ...(Object.fromEntries(
        Object.entries(values).map(([key, value]) => [key, Number.isNaN(Number(value)) ? value : Number(value)]),
      )),
      instance_name: selectedInstanceName || undefined,
    }
    const res = await fetch('/api/templates/miluphcuda-config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await res.json()
    setMessage(res.ok ? `Saved to ${data.target}` : data.detail || 'Could not save config')
  }

  return (
    <div>
      <h2>MiluphCUDA Config</h2>
      <p>Edit the material config values and save them into the selected MiluphCUDA simulation folder.</p>
      <form onSubmit={save} style={{ display: 'grid', gap: '10px', maxWidth: '640px' }}>
        {Object.entries(values).map(([key, value]) => (
          <label key={key} style={{ display: 'grid', gap: '6px' }}>
            <span style={{ fontWeight: 600 }}>{key}</span>
            <input
              value={value}
              onChange={(event) => setValues({ ...values, [key]: event.target.value })}
              placeholder={key}
            />
          </label>
        ))}
        <button type="submit">Save config</button>
        {message && <div>{message}</div>}
      </form>
    </div>
  )
}

function Run({ selectedInstanceName }: { selectedInstanceName: string }) {
  const [status, setStatus] = useState('idle')
  const [logs, setLogs] = useState<string[]>([])

  const start = async () => {
    await fetch('/api/simulation/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ instance_name: selectedInstanceName }),
    })
    setStatus('running')

    const source = new EventSource('/api/simulation/logs')
    source.onmessage = (e) => {
      setLogs((prev) => [...prev, e.data])
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
      <p>Selected installation: <strong>{selectedInstanceName || 'None'}</strong></p>

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