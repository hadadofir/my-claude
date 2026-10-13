import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';
import { sendOpportunisticNotification } from './notifications';
import { ShoppingList } from './shopping';

export const GEOFENCE_TASK = 'TASKER_GEOFENCE';

export interface GeofenceRegion {
  identifier: string;
  latitude: number;
  longitude: number;
  radius: number;
  listId: string;
  listName: string;
  storeName: string;
}

// Background task definition — must be at module top level
TaskManager.defineTask(GEOFENCE_TASK, ({ data, error }: { data: any; error: any }) => {
  if (error) {
    console.error('Geofence task error:', error);
    return;
  }
  if (data) {
    const { eventType, region } = data;
    if (eventType === Location.GeofencingEventType.Enter) {
      const [, listName, storeName, itemCountStr] = region.identifier.split('|');
      const itemCount = parseInt(itemCountStr ?? '1', 10);
      sendOpportunisticNotification(listName, itemCount, storeName);
    }
  }
});

export async function requestLocationPermissions(): Promise<boolean> {
  const { status: fg } = await Location.requestForegroundPermissionsAsync();
  if (fg !== 'granted') return false;
  const { status: bg } = await Location.requestBackgroundPermissionsAsync();
  return bg === 'granted';
}

export async function startGeofencing(regions: GeofenceRegion[], itemCounts: Record<string, number>): Promise<void> {
  const hasPerms = await requestLocationPermissions();
  if (!hasPerms) return;

  const locationRegions = regions.map((r) => ({
    identifier: `${r.identifier}|${r.listName}|${r.storeName}|${itemCounts[r.listId] ?? 0}`,
    latitude: r.latitude,
    longitude: r.longitude,
    radius: r.radius,
    notifyOnEnter: true,
    notifyOnExit: false,
  }));

  await Location.startGeofencingAsync(GEOFENCE_TASK, locationRegions);
}

export async function stopGeofencing(): Promise<void> {
  const isRegistered = await TaskManager.isTaskRegisteredAsync(GEOFENCE_TASK);
  if (isRegistered) {
    await Location.stopGeofencingAsync(GEOFENCE_TASK);
  }
}

export async function refreshGeofences(lists: ShoppingList[], itemCounts: Record<string, number>): Promise<void> {
  await stopGeofencing();
  const regions: GeofenceRegion[] = lists
    .filter((l) => l.locationLat && l.locationLng && (itemCounts[l.id] ?? 0) > 0)
    .map((l) => ({
      identifier: l.id,
      latitude: l.locationLat!,
      longitude: l.locationLng!,
      radius: l.locationRadius ?? 300,
      listId: l.id,
      listName: l.name,
      storeName: l.locationName ?? l.name,
    }));

  if (regions.length > 0) {
    await startGeofencing(regions, itemCounts);
  }
}
