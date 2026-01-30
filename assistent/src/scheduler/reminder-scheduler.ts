import cron from 'node-cron';
import { getDueReminders, markReminderTriggered } from '../services/reminder-store.js';
import { sendMessage } from '../whatsapp/client.js';

export async function checkAndTriggerReminders(): Promise<void> {
  const dueReminders = getDueReminders();

  for (const reminder of dueReminders) {
    try {
      const message = `🔔 *Reminder*\n\n${reminder.message}`;
      await sendMessage(reminder.chatId, message);
      markReminderTriggered(reminder.id);
      console.log(`Reminder triggered: ${reminder.message}`);
    } catch (error) {
      console.error(`Failed to trigger reminder ${reminder.id}:`, error);
    }
  }
}

export function startReminderScheduler(): void {
  console.log('Reminder scheduler started: checking every minute');

  // Check every minute for due reminders
  cron.schedule('* * * * *', () => {
    checkAndTriggerReminders();
  });

  // Also run immediately on start
  checkAndTriggerReminders();
}
