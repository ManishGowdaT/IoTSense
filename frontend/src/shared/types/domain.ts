/** Wire-level API enums. Keep these in sync with backend/openapi.yaml. */
export type SensorQuality = 'valid' | 'stale' | 'missing' | 'invalid' | 'warming_up' | 'uncalibrated';
export type DataSource = 'live_hardware' | 'simulation' | 'sample';
export type WashroomStatus = 'clean' | 'moderate' | 'dirty' | 'cleaning' | 'offline' | 'unknown';

export interface TelemetryObservationRequest {
  sensor_key: string;
  metric: 'temperature_c' | 'relative_humidity_pct' | 'pressure_pa' | 'gas_resistance_ohm' | 'analog_raw' | 'pin_voltage_v' | 'relative_index';
  value: number;
  unit: string;
  quality?: SensorQuality;
  metadata?: Record<string, unknown>;
}

export interface TelemetryRequest {
  device_id?: string;
  sequence: number;
  observed_at: string;
  firmware_version: string;
  observations: TelemetryObservationRequest[];
}

export interface TelemetryReceipt {
  telemetry_event_id: string;
  device_id: string;
  sequence: number;
  received_at: string;
  source_mode: DataSource;
  duplicate: boolean;
}

export interface HygieneScore {
  value: number | null;
  classification: WashroomStatus;
  algorithm_version: string;
  calculated_at: string;
  quality: SensorQuality;
  source_mode: DataSource;
  explanation: string[];
}

export interface WashroomSummary {
  id: string;
  name: string;
  facility_id: string;
  facility_name?: string;
  status: WashroomStatus;
  score: HygieneScore | null;
  last_telemetry_at: string | null;
  active_alert_count: number;
  device_online: boolean;
}

export interface DashboardSummary {
  generated_at: string;
  source_state: 'live_hardware' | 'simulation' | 'mixed' | 'stale' | 'unavailable';
  washroom_count: number;
  active_alert_count: number;
  washrooms: WashroomSummary[];
}

export interface PaginatedResponse<T> {
  items: T[];
  page: number;
  page_size: number;
  total?: number;
  has_more: boolean;
}
