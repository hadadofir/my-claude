import { google, gmail_v1 } from 'googleapis';
import { config } from '../config.js';

export interface EmailSummary {
  from: string;
  subject: string;
  snippet: string;
  date: Date;
}

export interface EmailBrief {
  emails: EmailSummary[];
  summary: string;
  count: number;
}

let gmailClient: gmail_v1.Gmail | null = null;

function getGmailClient(): gmail_v1.Gmail {
  if (!gmailClient) {
    const oauth2Client = new google.auth.OAuth2(
      config.google.clientId,
      config.google.clientSecret
    );

    oauth2Client.setCredentials({
      refresh_token: config.google.refreshToken,
    });

    gmailClient = google.gmail({ version: 'v1', auth: oauth2Client });
  }
  return gmailClient;
}

function getHeader(headers: gmail_v1.Schema$MessagePartHeader[], name: string): string {
  const header = headers?.find(h => h.name?.toLowerCase() === name.toLowerCase());
  return header?.value || '';
}

function extractSenderName(from: string): string {
  const match = from.match(/^([^<]+)/);
  return match ? match[1].trim().replace(/"/g, '') : from;
}

export async function getRecentEmails(hoursAgo: number = 24): Promise<EmailSummary[]> {
  const gmail = getGmailClient();

  const afterDate = new Date();
  afterDate.setHours(afterDate.getHours() - hoursAgo);
  const afterTimestamp = Math.floor(afterDate.getTime() / 1000);

  try {
    const response = await gmail.users.messages.list({
      userId: 'me',
      q: `after:${afterTimestamp}`,
      maxResults: 50,
    });

    const messages = response.data.messages || [];
    const emails: EmailSummary[] = [];

    for (const msg of messages.slice(0, 20)) {
      if (!msg.id) continue;

      const detail = await gmail.users.messages.get({
        userId: 'me',
        id: msg.id,
        format: 'metadata',
        metadataHeaders: ['From', 'Subject', 'Date'],
      });

      const headers = detail.data.payload?.headers || [];

      emails.push({
        from: getHeader(headers, 'From'),
        subject: getHeader(headers, 'Subject') || '(No subject)',
        snippet: detail.data.snippet || '',
        date: new Date(getHeader(headers, 'Date')),
      });
    }

    return emails;
  } catch (error) {
    console.error('Failed to fetch emails:', error);
    throw error;
  }
}

export async function generateEmailBrief(hoursAgo: number = 24): Promise<EmailBrief> {
  const emails = await getRecentEmails(hoursAgo);

  if (emails.length === 0) {
    return {
      emails: [],
      summary: 'No new emails in the last 24 hours.',
      count: 0,
    };
  }

  // Simple summary without AI - just list the emails
  const summaryLines = emails.slice(0, 10).map(e => {
    const sender = extractSenderName(e.from);
    return `• *${sender}*: ${e.subject}`;
  });

  const summary = summaryLines.join('\n');

  return {
    emails,
    summary,
    count: emails.length,
  };
}

export function formatEmailBriefForDisplay(brief: EmailBrief): string {
  if (brief.count === 0) {
    return '📧 No new emails in the last 24 hours.';
  }

  return `📧 *Email Brief* (${brief.count} emails)\n\n${brief.summary}`;
}
