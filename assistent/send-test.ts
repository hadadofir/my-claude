import { config } from './src/config.js';
import { getTodayEvents, getTomorrowEvents, formatEventsForDisplay } from './src/services/google-calendar.js';
import { sendMessageToPhone } from './src/whatsapp/client.js';

async function sendCalendarTest() {
  console.log('Sending calendar test to WhatsApp...');

  try {
    const todayEvents = await getTodayEvents();
    const tomorrowEvents = await getTomorrowEvents();

    const today = new Date().toLocaleDateString('he-IL', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
    });

    const tomorrow = new Date(Date.now() + 86400000).toLocaleDateString('he-IL', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
    });

    let message = `🧪 *Calendar Test*\n\n`;
    message += `📅 *Today (${today})*\n`;
    message += formatEventsForDisplay(todayEvents) || 'No events';
    message += `\n\n📅 *Tomorrow (${tomorrow})*\n`;
    message += formatEventsForDisplay(tomorrowEvents) || 'No events';
    message += `\n\n✅ Assistant is ready!`;

    await sendMessageToPhone(config.whatsappPhone, message);
    console.log('Test message sent!');
  } catch (error) {
    console.error('Failed:', error);
  }
}

sendCalendarTest();
