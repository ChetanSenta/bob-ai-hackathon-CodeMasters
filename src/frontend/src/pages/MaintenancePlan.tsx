import { useEffect, useState } from 'react';
import { getMaintenancePlan } from '../api/client';
import type { MaintenancePlanResponse, MaintenanceTask, Urgency } from '../types';
import { UrgencyChip } from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

function formatDate(iso?: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

function TaskRow({ task }: { task: MaintenanceTask }) {
  const rowBg =
    task.urgency === 'CRITICAL' ? 'rgba(248,113,113,0.05)' :
    task.urgency === 'HIGH'     ? 'rgba(251,146,60,0.05)'  : 'transparent';

  const hoursWarning =
    task.hours_available !== undefined &&
    task.hours_available < task.estimated_duration_hours * 1.5;

  return (
    <tr style={{ backgroundColor: rowBg, borderBottom: '1px solid var(--border)' }}>
      {/* Priority */}
      <td style={{ padding: '11px 14px', textAlign: 'center' as const }}>
        <span style={{
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          width: 24, height: 24, borderRadius: '50%',
          background: task.urgency === 'CRITICAL' ? 'var(--red-dim)' : 'var(--card)',
          border: `1px solid ${task.urgency === 'CRITICAL' ? 'var(--red-border)' : 'var(--border)'}`,
          color: task.urgency === 'CRITICAL' ? 'var(--red)' : 'var(--muted)',
          fontWeight: 800, fontSize: '0.6875rem',
        }}>
          {task.priority}
        </span>
      </td>

      {/* Urgency */}
      <td style={{ padding: '11px 14px' }}>
        <UrgencyChip urgency={task.urgency as Urgency} />
      </td>

      {/* Asset */}
      <td style={{ padding: '11px 14px' }}>
        <span style={{ color: 'var(--primary)', fontWeight: 700, fontSize: '0.8125rem' }}>{task.tail_number}</span>
        <span style={{ color: 'var(--muted)', fontSize: '0.6875rem', display: 'block', marginTop: 2 }}>{task.platform}</span>
      </td>

      {/* Component */}
      <td style={{ padding: '11px 14px', color: 'var(--primary)', fontSize: '0.8125rem', textTransform: 'capitalize' as const }}>
        {task.component}
      </td>

      {/* Action */}
      <td style={{ padding: '11px 14px', color: 'var(--muted)', fontSize: '0.75rem', maxWidth: 260 }}>
        {task.action}
      </td>

      {/* Est. hours */}
      <td style={{ padding: '11px 14px', fontWeight: 700, fontSize: '0.8125rem', textAlign: 'right' as const }}>
        {task.estimated_duration_hours}h
      </td>

      {/* Hours available */}
      <td style={{
        padding: '11px 14px',
        color: hoursWarning ? 'var(--red)' : 'var(--muted)',
        fontSize: '0.8125rem',
        textAlign: 'right' as const,
        fontWeight: hoursWarning ? 700 : 400,
      }}>
        {task.hours_available !== undefined ? `${task.hours_available.toFixed(1)}h` : '—'}
      </td>

      {/* Mission window */}
      <td style={{ padding: '11px 14px', color: 'var(--muted)', fontSize: '0.6875rem', whiteSpace: 'nowrap' as const }}>
        {formatDate(task.next_mission_window)}
      </td>
    </tr>
  );
}

export default function MaintenancePlan() {
  const [data, setData] = useState<MaintenancePlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMaintenancePlan()
      .then(({ data }) => setData(data))
      .catch((e) => setError(e?.message ?? 'Failed to reach API'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Loading maintenance plan…" />;

  if (error) {
    return (
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 20px' }}>
        <div className="alert alert-error">
          ⚠ Could not load maintenance plan: {error}
          <p style={{ marginTop: 6, color: 'var(--muted)', fontSize: '0.75rem' }}>
            Ensure the backend is running at <code style={{ color: 'var(--accent)' }}>http://localhost:8000</code>
          </p>
        </div>
      </div>
    );
  }

  const plan = data?.plan ?? [];
  const totalCritical = plan.filter((t) => t.urgency === 'CRITICAL').length;
  const totalHours = plan.reduce((s, t) => s + t.estimated_duration_hours, 0);

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 20px' }} className="fade-in">

      {/* Header */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 28, gap: 16 }}>
        <div>
          <h1 className="page-title">Maintenance Plan</h1>
          <p style={{ color: 'var(--muted)', fontSize: '0.8125rem', marginTop: 4 }}>
            {new Date().toLocaleDateString('en-GB', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })}
          </p>
        </div>

        {/* Summary stat cards */}
        <div style={{ display: 'flex', gap: 10 }}>
          <div className="stat-card" style={{ borderColor: totalCritical > 0 ? 'var(--red-border)' : 'var(--border)' }}>
            <div className="stat-value" style={{ color: totalCritical > 0 ? 'var(--red)' : 'var(--muted)' }}>{totalCritical}</div>
            <div className="stat-label">Critical</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{totalHours.toFixed(1)}h</div>
            <div className="stat-label">Est. Total</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{plan.length}</div>
            <div className="stat-label">Tasks</div>
          </div>
        </div>
      </div>

      {/* Table / empty state */}
      {plan.length === 0 ? (
        <div className="alert alert-success" style={{ textAlign: 'center', padding: '28px 20px', fontSize: '0.9375rem' }}>
          ✅ All assets are mission-ready. No maintenance tasks required.
        </div>
      ) : (
        <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead style={{ background: 'var(--surface)' }}>
                <tr>
                  {[
                    { label: '#',            align: 'center' },
                    { label: 'Urgency',      align: 'left'   },
                    { label: 'Asset',        align: 'left'   },
                    { label: 'Component',    align: 'left'   },
                    { label: 'Action',       align: 'left'   },
                    { label: 'Est. Hrs',     align: 'right'  },
                    { label: 'Hrs Avail.',   align: 'right'  },
                    { label: 'Mission',      align: 'left'   },
                  ].map(({ label, align }) => (
                    <th key={label} style={{
                      padding: '10px 14px',
                      textAlign: align as 'left' | 'right' | 'center',
                      fontSize: '0.6875rem',
                      fontWeight: 700,
                      color: 'var(--muted)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.08em',
                      borderBottom: '1px solid var(--border)',
                      whiteSpace: 'nowrap',
                    }}>
                      {label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {plan.map((task) => (
                  <TaskRow key={`${task.asset_id}-${task.priority}`} task={task} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
