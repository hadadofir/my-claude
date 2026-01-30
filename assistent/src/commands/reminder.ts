import {
  addReminder,
  getActiveReminders,
  formatRemindersForDisplay,
} from '../services/reminder-store.js';
import { ParsedCommand } from './parser.js';

export async function handleSetReminder(command: ParsedCommand, chatId: string): Promise<string> {
  const params = command.params;

  if (!params.message) {
    return 'What should I remind you about?';
  }

  if (!params.triggerAt) {
    return 'When should I remind you? Please specify a time.';
  }

  try {
    const triggerAt = new Date(params.triggerAt);

    if (triggerAt <= new Date()) {
      return 'That time has already passed. Please specify a future time.';
    }

    const reminder = addReminder(params.message, triggerAt, chatId);

    const timeStr = triggerAt.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

    return `⏰ Reminder set!\n\n*${reminder.message}*\n📅 ${timeStr}`;
  } catch (error) {
    console.error('Failed to set reminder:', error);
    return 'Sorry, I could not set the reminder. Please try again.';
  }
}

export async function handleListReminders(command: ParsedCommand): Promise<string> {
  try {
    const reminders = getActiveReminders();
    return formatRemindersForDisplay(reminders);
  } catch (error) {
    console.error('Failed to list reminders:', error);
    return 'Sorry, I could not fetch your reminders.';
  }
}
