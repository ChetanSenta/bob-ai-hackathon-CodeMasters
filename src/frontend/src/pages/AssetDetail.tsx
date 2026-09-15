import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getAssetDetail } from '../api/client';
import type { AssetDetailResponse, ReadinessStatus } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

function formatDate(iso?: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
  });
}

function rowTint(status: ReadinessStatus): string {
  if (status === 'RED')   return 'rgba(248,113,113,0.06)';
  if (status === 'AMBER') return 'rgba(251,191,36,0.05)';
  return 'transparent';
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{
      background: 'var(--card)',
      border: '1px solid var(--border)',
      borderRadius: 10,
      marginBottom: 20,
      overflow: 'hidden',
    }}>
      <div style={{
        padding: '12px 18px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        background: 'var(--surface)',
      }}>
        <h2 style={{ color: 'var(--primary)', fontSize: '0.875rem', fontWeight: 700, margin: 0 }}>
          {title}
        </h2>
      </div>
      {children}
    </div>
  );
}

export default function AssetDetail() {
  const { asset_id } = useParams<{ asset_id: string }>();
  const [data, setData] = useState<AssetDetailResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!asset_id) return;
    getAssetDetail(asset_id)
      .then(({ data }) => setData(data))
      .catch((e) => setError(e?.message ?? 'Failed to reach API'))
      .finally(() => setLoading(false));
  }, [asset_id]);

  if (loading) return <LoadingSpinner label="Loading asset detail…" />;

  if (error || !data) {
    return (
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px 20px' }}>
        <Link to="/" style={{ color: 'var(--accent)', fontSize: '0.8125rem', textDecoration: 'none' }}>← Fleet Overview</Link>
        <div className="alert alert-error" style={{ marginTop: 16 }}>
          ⚠ {error ?? 'Asset not found'}
        </div>
      </div>
    );
  }

  const scoreColor =
    data.overall_status === 'RED'   ? 'var(--red)'   :
    data.overall_status === 'AMBER' ? 'var(--amber)' : 'var(--green)';

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px 20px' }} className="fade-in">

      {/* Back link */}
      <Link to="/" style={{ color: 'var(--accent)', fontSize: '0.8125rem', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 5 }}>
        ← Fleet Overview
      </Link>

      {/* Asset header card */}
      <div style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        borderRadius: 10,
        padding: '22px 24px',
        marginTop: 14,
        marginBottom: 20,
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: 20,
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
            <h1 style={{ color: 'var(--primary)', fontSize: '1.75rem', fontWeight: 800, margin: 0, letterSpacing: '-0.02em' }}>
              {data.tail_number}
            </h1>
            <StatusBadge status={data.overall_status} size="lg" />
          </div>
          <p style={{ color: 'var(--muted)', fontSize: '0.875rem', margin: '0 0 6px' }}>
            {data.platform}
            {data.asset_type && <span> · {data.asset_type}</span>}
            {data.unit && <span> · {data.unit}</span>}
            {data.base && <span> · {data.base}</span>}
          </p>
          <p style={{ color: 'var(--muted)', fontSize: '0.75rem', margin: 0 }}>
            Next mission window:{' '}
            <span style={{ color: 'var(--primary)' }}>{formatDate(data.next_mission_window)}</span>
          </p>
        </div>

        {/* Score gauge */}
        <div style={{ textAlign: 'center', minWidth: 80 }}>
          <div style={{ fontSize: '2.25rem', fontWeight: 800, color: scoreColor, lineHeight: 1 }}>
            {data.overall_score}
          </div>
          <div style={{ fontSize: '0.625rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--muted)', marginTop: 4 }}>
            Score / 100
          </div>
        </div>
      </div>

      {/* Component breakdown */}
      <SectionCard title="Component Breakdown">
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                {['Component', 'Metric', 'Value', 'Status', 'Score'].map((h) => (
                  <th key={h}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.components.map((c, i) => (
                <tr key={i} style={{ backgroundColor: rowTint(c.status as ReadinessStatus) }}>
                  <td style={{ fontWeight: 600, textTransform: 'capitalize' }}>{c.component}</td>
                  <td style={{ color: 'var(--muted)', fontFamily: 'monospace', fontSize: '0.75rem' }}>{c.metric}</td>
                  <td style={{ fontWeight: 700, fontFamily: 'monospace' }}>{c.value}</td>
                  <td><StatusBadge status={c.status as ReadinessStatus} size="sm" /></td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div className="score-track" style={{ width: 60 }}>
                        <div className="score-fill" style={{
                          width: `${c.score}%`,
                          background: c.status === 'GREEN' ? 'var(--green)' : c.status === 'AMBER' ? 'var(--amber)' : 'var(--red)',
                        }} />
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>{c.score}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>

      {/* Readiness assessment */}
      {data.explanation && (
        <SectionCard title="Readiness Assessment">
          <blockquote className="assessment-quote">{data.explanation}</blockquote>
        </SectionCard>
      )}

      {/* Recent readings */}
      <SectionCard title="Recent Sensor Readings">
        <div style={{ overflowX: 'auto' }}>
          {data.recent_readings.length === 0 ? (
            <p style={{ color: 'var(--muted)', padding: '16px 18px', fontSize: '0.8125rem' }}>No readings available.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  {['Timestamp', 'Component', 'Metric', 'Value', 'Unit'].map((h) => (
                    <th key={h}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.recent_readings.slice(0, 10).map((r, i) => (
                  <tr key={i}>
                    <td style={{ color: 'var(--muted)', whiteSpace: 'nowrap', fontFamily: 'monospace', fontSize: '0.75rem' }}>{formatDate(r.timestamp)}</td>
                    <td style={{ textTransform: 'capitalize' }}>{r.component ?? '—'}</td>
                    <td style={{ color: 'var(--muted)', fontFamily: 'monospace', fontSize: '0.75rem' }}>{r.metric_name}</td>
                    <td style={{ fontWeight: 600, fontFamily: 'monospace' }}>{r.value}</td>
                    <td style={{ color: 'var(--muted)' }}>{r.unit ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </SectionCard>

      {/* Service history */}
      <SectionCard title="Service History">
        <div style={{ overflowX: 'auto' }}>
          {data.service_history.length === 0 ? (
            <p style={{ color: 'var(--muted)', padding: '16px 18px', fontSize: '0.8125rem' }}>No service records found.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  {['Date', 'Component', 'Type', 'Technician', 'Notes', 'Outcome'].map((h) => (
                    <th key={h}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.service_history.map((r, i) => {
                  const isGood = ['completed', 'pass', 'ok'].some(k => r.outcome?.toLowerCase().includes(k));
                  const isDeferred = r.outcome?.toLowerCase().includes('deferred');
                  const outcomeColor = isGood ? 'var(--green)' : isDeferred ? 'var(--red)' : 'var(--amber)';
                  const outcomeBg   = isGood ? 'var(--green-dim)' : isDeferred ? 'var(--red-dim)' : 'var(--amber-dim)';
                  const outcomeBdr  = isGood ? 'var(--green-border)' : isDeferred ? 'var(--red-border)' : 'var(--amber-border)';
                  return (
                    <tr key={i}>
                      <td style={{ color: 'var(--muted)', whiteSpace: 'nowrap', fontFamily: 'monospace', fontSize: '0.75rem' }}>{r.date ?? '—'}</td>
                      <td style={{ textTransform: 'capitalize' }}>{r.component ?? '—'}</td>
                      <td style={{ color: 'var(--muted)', fontSize: '0.75rem' }}>{r.maintenance_type ?? '—'}</td>
                      <td>{r.technician ?? '—'}</td>
                      <td style={{ color: 'var(--muted)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: '0.75rem' }}>
                        {r.notes ?? '—'}
                      </td>
                      <td>
                        {r.outcome ? (
                          <span style={{
                            background: outcomeBg,
                            color: outcomeColor,
                            border: `1px solid ${outcomeBdr}`,
                            borderRadius: 4,
                            padding: '2px 8px',
                            fontSize: '0.6875rem',
                            fontWeight: 700,
                            textTransform: 'capitalize',
                          }}>
                            {r.outcome}
                          </span>
                        ) : '—'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </SectionCard>
    </div>
  );
}
