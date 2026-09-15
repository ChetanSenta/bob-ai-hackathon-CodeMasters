import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getFleetReadiness } from '../api/client';
import type { AssetReadinessSummary, FleetReadinessResponse, ReadinessStatus } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

type Filter = 'All' | 'Helicopters' | 'Fixed-Wing' | 'Ground Vehicles' | 'RED only';
const FILTER_LABELS: Filter[] = ['All', 'Helicopters', 'Fixed-Wing', 'Ground Vehicles', 'RED only'];

function matchesFilter(asset: AssetReadinessSummary, filter: Filter): boolean {
  if (filter === 'All') return true;
  if (filter === 'RED only') return asset.overall_status === 'RED';
  const t = asset.asset_type?.toLowerCase() ?? '';
  if (filter === 'Helicopters') return t.includes('helicopter') || t.includes('rotary');
  if (filter === 'Fixed-Wing') return t.includes('fixed') || t.includes('aircraft') || t.includes('plane');
  if (filter === 'Ground Vehicles') return t.includes('ground') || t.includes('vehicle') || t.includes('tank');
  return true;
}

function formatDate(iso?: string): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
  });
}

function ScoreBar({ score, status }: { score: number; status: ReadinessStatus }) {
  const color = status === 'GREEN' ? 'var(--green)' : status === 'AMBER' ? 'var(--amber)' : 'var(--red)';
  return (
    <div className="score-track">
      <div className="score-fill" style={{ width: `${score}%`, background: color }} />
    </div>
  );
}

function SummaryPill({ count, label, color }: { count: number; label: string; color: string }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 8,
      background: 'var(--card)', border: '1px solid var(--border)',
      borderRadius: 8, padding: '10px 16px',
    }}>
      <span style={{ fontSize: '1.25rem', fontWeight: 800, color }}>{count}</span>
      <span style={{ fontSize: '0.6875rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: 'var(--muted)' }}>{label}</span>
    </div>
  );
}

export default function FleetOverview() {
  const [data, setData] = useState<FleetReadinessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Filter>('All');

  useEffect(() => {
    getFleetReadiness()
      .then(({ data }) => setData(data))
      .catch((e) => setError(e?.message ?? 'Failed to reach API'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Fetching fleet readiness…" />;

  if (error) {
    return (
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '40px 20px' }}>
        <div className="alert alert-error">
          <strong>⚠ Backend unreachable</strong> — {error}
          <p style={{ marginTop: 6, color: 'var(--muted)', fontSize: '0.75rem' }}>
            Ensure the backend is running at <code style={{ color: 'var(--accent)' }}>http://localhost:8000</code>
          </p>
        </div>
      </div>
    );
  }

  const fleet = data?.fleet ?? [];
  const summary = data?.summary;
  const filtered = fleet.filter((a) => matchesFilter(a, filter));

  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '32px 20px' }} className="fade-in">

      {/* Page header */}
      <div style={{ marginBottom: 28, display: 'flex', flexWrap: 'wrap', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
        <div>
          <h1 className="page-title">Fleet Overview</h1>
          <p style={{ color: 'var(--muted)', fontSize: '0.8125rem', marginTop: 4 }}>
            Real-time readiness status across all assigned platforms
          </p>
        </div>

        {/* Summary pills */}
        {summary && (
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <SummaryPill count={summary.total}  label="Total"  color="var(--primary)" />
            <SummaryPill count={summary.GREEN}  label="Green"  color="var(--green)"   />
            <SummaryPill count={summary.AMBER}  label="Amber"  color="var(--amber)"   />
            <SummaryPill count={summary.RED}    label="Red"    color="var(--red)"     />
          </div>
        )}
      </div>

      {/* Filter row */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 24 }}>
        {FILTER_LABELS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`btn btn-ghost${filter === f ? ' active' : ''}`}
          >
            {f}
            {f === 'RED only' && summary?.RED ? (
              <span style={{
                background: 'var(--red)',
                color: '#fff',
                borderRadius: 9999,
                padding: '1px 6px',
                fontSize: '10px',
                fontWeight: 700,
                marginLeft: 4,
              }}>
                {summary.RED}
              </span>
            ) : null}
          </button>
        ))}
        <span style={{ marginLeft: 'auto', color: 'var(--muted)', fontSize: '0.75rem', alignSelf: 'center' }}>
          {filtered.length} asset{filtered.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Asset grid */}
      {filtered.length === 0 ? (
        <p style={{ color: 'var(--muted)', textAlign: 'center', padding: '60px 0', fontSize: '0.875rem' }}>
          No assets match this filter.
        </p>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: 16,
        }}>
          {filtered.map((asset) => {
            const borderColor =
              asset.overall_status === 'RED'   ? 'rgba(248,113,113,0.45)' :
              asset.overall_status === 'AMBER' ? 'rgba(251,191,36,0.35)'  : 'var(--border)';
            const glowColor =
              asset.overall_status === 'RED'   ? '0 0 20px rgba(248,113,113,0.10)' :
              asset.overall_status === 'AMBER' ? '0 0 20px rgba(251,191,36,0.08)'  : 'none';

            return (
              <Link key={asset.asset_id} to={`/asset/${asset.asset_id}`} style={{ textDecoration: 'none', display: 'block' }}>
                <div style={{
                  background: 'var(--card)',
                  border: `1px solid ${borderColor}`,
                  borderRadius: 10,
                  padding: '18px 20px',
                  cursor: 'pointer',
                  transition: 'border-color 0.2s, box-shadow 0.2s, transform 0.15s',
                  boxShadow: glowColor,
                }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-2px)';
                    (e.currentTarget as HTMLDivElement).style.boxShadow = '0 6px 24px rgba(0,0,0,0.5)';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)';
                    (e.currentTarget as HTMLDivElement).style.boxShadow = glowColor;
                  }}
                >
                  {/* Header row */}
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 10 }}>
                    <div>
                      <div style={{ color: 'var(--primary)', fontWeight: 800, fontSize: '1.125rem', letterSpacing: '-0.01em' }}>
                        {asset.tail_number}
                      </div>
                      <div style={{ color: 'var(--muted)', fontSize: '0.75rem', marginTop: 2 }}>
                        {asset.platform}
                      </div>
                    </div>
                    <StatusBadge status={asset.overall_status} size="sm" />
                  </div>

                  {/* Unit / base */}
                  {(asset.unit || asset.base) && (
                    <div style={{
                      color: 'var(--muted)', fontSize: '0.6875rem', marginBottom: 12,
                      display: 'flex', alignItems: 'center', gap: 6,
                    }}>
                      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                      </svg>
                      {[asset.unit, asset.base].filter(Boolean).join(' · ')}
                    </div>
                  )}

                  {/* Score bar */}
                  <div style={{ marginBottom: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5, fontSize: '0.6875rem', color: 'var(--muted)' }}>
                      <span>Readiness Score</span>
                      <span style={{ color: 'var(--primary)', fontWeight: 700 }}>{asset.overall_score}/100</span>
                    </div>
                    <ScoreBar score={asset.overall_score} status={asset.overall_status} />
                  </div>

                  {/* Footer */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 4 }}>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--muted)' }}>
                      Next mission:{' '}
                      <span style={{ color: 'var(--primary)' }}>{formatDate(asset.next_mission_window)}</span>
                    </div>
                    <span style={{ color: 'var(--accent)', fontSize: '0.6875rem', fontWeight: 600 }}>
                      Details →
                    </span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
