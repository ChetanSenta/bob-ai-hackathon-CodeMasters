import { useRef, useState } from 'react';
import { uploadSensorData, uploadServiceRecords } from '../api/client';
import type { IngestResponse } from '../types';

interface UploadZoneProps {
  title: string;
  icon: string;
  description: string;
  columns: string;
  onUpload: (file: File) => Promise<{ data: IngestResponse }>;
}

function UploadZone({ title, icon, description, columns, onUpload }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ ok: true; ingested: number } | { ok: false; message: string } | null>(null);
  const [dragging, setDragging] = useState(false);

  function handleFileChange(f: File) { setFile(f); setResult(null); }

  async function handleUpload() {
    if (!file) return;
    setLoading(true);
    setResult(null);
    try {
      const { data } = await onUpload(file);
      setResult({ ok: true, ingested: data.ingested });
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { detail?: string } }; message?: string })
          ?.response?.data?.detail ??
        (e as { message?: string })?.message ?? 'Upload failed';
      setResult({ ok: false, message: msg });
    } finally {
      setLoading(false);
    }
  }

  function onDrop(ev: React.DragEvent) {
    ev.preventDefault();
    setDragging(false);
    const f = ev.dataTransfer.files?.[0];
    if (f) handleFileChange(f);
  }

  return (
    <div style={{
      background: 'var(--card)',
      border: '1px solid var(--border)',
      borderRadius: 10,
      padding: '24px',
      flex: '1 1 300px',
      display: 'flex',
      flexDirection: 'column',
      gap: 16,
    }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 22 }}>{icon}</span>
        <div>
          <h3 style={{ color: 'var(--primary)', fontWeight: 700, fontSize: '0.9375rem', margin: 0 }}>{title}</h3>
          <p style={{ color: 'var(--muted)', fontSize: '0.6875rem', margin: '2px 0 0' }}>{description}</p>
        </div>
      </div>

      {/* Columns reference */}
      <div style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 6,
        padding: '8px 12px',
        fontSize: '0.6875rem',
        color: 'var(--muted)',
        fontFamily: 'monospace',
        lineHeight: 1.6,
      }}>
        {columns}
      </div>

      {/* Drop zone */}
      <div
        className={`drop-zone${dragging ? ' dragging' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          style={{ display: 'none' }}
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFileChange(f); }}
        />
        <div style={{ fontSize: 28, marginBottom: 8 }}>
          {file ? '📄' : '📂'}
        </div>
        <div style={{ fontSize: '0.8125rem' }}>
          {file ? (
            <span style={{ color: 'var(--green)', fontWeight: 600 }}>{file.name}</span>
          ) : (
            <span style={{ color: 'var(--muted)' }}>Drop CSV here or <span style={{ color: 'var(--accent)', fontWeight: 600 }}>click to browse</span></span>
          )}
        </div>
        {file && (
          <div style={{ color: 'var(--muted)', fontSize: '0.6875rem', marginTop: 4 }}>
            {(file.size / 1024).toFixed(1)} KB
          </div>
        )}
      </div>

      {/* Upload button */}
      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="btn"
        style={{
          width: '100%',
          justifyContent: 'center',
          background: file && !loading ? 'var(--accent)' : 'var(--surface)',
          color: file && !loading ? '#020d18' : 'var(--muted)',
          border: `1px solid ${file && !loading ? 'var(--accent)' : 'var(--border)'}`,
          fontWeight: 700,
        }}
      >
        {loading ? (
          <>
            <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <circle cx="12" cy="12" r="10" strokeOpacity=".25"/>
              <path d="M12 2a10 10 0 0 1 10 10" strokeLinecap="round"/>
            </svg>
            Uploading…
          </>
        ) : 'Upload'}
      </button>

      {/* Feedback */}
      {result && (
        <div className={`alert ${result.ok ? 'alert-success' : 'alert-error'}`}>
          {result.ok
            ? `✅ Ingested ${result.ingested} reading${result.ingested !== 1 ? 's' : ''}`
            : `❌ ${result.message}`}
        </div>
      )}
    </div>
  );
}

export default function DataUpload() {
  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px 20px' }} className="fade-in">
      <h1 className="page-title">Data Upload</h1>
      <p style={{ color: 'var(--muted)', fontSize: '0.8125rem', marginTop: 6, marginBottom: 28 }}>
        Upload HUMS sensor telemetry and service records to populate the readiness database.
      </p>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20 }}>
        <UploadZone
          title="Sensor Data (HUMS)"
          icon="📡"
          description="Upload HUMS telemetry CSV"
          columns="reading_id · asset_id · tail_number · timestamp · metric_name · value · unit · component"
          onUpload={uploadSensorData}
        />
        <UploadZone
          title="Service Records"
          icon="🔧"
          description="Upload maintenance history CSV"
          columns="record_id · asset_id · component · maintenance_type · technician · date · notes · outcome"
          onUpload={uploadServiceRecords}
        />
      </div>

      {/* Info banner */}
      <div className="alert alert-info" style={{ marginTop: 28 }}>
        <strong style={{ color: 'var(--primary)' }}>ℹ Sample data pre-loaded</strong>
        <p style={{ marginTop: 4, lineHeight: 1.5 }}>
          The initial dataset (25 assets · 600 sensor readings · 65 service records) is seeded automatically
          via <code style={{ color: 'var(--accent)', fontFamily: 'monospace' }}>db_init.py</code> when the backend starts.
          Use the upload zones above to ingest additional data.
        </p>
        <p style={{ marginTop: 6, fontSize: '0.6875rem', color: 'var(--muted)' }}>
          Sample files are in <code style={{ fontFamily: 'monospace' }}>src/data/</code> — you can upload them directly to reload the baseline dataset.
        </p>
      </div>
    </div>
  );
}
