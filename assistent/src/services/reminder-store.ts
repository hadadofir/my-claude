import * as fs from 'fs';
import * as path from 'path';
import { config } from '../config.js';

export interface Reminder {
  id: string;
  message: string;
  triggerAt: Date;
  chatId: string;
  createdAt: Date;
  triggered: boolean;
}

interface ReminderStore {
  reminders: Reminder[];
}

function ensureStoreDirectory(): void {
  const dir = path.dirname(config.reminderStorePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function loadStore(): ReminderStore {
  ensureStoreDirectory();

  if (!fs.existsSync(config.reminderStorePath)) {
    return { reminders: [] };
  }

  try {
    const data = fs.readFileSync(config.reminderStorePath, 'utf-8');
    const store = JSON.parse(data);

    // Convert date strings back to Date objects
    store.reminders = store.reminders.map((r: any) => ({
      ...r,
      triggerAt: new Date(r.triggerAt),
      createdAt: new Date(r.createdAt),
    }));

    return store;
  } catch (error) {
    console.error('Failed to load reminder store:', error);
    return { reminders: [] };
  }
}

function saveStore(store: ReminderStore): void {
  ensureStoreDirectory();
  fs.writeFileSync(config.reminderStorePath, JSON.stringify(store, null, 2));
}

function generateId(): string {
  return `rem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export function addReminder(message: string, triggerAt: Date, chatId: string): Reminder {
  const store = loadStore();

  const reminder: Reminder = {
    id: generateId(),
    message,
    triggerAt,
    chatId,
    createdAt: new Date(),
    triggered: false,
  };

  store.reminders.push(reminder);
  saveStore(store);

  console.log(`Reminder added: "${message}" at ${triggerAt.toISOString()}`);
  return reminder;
}

export function getActiveReminders(): Reminder[] {
  const store = loadStore();
  return store.reminders.filter(r => !r.triggered);
}

export function getDueReminders(): Reminder[] {
  const store = loadStore();
  const now = new Date();

  return store.reminders.filter(r => !r.triggered && r.triggerAt <= now);
}

export function markReminderTriggered(id: string): void {
  const store = loadStore();

  const reminder = store.reminders.find(r => r.id === id);
  if (reminder) {
    reminder.triggered = true;
    saveStore(store);
    console.log(`Reminder marked as triggered: ${id}`);
  }
}

export function deleteReminder(id: string): boolean {
  const store = loadStore();

  const index = store.reminders.findIndex(r => r.id === id);
  if (index !== -1) {
    store.reminders.splice(index, 1);
    saveStore(store);
    console.log(`Reminder deleted: ${id}`);
    return true;
  }

  return false;
}

export function formatRemindersForDisplay(reminders: Reminder[]): string {
  if (reminders.length === 0) {
    return 'No active reminders.';
  }

  const lines = reminders.map(r => {
    const timeStr = r.triggerAt.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
    return `• ${timeStr}: ${r.message}`;
  });

  return `🔔 *Active Reminders*\n\n${lines.join('\n')}`;
}
