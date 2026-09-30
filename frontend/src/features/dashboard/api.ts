import { requestJson } from '../../shared/api/http';
import type { DashboardSummary } from '../../shared/types/domain';

/** Connected to the backend in a later integration phase; sample mode remains the current source. */
export function fetchDashboard(signal?: AbortSignal): Promise<DashboardSummary> {
  return requestJson<DashboardSummary>('/dashboard', { signal });
}
