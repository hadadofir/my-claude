import cron from 'node-cron';
import { getTomorrowEvents, formatEventsForDisplay } from '../services/google-calendar.js';
import { getActiveReminders, formatRemindersForDisplay } from '../services/reminder-store.js';
import { sendMessage, sendMessageToPhone } from '../whatsapp/client.js';
import { getTargetGroupChatId } from '../whatsapp/target-group.js';
import { config } from '../config.js';

export async function generateDailyBrief(): Promise<string> {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);

  const dateStr = tomorrow.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  let brief = `📅 *Daily Brief for ${dateStr}*\n\n`;

  // Get tomorrow's events
  try {
    const events = await getTomorrowEvents();
    if (events.length > 0) {
      brief += `*Tomorrow's Schedule:*\n${formatEventsForDisplay(events)}\n\n`;
    } else {
      brief += `*Tomorrow's Schedule:*\nNo events scheduled.\n\n`;
    }
  } catch (error) {
    console.error('Failed to get calendar events for daily brief:', error);
    brief += `*Tomorrow's Schedule:*\nUnable to fetch calendar.\n\n`;
  }

  // Get active reminders
  const reminders = getActiveReminders();
  const upcomingReminders = reminders.filter(r => {
    const reminderDate = new Date(r.triggerAt);
    const in24Hours = new Date();
    in24Hours.setHours(in24Hours.getHours() + 24);
    return reminderDate <= in24Hours;
  });

  if (upcomingReminders.length > 0) {
    brief += `*Upcoming Reminders:*\n`;
    upcomingReminders.forEach(r => {
      const timeStr = r.triggerAt.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
      });
      brief += `• ${timeStr}: ${r.message}\n`;
    });
  }

  brief += `\nHave a great evening! 🌙`;

  return brief;
}

export async function sendDailyBrief(): Promise<void> {
  console.log('Sending daily brief...');

  try {
    const brief = await generateDailyBrief();
    // Send to self-chat
    await sendMessageToPhone(config.whatsappPhone, brief);
    console.log('Daily brief sent successfully');
  } catch (error) {
    console.error('Failed to send daily brief:', error);
  }
}

export function startDailyBriefScheduler(): void {
  const hour = config.dailyBriefHour;
  const minute = config.dailyBriefMinute;

  const cronExpression = `${minute} ${hour} * * *`;

  console.log(`Daily brief scheduler started: ${hour}:${minute.toString().padStart(2, '0')} every day`);

  cron.schedule(cronExpression, () => {
    sendDailyBrief();
  });
}

// For manual testing
export async function testDailyBrief(): Promise<void> {
  console.log('Testing daily brief generation...');
  const brief = await generateDailyBrief();
  console.log('Generated brief:');
  console.log(brief);
}
