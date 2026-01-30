import {
  createEvent,
  listEvents,
  getTodayEvents,
  getTomorrowEvents,
  formatEventsForDisplay,
  CalendarEvent,
} from '../services/google-calendar.js';
import { ParsedCommand } from './parser.js';

export async function handleScheduleEvent(command: ParsedCommand): Promise<string> {
  const params = command.params;

  if (!params.title) {
    return 'I need to know what to schedule. Please include a title for the event.';
  }

  if (!params.date) {
    return 'I need to know when to schedule this. Please include a date.';
  }

  try {
    const startDate = new Date(params.date);

    // Set time if provided
    if (params.time) {
      const [hours, minutes] = params.time.split(':').map(Number);
      startDate.setHours(hours, minutes, 0, 0);
    } else {
      // Default to 9:00 AM
      startDate.setHours(9, 0, 0, 0);
    }

    // Calculate end time
    const durationMinutes = params.duration || 60;
    const endDate = new Date(startDate.getTime() + durationMinutes * 60000);

    const event: CalendarEvent = {
      title: params.title,
      start: startDate,
      end: endDate,
      description: params.description,
      attendees: params.attendees,
    };

    const created = await createEvent(event);

    const timeStr = startDate.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

    return `✅ Event scheduled!\n\n*${created.title}*\n📅 ${timeStr}\n⏱️ ${durationMinutes} minutes`;
  } catch (error) {
    console.error('Failed to schedule event:', error);
    return 'Sorry, I could not schedule the event. Please check your Google Calendar settings.';
  }
}

export async function handleListCalendar(command: ParsedCommand): Promise<string> {
  const params = command.params;

  try {
    let date: Date;
    let dateLabel: string;

    if (params.date) {
      date = new Date(params.date);
      dateLabel = date.toLocaleDateString('en-US', {
        weekday: 'long',
        month: 'long',
        day: 'numeric',
      });
    } else {
      date = new Date();
      dateLabel = 'Today';
    }

    const events = await listEvents(date);

    if (events.length === 0) {
      return `📅 *${dateLabel}*\n\nNo events scheduled.`;
    }

    return `📅 *${dateLabel}*\n\n${formatEventsForDisplay(events)}`;
  } catch (error) {
    console.error('Failed to list calendar:', error);
    return 'Sorry, I could not fetch your calendar. Please check your Google Calendar settings.';
  }
}

export async function handleTomorrowPreview(command: ParsedCommand): Promise<string> {
  try {
    const events = await getTomorrowEvents();
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);

    const dateLabel = tomorrow.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
    });

    if (events.length === 0) {
      return `📅 *Tomorrow (${dateLabel})*\n\nNo events scheduled.`;
    }

    return `📅 *Tomorrow (${dateLabel})*\n\n${formatEventsForDisplay(events)}`;
  } catch (error) {
    console.error('Failed to get tomorrow preview:', error);
    return "Sorry, I could not fetch tomorrow's schedule. Please check your Google Calendar settings.";
  }
}
