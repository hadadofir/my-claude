import { config } from '../config.js';

export type CommandType =
  | 'schedule_event'
  | 'list_calendar'
  | 'tomorrow_preview'
  | 'email_brief'
  | 'set_reminder'
  | 'list_reminders'
  | 'unknown';

export interface ParsedCommand {
  type: CommandType;
  params: Record<string, any>;
  originalText: string;
}

export interface ScheduleEventParams {
  title: string;
  date: string;
  time?: string;
  duration?: number;
  attendees?: string[];
  description?: string;
}

export interface ListCalendarParams {
  date: string;
}

export interface SetReminderParams {
  message: string;
  triggerAt: string;
}

// Simple regex-based command parser (no AI needed)
export async function parseCommand(text: string): Promise<ParsedCommand> {
  const lowerText = text.toLowerCase().trim();

  // List calendar today
  if (lowerText.match(/calendar.*today|today.*calendar|what'?s.*today|מה.*היום/i)) {
    return {
      type: 'list_calendar',
      params: { date: new Date().toISOString().split('T')[0] },
      originalText: text,
    };
  }

  // Tomorrow preview
  if (lowerText.match(/tomorrow|what'?s.*tomorrow|מה.*מחר|מחר/i)) {
    return {
      type: 'tomorrow_preview',
      params: {},
      originalText: text,
    };
  }

  // Email brief
  if (lowerText.match(/email|mail|brief|אימייל|מייל/i)) {
    return {
      type: 'email_brief',
      params: {},
      originalText: text,
    };
  }

  // List reminders
  if (lowerText.match(/list.*reminder|show.*reminder|reminders|תזכורות/i)) {
    return {
      type: 'list_reminders',
      params: {},
      originalText: text,
    };
  }

  // Set reminder - "remind me to X in Y minutes/hours"
  const reminderMatch = text.match(/remind.*?(?:me\s+)?(?:to\s+)?(.+?)\s+in\s+(\d+)\s*(minute|hour|min|hr|שעה|דקה)/i);
  if (reminderMatch) {
    const message = reminderMatch[1].trim();
    const amount = parseInt(reminderMatch[2], 10);
    const unit = reminderMatch[3].toLowerCase();

    const now = new Date();
    if (unit.includes('hour') || unit.includes('hr') || unit.includes('שעה')) {
      now.setHours(now.getHours() + amount);
    } else {
      now.setMinutes(now.getMinutes() + amount);
    }

    return {
      type: 'set_reminder',
      params: {
        message: message,
        triggerAt: now.toISOString(),
      },
      originalText: text,
    };
  }

  // Schedule event - "schedule X tomorrow/today at Y"
  const scheduleMatch = text.match(/schedule\s+(.+?)\s+(tomorrow|today|מחר|היום)\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?/i);
  if (scheduleMatch) {
    const title = scheduleMatch[1].trim();
    const dayWord = scheduleMatch[2].toLowerCase();
    let hours = parseInt(scheduleMatch[3], 10);
    const minutes = scheduleMatch[4] ? parseInt(scheduleMatch[4], 10) : 0;
    const ampm = scheduleMatch[5]?.toLowerCase();

    if (ampm === 'pm' && hours < 12) hours += 12;
    if (ampm === 'am' && hours === 12) hours = 0;

    const date = new Date();
    if (dayWord === 'tomorrow' || dayWord === 'מחר') {
      date.setDate(date.getDate() + 1);
    }

    return {
      type: 'schedule_event',
      params: {
        title: title,
        date: date.toISOString().split('T')[0],
        time: `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`,
        duration: 60,
      },
      originalText: text,
    };
  }

  return {
    type: 'unknown',
    params: {},
    originalText: text,
  };
}
