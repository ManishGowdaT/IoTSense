export type ScreenId =
  | 'landing' | 'login' | 'forgot' | 'dashboard' | 'washrooms'
  | 'washroom-detail' | 'sensor' | 'analysis' | 'causes' | 'analytics'
  | 'alerts' | 'cleaning' | 'verification' | 'devices' | 'provision'
  | 'users' | 'settings' | 'audit' | 'health' | 'profile';

export const routeByScreen: Record<ScreenId, string> = {
  landing: '/',
  login: '/login',
  forgot: '/forgot-password',
  dashboard: '/app/dashboard',
  washrooms: '/app/washrooms',
  'washroom-detail': '/app/washrooms/north-wing-washroom-1',
  sensor: '/app/sensors/mq135-sample',
  analysis: '/app/hygiene-analysis',
  causes: '/app/cause-identification',
  analytics: '/app/analytics',
  alerts: '/app/alerts',
  cleaning: '/app/cleaning',
  verification: '/app/cleaning/CLN-2038',
  devices: '/app/devices',
  provision: '/app/devices/provision',
  users: '/app/users',
  settings: '/app/settings',
  audit: '/app/audit-logs',
  health: '/app/system-health',
  profile: '/app/profile',
};

const screenByRoute = new Map(Object.entries(routeByScreen).map(([screen, path]) => [path, screen as ScreenId]));

export function screenFromPath(pathname: string): ScreenId {
  return screenByRoute.get(pathname.replace(/\/$/, '') || '/') ?? 'dashboard';
}

export function isKnownPath(pathname: string): boolean {
  return screenByRoute.has(pathname.replace(/\/$/, '') || '/');
}
