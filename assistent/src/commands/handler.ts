import { parseCommand, ParsedCommand } from './parser.js';
import { handleScheduleEvent, handleListCalendar, handleTomorrowPreview } from './calendar.js';
import { handleEmailBrief } from './email.js';
import { handleSetReminder, handleListReminders } from './reminder.js';

export async function handleCommand(chatId: string, commandText: string): Promise<string> {
  console.log(`Processing command: "${commandText}"`);

  // Parse the command using AI
  const parsed = await parseCommand(commandText);
  console.log(`Parsed command type: ${parsed.type}`);

  // Route to appropriate handler
  switch (parsed.type) {
    case 'schedule_event':
      return handleScheduleEvent(parsed);

    case 'list_calendar':
      return handleListCalendar(parsed);

    case 'tomorrow_preview':
      return handleTomorrowPreview(parsed);

    case 'email_brief':
      return handleEmailBrief(parsed);

    case 'set_reminder':
      return handleSetReminder(parsed, chatId);

    case 'list_reminders':
      return handleListReminders(parsed);

    case 'unknown':
    default:
      return getHelpMessage();
  }
}

function getHelpMessage(): string {
  return `🤖 *WhatsApp Assistant*

I can help you with:

📅 *Calendar*
• "What's on my calendar today"
• "What's tomorrow"
• "Schedule meeting tomorrow at 10am"

📧 *Email*
• "Email brief"

⏰ *Reminders*
• "Remind me to call mom in 2 hours"
• "List reminders"

Just start your message with *Assist* followed by your command!`;
}
