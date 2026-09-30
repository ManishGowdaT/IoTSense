import type { ScreenId } from './routes';

export type UserRole = 'Super Admin' | 'Facility Admin' | 'Maintenance Staff' | 'Viewer';

const publicScreens: ScreenId[] = ['landing', 'login', 'forgot'];
const adminOnly: ScreenId[] = ['provision', 'users', 'settings', 'audit', 'health'];

/** Frontend navigation hint only. The API must enforce all authorization decisions. */
export function canAccessScreen(screen: ScreenId, role: UserRole): boolean {
  if (publicScreens.includes(screen)) return true;
  if (role === 'Super Admin' || role === 'Facility Admin') return true;
  if (role === 'Maintenance Staff' || role === 'Viewer') return !adminOnly.includes(screen);
  return false;
}

export function visibleScreens<T extends { id: ScreenId }>(screens: T[], role: UserRole): T[] {
  return screens.filter(({ id }) => canAccessScreen(id, role));
}
