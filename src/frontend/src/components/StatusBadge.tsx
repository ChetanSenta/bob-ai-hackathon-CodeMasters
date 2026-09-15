import type { ReadinessStatus, Urgency } from '../types';

/* ── Status badge ─────────────────────────────────────────── */
interface StatusBadgeProps {
  status: ReadinessStatus;
  size?: 'sm' | 'md' | 'lg';
}

const STATUS_CONFIG: Record<ReadinessStatus, { bg: string; border: string; text: string; label: string; dot: string }> = {
  GREEN: { bg: 'var(--green-dim)',  border: 'var(--green-border)',  text: 'var(--green)',  label: 'GREEN',  dot: 'var(--green)'  },
  AMBER: { bg: 'var(--amber-dim)', border: 'var(--amber-border)', text: 'var(--amber)', label: 'AMBER', dot: 'var(--amber)' },
  RED:   { bg: 'var(--red-dim)',   border: 'var(--red-border)',   text: 'var(--red)',   label: 'RED',   dot: 'var(--red)'   },
};

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const c = STATUS_CONFIG[status] ?? STATUS_CONFIG['AMBER'];
  const sizeMap = { sm: { px: '4px 9px', fs: '10px', ds: 6 }, md: { px: '5px 11px', fs: '11px', ds: 7 }, lg: { px: '6px 14px', fs: '13px', ds: 8 } };
  const sz = sizeMap[size];

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 5,
      background: c.bg,
      border: `1px solid ${c.border}`,
      color: c.text,
      borderRadius: 9999,
      padding: sz.px,
      fontSize: sz.fs,
      fontWeight: 700,
      letterSpacing: '0.05em',
      whiteSpace: 'nowrap',
    }}>
      {/* Pulsing dot for RED */}
      <span style={{
        width: sz.ds,
        height: sz.ds,
        borderRadius: '50%',
        background: c.dot,
        flexShrink: 0,
        animation: status === 'RED' ? 'pulse 1.5s infinite' : undefined,
        display: 'inline-block',
      }} />
      {c.label}
    </span>
  );
}

/* ── Urgency chip ─────────────────────────────────────────── */
interface UrgencyChipProps { urgency: Urgency; }

const URGENCY_CONFIG: Record<Urgency, { bg: string; border: string; text: string }> = {
  CRITICAL: { bg: 'var(--red-dim)',    border: 'var(--red-border)',    text: 'var(--red)'    },
  HIGH:     { bg: 'var(--orange-dim)', border: 'rgba(251,146,60,0.35)', text: 'var(--orange)' },
  MEDIUM:   { bg: 'var(--amber-dim)', border: 'var(--amber-border)',  text: 'var(--amber)'  },
};

export function UrgencyChip({ urgency }: UrgencyChipProps) {
  const c = URGENCY_CONFIG[urgency] ?? URGENCY_CONFIG['MEDIUM'];
  return (
    <span style={{
      display: 'inline-block',
      background: c.bg,
      border: `1px solid ${c.border}`,
      color: c.text,
      borderRadius: 5,
      padding: '3px 9px',
      fontSize: '10px',
      fontWeight: 800,
      letterSpacing: '0.07em',
      textTransform: 'uppercase',
    }}>
      {urgency}
    </span>
  );
}
