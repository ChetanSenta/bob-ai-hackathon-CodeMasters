// ---------------------------------------------------------------------------
// Types matching src/backend/schemas.py exactly
// ---------------------------------------------------------------------------

// Readiness
export type ReadinessStatus = 'GREEN' | 'AMBER' | 'RED';
export type Urgency = 'CRITICAL' | 'HIGH' | 'MEDIUM';

export interface ComponentStatus {
  component: string;
  metric: string;
  value: number;
  status: ReadinessStatus;
  score: number;
}

export interface AssetReadinessSummary {
  asset_id: string;
  tail_number: string;
  platform: string;
  asset_type: string;
  unit?: string;
  base?: string;
  next_mission_window?: string;   // ISO datetime string from JSON
  overall_status: ReadinessStatus;
  overall_score: number;
  components: ComponentStatus[];
}

export interface FleetSummary {
  total: number;
  GREEN: number;
  AMBER: number;
  RED: number;
}

export interface FleetReadinessResponse {
  fleet: AssetReadinessSummary[];
  summary: FleetSummary;
}

export interface SensorReadingOut {
  reading_id: string;
  asset_id: string;
  tail_number?: string;
  timestamp: string;
  metric_name: string;
  value: number;
  unit?: string;
  component?: string;
}

export interface ServiceRecordOut {
  record_id: string;
  asset_id: string;
  tail_number?: string;
  component?: string;
  maintenance_type?: string;
  technician?: string;
  date?: string;
  notes?: string;
  outcome?: string;
}

export interface AssetDetailResponse {
  asset_id: string;
  tail_number: string;
  platform: string;
  asset_type: string;
  unit?: string;
  base?: string;
  next_mission_window?: string;
  overall_status: ReadinessStatus;
  overall_score: number;
  components: ComponentStatus[];
  recent_readings: SensorReadingOut[];
  service_history: ServiceRecordOut[];
  explanation: string;
}

// Predictions
export interface FailurePrediction {
  asset_id: string;
  tail_number: string;
  platform: string;
  component: string;
  metric: string;
  current_value: number;
  threshold_red?: number;
  urgency: Urgency;
  next_mission_window?: string;
  hours_until_mission?: number;
  recommendation: string;
}

export interface PredictionsResponse {
  predictions: FailurePrediction[];
}

// Maintenance plan
export interface MaintenanceTask {
  priority: number;
  asset_id: string;
  tail_number: string;
  platform: string;
  component: string;
  urgency: Urgency;
  action: string;
  estimated_duration_hours: number;
  next_mission_window?: string;
  hours_available?: number;
}

export interface MaintenancePlanResponse {
  plan: MaintenanceTask[];
}

// Ingest responses
export interface IngestResponse {
  ingested: number;
  errors: string[];
}
