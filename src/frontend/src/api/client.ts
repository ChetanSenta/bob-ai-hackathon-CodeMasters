import axios from 'axios';
import type {
  FleetReadinessResponse,
  AssetDetailResponse,
  PredictionsResponse,
  MaintenancePlanResponse,
  IngestResponse,
} from '../types';

const BASE_URL = (import.meta as ImportMeta & { env: { VITE_API_URL?: string } }).env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({ baseURL: BASE_URL });

export const getFleetReadiness = (): Promise<{ data: FleetReadinessResponse }> =>
  api.get<FleetReadinessResponse>('/readiness/fleet');

export const getAssetDetail = (assetId: string): Promise<{ data: AssetDetailResponse }> =>
  api.get<AssetDetailResponse>(`/readiness/asset/${assetId}`);

export const getFailurePredictions = (): Promise<{ data: PredictionsResponse }> =>
  api.get<PredictionsResponse>('/predict/failures');

export const getMaintenancePlan = (): Promise<{ data: MaintenancePlanResponse }> =>
  api.get<MaintenancePlanResponse>('/maintenance/plan');

export const uploadSensorData = (file: File): Promise<{ data: IngestResponse }> => {
  const form = new FormData();
  form.append('file', file);
  return api.post<IngestResponse>('/ingest/sensors/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const uploadServiceRecords = (file: File): Promise<{ data: IngestResponse }> => {
  const form = new FormData();
  form.append('file', file);
  return api.post<IngestResponse>('/ingest/service-records/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
