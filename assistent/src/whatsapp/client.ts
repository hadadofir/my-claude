import { config } from '../config.js';

const API_BASE = `https://api.green-api.com/waInstance${config.greenApi.instanceId}`;

export interface WhatsAppClient {
  sendMessage(chatId: string, message: string): Promise<void>;
  downloadFile(url: string): Promise<Buffer>;
}

export function formatPhoneAsChatId(phone: string): string {
  const cleaned = phone.replace(/\D/g, '');
  return `${cleaned}@c.us`;
}

async function apiCall(method: string, endpoint: string, body?: any): Promise<any> {
  const url = `${API_BASE}/${endpoint}/${config.greenApi.token}`;

  const options: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }

  const text = await response.text();
  return text ? JSON.parse(text) : null;
}

export async function sendMessage(chatId: string, message: string): Promise<void> {
  try {
    await apiCall('POST', 'sendMessage', {
      chatId,
      message,
    });
    console.log(`Message sent to ${chatId}`);
  } catch (error) {
    console.error('Failed to send message:', error);
    throw error;
  }
}

export async function sendMessageToPhone(phone: string, message: string): Promise<void> {
  const chatId = formatPhoneAsChatId(phone);
  await sendMessage(chatId, message);
}

export async function downloadFile(url: string): Promise<Buffer> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to download file: ${response.statusText}`);
  }
  const arrayBuffer = await response.arrayBuffer();
  return Buffer.from(arrayBuffer);
}

export async function receiveNotification(): Promise<any> {
  try {
    const response = await apiCall('GET', 'receiveNotification');
    return response;
  } catch (error) {
    console.error('Failed to receive notification:', error);
    return null;
  }
}

export async function deleteNotification(receiptId: number): Promise<void> {
  try {
    const url = `${API_BASE}/deleteNotification/${receiptId}/${config.greenApi.token}`;
    await fetch(url, { method: 'DELETE' });
    // Silently ignore errors - deduplication handles repeats
  } catch {
    // Silently ignore
  }
}

export interface Contact {
  id: string;
  name: string;
  type: 'user' | 'group';
}

export async function getContacts(): Promise<Contact[]> {
  try {
    const response = await apiCall('GET', 'getContacts');
    return response || [];
  } catch (error) {
    console.error('Failed to get contacts:', error);
    return [];
  }
}

export async function findGroupByName(groupName: string): Promise<Contact | null> {
  const contacts = await getContacts();
  const group = contacts.find(
    (c) => c.type === 'group' && c.name?.toLowerCase() === groupName.toLowerCase()
  );
  return group || null;
}

export async function setGroupPicture(groupId: string, imageUrl: string): Promise<boolean> {
  try {
    // First download the image
    const imageResponse = await fetch(imageUrl);
    if (!imageResponse.ok) {
      throw new Error(`Failed to fetch image: ${imageResponse.statusText}`);
    }
    const imageBuffer = await imageResponse.arrayBuffer();
    const base64Image = Buffer.from(imageBuffer).toString('base64');

    // Determine content type
    const contentType = imageResponse.headers.get('content-type') || 'image/jpeg';

    // Use the setGroupPicture endpoint with form data
    const url = `${API_BASE}/setGroupPicture/${config.greenApi.token}`;
    const formData = new FormData();
    const blob = new Blob([Buffer.from(imageBuffer)], { type: contentType });
    formData.append('file', blob, 'group-picture.jpg');
    formData.append('groupId', groupId);

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`API error ${response.status}: ${text}`);
    }

    const result = await response.json();
    console.log('Group picture updated:', result);
    return result.setGroupPicture === true;
  } catch (error) {
    console.error('Failed to set group picture:', error);
    return false;
  }
}

export interface OutgoingMessage {
  idMessage: string;
  timestamp: number;
  chatId: string;
  textMessage?: string;
  typeMessage: string;
  sendByApi: boolean;
}

export async function getLastOutgoingMessages(): Promise<OutgoingMessage[]> {
  try {
    const response = await apiCall('GET', 'lastOutgoingMessages');
    return response || [];
  } catch (error) {
    console.error('Failed to get outgoing messages:', error);
    return [];
  }
}

export const whatsappClient: WhatsAppClient = {
  sendMessage,
  downloadFile,
};
