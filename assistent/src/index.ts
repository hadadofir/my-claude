import { config } from './config.js';
import { startListener } from './whatsapp/listener.js';
import { sendMessage } from './whatsapp/client.js';
import { handleCommand } from './commands/handler.js';
import { startDailyBriefScheduler } from './scheduler/daily-brief.js';
import { startReminderScheduler } from './scheduler/reminder-scheduler.js';
import { initializeTargetGroup, setTargetGroupPicture, getTargetGroupChatId } from './whatsapp/target-group.js';

// Funny robot/AI assistant image URL
const FUNNY_GROUP_PICTURE_URL = 'https://i.imgur.com/7kQEsHg.png';

async function onCommand(chatId: string, command: string): Promise<void> {
  try {
    const response = await handleCommand(chatId, command);
    await sendMessage(chatId, response);
  } catch (error) {
    console.error('Error handling command:', error);
    await sendMessage(chatId, 'Sorry, an error occurred. Please try again.');
  }
}

async function main(): Promise<void> {
  console.log('========================================');
  console.log('   WhatsApp Personal Assistant');
  console.log('========================================');
  console.log('');

  // Validate configuration
  try {
    console.log('Validating configuration...');
    console.log(`✓ Green API Instance: ${config.greenApi.instanceId}`);
    console.log(`✓ WhatsApp Phone: ${config.whatsappPhone}`);
    console.log(`✓ Target Group: ${config.targetGroupName}`);
    console.log(`✓ Google OAuth: Configured`);
    console.log(`✓ OpenAI API: ${config.openaiApiKey ? 'Configured' : 'Not configured'}`);
    console.log('');
  } catch (error) {
    console.error('Configuration error:', error);
    process.exit(1);
  }

  // Initialize target group
  console.log('Initializing target group...');
  const groupId = await initializeTargetGroup();
  if (groupId) {
    console.log(`✓ Listening to group: ${config.targetGroupName}`);

    // Set a funny group picture (only once on first run or when requested)
    if (process.env.SET_GROUP_PICTURE === 'true') {
      console.log('Setting funny group picture...');
      await setTargetGroupPicture(FUNNY_GROUP_PICTURE_URL);
    }
  } else {
    console.log('⚠ Target group not found - will listen to all chats');
  }
  console.log('');

  // Start schedulers
  console.log('Starting schedulers...');
  startDailyBriefScheduler();
  startReminderScheduler();
  console.log('');

  // Start WhatsApp listener
  console.log('Starting WhatsApp listener...');
  console.log('Listening for "Assist" commands...');
  console.log('');
  console.log('Examples:');
  console.log('  Assist what\'s on my calendar today');
  console.log('  Assist remind me to call mom in 2 hours');
  console.log('  Assist email brief');
  console.log('');
  console.log('Press Ctrl+C to stop.');
  console.log('========================================');

  await startListener(onCommand);
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\nShutting down...');
  process.exit(0);
});

// Run the assistant
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
