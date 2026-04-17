import { NavLink, Outlet } from 'react-router-dom'

export function AppShell() {
  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <div className="logo-mark" />
          <div>
            <div className="brand-name">SceneProof</div>
            <div className="brand-tag">Policy → training video</div>
          </div>
        </div>
        <nav className="nav">
          <NavLink to="/" end className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
            Upload
          </NavLink>
          <span className="nav-muted">Review & output follow your job</span>
        </nav>
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="footer muted">
        Beta University Seed Agents Challenge · Seed 2.0 · Seedream · Seedance · Seed Speech · OmniHuman
      </footer>
    </div>
  )
}
