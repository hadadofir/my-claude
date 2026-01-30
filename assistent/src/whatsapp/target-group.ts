import { findGroupByName, setGroupPicture } from './client.js';
import { config } from '../config.js';

let targetGroupChatId: string | null = null;

export function getTargetGroupChatId(): string | null {
  return targetGroupChatId;
}

export async function initializeTargetGroup(): Promise<string | null> {
  console.log(`Looking for group: ${config.targetGroupName}`);

  const group = await findGroupByName(config.targetGroupName);
  if (!group) {
    console.error(`Could not find group named "${config.targetGroupName}".`);
    console.log('Make sure the group exists and the bot is a member.');
    return null;
  }

  targetGroupChatId = group.id;
  console.log(`Found group "${config.targetGroupName}" with ID: ${targetGroupChatId}`);
  return targetGroupChatId;
}

export async function setTargetGroupPicture(imageUrl: string): Promise<boolean> {
  if (!targetGroupChatId) {
    console.error('Target group not initialized. Call initializeTargetGroup first.');
    return false;
  }

  console.log(`Setting group picture for ${config.targetGroupName}...`);
  const success = await setGroupPicture(targetGroupChatId, imageUrl);
  if (success) {
    console.log('Group picture updated successfully!');
  }
  return success;
}
