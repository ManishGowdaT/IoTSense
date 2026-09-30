function readEnv(value: string | undefined, fallback: string): string {
  return value?.trim() || fallback;
}

export const appConfig = {
  apiBaseUrl: readEnv(import.meta.env.VITE_API_BASE_URL, '/api/v1'),
  dataMode: readEnv(import.meta.env.VITE_DATA_MODE, 'sample'),
  appName: readEnv(import.meta.env.VITE_APP_NAME, 'IoTSense'),
} as const;

export type DataMode = 'live' | 'simulation' | 'sample';
