import { receiveNotification, deleteNotification, sendMessage, getLastOutgoingMessages } from './client.js';
import { transcribeVoiceNote } from './voice.js';
import { config } from '../config.js';
import { getTargetGroupChatId } from './target-group.js';

// Track the last processed self-chat message timestamp
let lastSelfChatTimestamp = Math.floor(Date.now() / 1000);

export interface IncomingMessage {
  chatId: string;
  senderPhone: string;
  text: string;
  isVoice: boolean;
  voiceUrl?: string;
  timestamp: number;
}

export type MessageHandler = (message: IncomingMessage) => Promise<void>;

const ASSIST_PREFIX = /^assist\s*/i;

// Track processed message IDs to prevent duplicates
const processedMessages = new Set<string>();

function isAssistCommand(text: string): boolean {
  return ASSIST_PREFIX.test(text);
}

function extractCommand(text: string): string {
  return text.replace(ASSIST_PREFIX, '').trim();
}

function isFromMyPhone(senderPhone: string, chatId: string): boolean {
  const myPhone = config.whatsappPhone.replace(/\D/g, '');
  const sender = senderPhone.replace(/\D/g, '');
  const chat = chatId.replace(/\D/g, '');

  // Accept if sender is my phone, or if it's a self-chat (chatId is my number)
  const senderMatch = sender === myPhone || sender.endsWith(myPhone) || myPhone.endsWith(sender);
  const selfChat = chat === myPhone || chat.endsWith(myPhone) || myPhone.endsWith(chat);

  return senderMatch || selfChat;
}

export async function startListener(onCommand: (chatId: string, command: string) => Promise<void>): Promise<void> {
  console.log('Starting WhatsApp message listener...');

  const targetGroupChatId = getTargetGroupChatId();
  const selfChatId = `${config.whatsappPhone}@c.us`;

  console.log(`Listening to self-chat: ${selfChatId}`);
  if (targetGroupChatId) {
    console.log(`Also listening to group: ${config.targetGroupName}`);
  }

  // Start self-chat polling in parallel (workaround for Green API limitation)
  pollSelfChatMessages(selfChatId, onCommand);
  console.log('Self-chat polling started');

  while (true) {
    try {
      const notification = await receiveNotification();

      if (!notification) {
        await sleep(1000);
        continue;
      }

      const { receiptId, body } = notification;

      // Handle both incoming and outgoing messages (for self-messages)
      if (body.typeWebhook === 'incomingMessageReceived' || body.typeWebhook === 'outgoingMessageReceived') {
        const messageData = body.messageData;
        const senderData = body.senderData;
        const chatId = senderData?.chatId || body.chatId;
        const senderPhone = senderData?.sender?.replace('@c.us', '') || '';
        const messageId = body.idMessage;

        // Skip if already processed
        if (messageId && processedMessages.has(messageId)) {
          await deleteNotification(receiptId);
          continue;
        }
        if (messageId) {
          processedMessages.add(messageId);
          // Clean up old IDs (keep last 1000)
          if (processedMessages.size > 1000) {
            const firstId = processedMessages.values().next().value;
            processedMessages.delete(firstId);
          }
        }

        // Log the message source and content
        console.log(`Message from: ${senderPhone} in chat: ${chatId}`);
        console.log(`Message data type: ${messageData?.typeMessage}`);

        // Filter: only process messages from self-chat or target group
        const isAllowedChat = chatId === selfChatId || (targetGroupChatId && chatId === targetGroupChatId);
        if (!isAllowedChat) {
          console.log(`Ignoring message from non-target chat: ${chatId}`);
          await deleteNotification(receiptId);
          continue;
        }

        let messageText = '';
        let isVoice = false;
        let voiceUrl: string | undefined;

        if (messageData.typeMessage === 'textMessage') {
          messageText = messageData.textMessageData?.textMessage || '';
        } else if (messageData.typeMessage === 'extendedTextMessage') {
          messageText = messageData.extendedTextMessageData?.text || '';
        } else if (messageData.typeMessage === 'audioMessage') {
          isVoice = true;
          voiceUrl = messageData.fileMessageData?.downloadUrl;

          if (voiceUrl) {
            console.log('Received voice note, transcribing...');
            try {
              messageText = await transcribeVoiceNote(voiceUrl);
              console.log(`Transcribed: ${messageText}`);
            } catch (error) {
              console.error('Failed to transcribe voice note:', error);
              await sendMessage(chatId, 'Sorry, I could not transcribe your voice note.');
              await deleteNotification(receiptId);
              continue;
            }
          }
        }

        console.log(`Extracted text: "${messageText}"`);

        if (messageText && isAssistCommand(messageText)) {
          const command = extractCommand(messageText);
          console.log(`Received command: "${command}" from ${chatId}`);

          try {
            await onCommand(chatId, command);
          } catch (error) {
            console.error('Error handling command:', error);
            await sendMessage(chatId, 'Sorry, an error occurred while processing your command.');
          }
        }
      }

      await deleteNotification(receiptId);
    } catch (error) {
      console.error('Listener error:', error);
      await sleep(5000);
    }
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Poll for self-chat messages (workaround for Green API limitation)
async function pollSelfChatMessages(
  selfChatId: string,
  onCommand: (chatId: string, command: string) => Promise<void>
): Promise<void> {
  while (true) {
    try {
      const messages = await getLastOutgoingMessages();

      // Filter for self-chat messages that are newer than last processed
      const selfChatMessages = messages.filter(
        m => m.chatId === selfChatId &&
             m.timestamp > lastSelfChatTimestamp &&
             m.textMessage &&
             !m.sendByApi && // Don't process messages sent by the bot itself
             !processedMessages.has(m.idMessage)
      );

      for (const msg of selfChatMessages) {
        processedMessages.add(msg.idMessage);
        lastSelfChatTimestamp = Math.max(lastSelfChatTimestamp, msg.timestamp);

        const messageText = msg.textMessage || '';
        console.log(`[Self-chat] Message: "${messageText}"`);

        if (messageText && isAssistCommand(messageText)) {
          const command = extractCommand(messageText);
          console.log(`[Self-chat] Received command: "${command}"`);

          try {
            await onCommand(selfChatId, command);
          } catch (error) {
            console.error('Error handling self-chat command:', error);
            await sendMessage(selfChatId, 'Sorry, an error occurred while processing your command.');
          }
        }
      }
    } catch (error) {
      console.error('Self-chat polling error:', error);
    }

    await sleep(2000); // Poll every 2 seconds
  }
}
