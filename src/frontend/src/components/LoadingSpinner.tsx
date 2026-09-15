export default function LoadingSpinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '80px 20px',
      gap: 16,
    }}>
      <svg
        width="36" height="36"
        viewBox="0 0 36 36"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="animate-spin"
      >
        <circle cx="18" cy="18" r="14" stroke="var(--border)" strokeWidth="3" />
        <path
          d="M18 4a14 14 0 0 1 14 14"
          stroke="var(--accent)"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
      <span style={{ color: 'var(--muted)', fontSize: '0.8125rem', letterSpacing: '0.02em' }}>
        {label}
      </span>
    </div>
  );
}
