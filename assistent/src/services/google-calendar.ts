import { google, calendar_v3 } from 'googleapis';
import { config } from '../config.js';

export interface CalendarEvent {
  id?: string;
  title: string;
  start: Date;
  end: Date;
  description?: string;
  attendees?: string[];
  location?: string;
}

let calendarClient: calendar_v3.Calendar | null = null;

function getCalendarClient(): calendar_v3.Calendar {
  if (!calendarClient) {
    const oauth2Client = new google.auth.OAuth2(
      config.google.clientId,
      config.google.clientSecret
    );

    oauth2Client.setCredentials({
      refresh_token: config.google.refreshToken,
    });

    calendarClient = google.calendar({ version: 'v3', auth: oauth2Client });
  }
  return calendarClient;
}

export async function listEvents(date: Date): Promise<CalendarEvent[]> {
  const calendar = getCalendarClient();

  const startOfDay = new Date(date);
  startOfDay.setHours(0, 0, 0, 0);

  const endOfDay = new Date(date);
  endOfDay.setHours(23, 59, 59, 999);

  try {
    const response = await calendar.events.list({
      calendarId: 'primary',
      timeMin: startOfDay.toISOString(),
      timeMax: endOfDay.toISOString(),
      singleEvents: true,
      orderBy: 'startTime',
    });

    const events = response.data.items || [];

    return events.map(event => ({
      id: event.id || undefined,
      title: event.summary || 'Untitled',
      start: new Date(event.start?.dateTime || event.start?.date || ''),
      end: new Date(event.end?.dateTime || event.end?.date || ''),
      description: event.description || undefined,
      attendees: event.attendees?.map(a => a.email || '').filter(Boolean),
      location: event.location || undefined,
    }));
  } catch (error) {
    console.error('Failed to list calendar events:', error);
    throw error;
  }
}

export async function createEvent(event: CalendarEvent): Promise<CalendarEvent> {
  const calendar = getCalendarClient();

  try {
    const response = await calendar.events.insert({
      calendarId: 'primary',
      requestBody: {
        summary: event.title,
        description: event.description,
        location: event.location,
        start: {
          dateTime: event.start.toISOString(),
          timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        },
        end: {
          dateTime: event.end.toISOString(),
          timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        },
        attendees: event.attendees?.map(email => ({ email })),
      },
    });

    return {
      id: response.data.id || undefined,
      title: response.data.summary || event.title,
      start: new Date(response.data.start?.dateTime || event.start),
      end: new Date(response.data.end?.dateTime || event.end),
      description: response.data.description || undefined,
      attendees: response.data.attendees?.map(a => a.email || '').filter(Boolean),
      location: response.data.location || undefined,
    };
  } catch (error) {
    console.error('Failed to create calendar event:', error);
    throw error;
  }
}

export function formatEventsForDisplay(events: CalendarEvent[]): string {
  if (events.length === 0) {
    return 'No events scheduled.';
  }

  const lines = events.map(event => {
    const startTime = event.start.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
    const endTime = event.end.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });

    let line = `• ${startTime} - ${endTime}: ${event.title}`;

    if (event.location) {
      line += ` (${event.location})`;
    }

    return line;
  });

  return lines.join('\n');
}

export async function getTomorrowEvents(): Promise<CalendarEvent[]> {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return listEvents(tomorrow);
}

export async function getTodayEvents(): Promise<CalendarEvent[]> {
  return listEvents(new Date());
}
