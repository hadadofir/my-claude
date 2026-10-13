import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) return null;

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') return null;

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'Default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
    });
    await Notifications.setNotificationChannelAsync('location', {
      name: 'Location Reminders',
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 500],
    });
  }

  const token = (await Notifications.getExpoPushTokenAsync()).data;
  return token;
}

export async function scheduleTaskReminder(taskTitle: string, dueDate: Date): Promise<string> {
  const trigger = new Date(dueDate);
  trigger.setHours(trigger.getHours() - 1);

  return Notifications.scheduleNotificationAsync({
    content: {
      title: 'Task reminder',
      body: `"${taskTitle}" is due in 1 hour`,
      sound: true,
    },
    trigger,
  });
}

export async function sendOpportunisticNotification(listName: string, itemCount: number, storeName: string): Promise<void> {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: `You're near ${storeName}!`,
      body: `You have ${itemCount} item${itemCount !== 1 ? 's' : ''} on your "${listName}" list`,
      sound: true,
      data: { type: 'opportunistic', storeName },
    },
    trigger: null,
  });
}

export async function cancelNotification(id: string): Promise<void> {
  await Notifications.cancelScheduledNotificationAsync(id);
}

export async function cancelAllNotifications(): Promise<void> {
  await Notifications.cancelAllScheduledNotificationsAsync();
}
