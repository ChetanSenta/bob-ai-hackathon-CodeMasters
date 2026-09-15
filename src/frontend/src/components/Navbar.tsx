import { NavLink } from 'react-router-dom';

const BOB_COPILOT_URL = import.meta.env.VITE_BOB_COPILOT_URL ?? '#';

export default function Navbar() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `btn btn-ghost${isActive ? ' active' : ''}`;

  return (
    <nav style={{
      background: 'var(--surface)',
      borderBottom: '1px solid var(--border)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
    }}>
      {/* accent gradient bar */}
      <div style={{
        height: 2,
        background: 'linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #34d399 100%)',
      }} />

      <div style={{
        maxWidth: 1280,
        margin: '0 auto',
        padding: '0 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 52,
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 18 }}>🛡️</span>
          <span style={{
            color: 'var(--primary)',
            fontWeight: 700,
            fontSize: '0.9375rem',
            letterSpacing: '-0.01em',
            whiteSpace: 'nowrap',
          }}>
            Mission Readiness Officer
          </span>
          <span style={{
            background: 'var(--accent-dim)',
            border: '1px solid rgba(56,189,248,0.3)',
            color: 'var(--accent)',
            fontSize: '0.625rem',
            fontWeight: 700,
            letterSpacing: '0.06em',
            padding: '2px 7px',
            borderRadius: 4,
            textTransform: 'uppercase' as const,
            marginLeft: 4,
          }}>
            LIVE
          </span>
        </div>

        {/* Nav links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <NavLink to="/" end className={linkClass}>Fleet Overview</NavLink>
          <NavLink to="/maintenance" className={linkClass}>Maintenance Plan</NavLink>
          <NavLink to="/upload" className={linkClass}>Data Upload</NavLink>
        </div>

        {/* CTA */}
        <a
          href={BOB_COPILOT_URL}
          target={BOB_COPILOT_URL !== '#' ? '_blank' : undefined}
          rel="noopener noreferrer"
          className="btn btn-accent"
          style={{ marginLeft: 8 }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          Chat with Bob
        </a>
      </div>
    </nav>
  );
}
