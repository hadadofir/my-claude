import { GoogleSignin } from '@react-native-google-signin/google-signin';

const CALENDAR_BASE = 'https://www.googleapis.com/calendar/v3';

async function getAccessToken(): Promise<string> {
  const tokens = await GoogleSignin.getTokens();
  return tokens.accessToken;
}

async function calendarFetch(path: string, options: RequestInit = {}): Promise<any> {
  const token = await getAccessToken();
  const res = await fetch(`${CALENDAR_BASE}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  if (!res.ok) throw new Error(`Calendar API error: ${res.status}`);
  return res.json();
}

export interface CalendarEvent {
  id?: string;
  summary: string;
  description?: string;
  start: { dateTime: string; timeZone?: string };
  end: { dateTime: string; timeZone?: string };
}

export async function getUpcomingEvents(maxResults = 20): Promise<CalendarEvent[]> {
  const timeMin = new Date().toISOString();
  const timeMax = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();
  const data = await calendarFetch(
    `/calendars/primary/events?timeMin=${timeMin}&timeMax=${timeMax}&maxResults=${maxResults}&singleEvents=true&orderBy=startTime`
  );
  return data.items ?? [];
}

export async function createEvent(event: CalendarEvent): Promise<CalendarEvent> {
  return calendarFetch('/calendars/primary/events', {
    method: 'POST',
    body: JSON.stringify(event),
  });
}

export async function updateEvent(eventId: string, updates: Partial<CalendarEvent>): Promise<CalendarEvent> {
  return calendarFetch(`/calendars/primary/events/${eventId}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function deleteEvent(eventId: string): Promise<void> {
  const token = await getAccessToken();
  await fetch(`${CALENDAR_BASE}/calendars/primary/events/${eventId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function taskToCalendarEvent(title: string, dueDate: Date, description?: string): CalendarEvent {
  const end = new Date(dueDate);
  end.setHours(end.getHours() + 1);
  return {
    summary: title,
    description,
    start: { dateTime: dueDate.toISOString() },
    end: { dateTime: end.toISOString() },
  };
}
