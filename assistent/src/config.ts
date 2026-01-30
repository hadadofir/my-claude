import dotenv from 'dotenv';

dotenv.config();

function getEnvVar(name: string, required: boolean = true): string {
  const value = process.env[name];
  if (!value && required) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value || '';
}

export const config = {
  // Green API (WhatsApp)
  greenApi: {
    instanceId: getEnvVar('GREEN_API_INSTANCE_ID'),
    token: getEnvVar('GREEN_API_TOKEN'),
  },
  whatsappPhone: getEnvVar('WHATSAPP_PHONE'),

  // Google OAuth
  google: {
    clientId: getEnvVar('GOOGLE_CLIENT_ID'),
    clientSecret: getEnvVar('GOOGLE_CLIENT_SECRET'),
    refreshToken: getEnvVar('GOOGLE_REFRESH_TOKEN'),
  },

  // Google Gemini API (optional - for AI features)
  geminiApiKey: getEnvVar('GEMINI_API_KEY', false),

  // OpenAI API (for Whisper transcription) - optional
  openaiApiKey: getEnvVar('OPENAI_API_KEY', false),

  // Daily brief time (24-hour format)
  dailyBriefHour: parseInt(process.env.DAILY_BRIEF_HOUR || '22', 10),
  dailyBriefMinute: parseInt(process.env.DAILY_BRIEF_MINUTE || '0', 10),

  // Reminder storage path
  reminderStorePath: process.env.REMINDER_STORE_PATH || './data/reminders.json',

  // Target group name (only listen to this group)
  targetGroupName: getEnvVar('TARGET_GROUP_NAME', false) || 'AI-Assist',
};

export type Config = typeof config;
