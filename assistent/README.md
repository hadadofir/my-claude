# WhatsApp Personal Assistant

A Node.js/TypeScript personal assistant that listens to WhatsApp messages and performs tasks when commanded with the "Assist" keyword.

## Features

- **WhatsApp Command Listener** - Listens for messages starting with "Assist"
- **Voice Note Support** - Transcribes voice messages using OpenAI Whisper
- **Google Calendar Integration** - Schedule events, view agenda
- **Gmail Integration** - Get email briefs from the last day
- **Reminders** - Set and manage reminders
- **Daily Brief** - Automated 22:00 summary of tomorrow's schedule

## Prerequisites

1. **Green API Account** - For WhatsApp messaging
2. **Google Cloud Project** - For Calendar and Gmail APIs
3. **Anthropic API Key** - For Claude AI (command parsing)
4. **OpenAI API Key** - For Whisper (voice transcription)

## Installation

```bash
# Clone or navigate to the project
cd assistant

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
```

## Configuration

### 1. Green API Setup

1. Go to [green-api.com](https://green-api.com/)
2. Create an account and get your Instance ID and API Token
3. Scan the QR code with WhatsApp to connect your phone
4. Add credentials to `.env`:
   ```
   GREEN_API_INSTANCE_ID=your_instance_id
   GREEN_API_TOKEN=your_token
   WHATSAPP_PHONE=your_phone_number
   ```

### 2. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Calendar API** and **Gmail API**
4. Create OAuth 2.0 credentials:
   - Application type: Desktop app
   - Download the credentials JSON
5. Get a refresh token:

```bash
# Install the Google OAuth playground or use this script
node scripts/get-google-token.js
```

Or use the [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/):
- Configure with your Client ID and Secret
- Select Calendar and Gmail scopes
- Exchange authorization code for tokens
- Copy the refresh token

6. Add to `.env`:
   ```
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   GOOGLE_REFRESH_TOKEN=your_refresh_token
   ```

### 3. Anthropic API Setup

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Create an API key
3. Add to `.env`:
   ```
   ANTHROPIC_API_KEY=your_key
   ```

### 4. OpenAI API Setup (for voice notes)

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Create an API key
3. Add to `.env`:
   ```
   OPENAI_API_KEY=your_key
   ```

## Usage

### Start the Assistant

```bash
npm start
```

### Development Mode (with auto-reload)

```bash
npm run dev
```

### Commands

Send these messages to yourself on WhatsApp:

| Command | Action |
|---------|--------|
| `Assist what's on my calendar today` | Lists today's events |
| `Assist what's tomorrow` | Preview tomorrow's schedule |
| `Assist schedule meeting tomorrow at 10am with John` | Creates calendar event |
| `Assist remind me to call mom in 2 hours` | Sets a reminder |
| `Assist list reminders` | Shows active reminders |
| `Assist email brief` | Summarizes last 24h of emails |

You can also send voice notes starting with "Assist" - they will be transcribed and processed.

### Daily Brief

The assistant automatically sends a summary at 22:00 (configurable) with:
- Tomorrow's calendar events
- Upcoming reminders

Configure the time in `.env`:
```
DAILY_BRIEF_HOUR=22
DAILY_BRIEF_MINUTE=0
```

## Project Structure

```
assistant/
├── src/
│   ├── index.ts              # Main entry point
│   ├── config.ts             # Configuration management
│   ├── whatsapp/
│   │   ├── client.ts         # Green API client wrapper
│   │   ├── listener.ts       # Message listener
│   │   └── voice.ts          # Voice transcription
│   ├── commands/
│   │   ├── parser.ts         # AI command parser
│   │   ├── handler.ts        # Command router
│   │   ├── calendar.ts       # Calendar handlers
│   │   ├── email.ts          # Email handlers
│   │   └── reminder.ts       # Reminder handlers
│   ├── services/
│   │   ├── google-calendar.ts # Google Calendar API
│   │   ├── gmail.ts          # Gmail API
│   │   └── reminder-store.ts # Reminder storage
│   └── scheduler/
│       ├── daily-brief.ts    # 22:00 daily summary
│       └── reminder-scheduler.ts # Reminder checker
├── data/
│   └── reminders.json        # Reminder storage (auto-created)
├── .env                      # Environment variables
├── .env.example              # Template
├── package.json
├── tsconfig.json
└── README.md
```

## Troubleshooting

### "Missing required environment variable"
Make sure all required variables in `.env` are filled in.

### WhatsApp messages not being received
1. Check Green API dashboard - is your instance connected?
2. Verify the phone number format (no + or spaces)
3. Check console for error messages

### Google Calendar/Gmail not working
1. Verify OAuth credentials are correct
2. Make sure refresh token is valid
3. Check that APIs are enabled in Google Cloud Console

### Voice notes not being transcribed
1. Verify OpenAI API key is valid
2. Check that you have Whisper API access
3. Voice notes must start with "Assist" to be processed

## Security Notes

- Keep your `.env` file secret - never commit it to git
- The assistant only responds to messages from your configured phone number
- Reminders are stored locally in a JSON file

## License

MIT
