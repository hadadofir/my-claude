# Session Context - WhatsApp Personal Assistant

## Current State (2026-01-26)

### What's Working
- Script is running and listening for "Assist" commands
- Listening to **self-chat** (`972526662836@c.us`) - PRIMARY
- Also listening to **AI-Assist group** (`120363425786728836@g.us`)
- Daily brief scheduler: 22:00 every day (sends to self-chat)
- Reminder scheduler: checking every minute

### Key Fix Applied This Session
- **Fixed API URL** in `src/whatsapp/client.ts:3`
  - Changed from `https://7105.api.greenapi.com/...` (wrong - DNS doesn't resolve)
  - To `https://api.green-api.com/...` (correct)

### Why Self-Chat Was Needed
- Green API doesn't deliver self-sent messages in groups to the notification queue
- Self-sent messages in private chats (including self-chat) DO work
- Modified `src/whatsapp/listener.ts` to accept messages from self-chat
- Modified `src/scheduler/daily-brief.ts` to send to self-chat

### Files Modified This Session
1. `src/whatsapp/client.ts` - Fixed API base URL
2. `src/whatsapp/listener.ts` - Added self-chat listening
3. `src/scheduler/daily-brief.ts` - Send daily brief to self-chat

### How to Test
1. Open WhatsApp on your phone
2. Go to your self-chat (message yourself)
3. Send: `Assist hello` or `Assist what's on my calendar today`

### How to Run
```bash
cd /media/external/Ofir/sandbox/assistent
npm start
```

### Configuration
- Green API Instance: `7105482087`
- WhatsApp Phone: `972526662836`
- Target Group: `AI-Assist`
- Self-chat ID: `972526662836@c.us`
- Group ID: `120363425786728836@g.us`

### Environment Variables (in .env)
- GREEN_API_INSTANCE_ID
- GREEN_API_TOKEN
- WHATSAPP_PHONE
- GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN
- GEMINI_API_KEY
- OPENAI_API_KEY (optional - for voice transcription)

### Known Limitations
- Self-sent messages in groups don't trigger notifications (Green API limitation)
- Voice transcription requires OPENAI_API_KEY to be set

### Next Steps / TODO
- Test sending "Assist" commands from self-chat
- Verify commands are being processed correctly
