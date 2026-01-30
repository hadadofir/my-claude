import { generateEmailBrief, formatEmailBriefForDisplay } from '../services/gmail.js';
import { ParsedCommand } from './parser.js';

export async function handleEmailBrief(command: ParsedCommand): Promise<string> {
  try {
    const brief = await generateEmailBrief(24);
    return formatEmailBriefForDisplay(brief);
  } catch (error) {
    console.error('Failed to get email brief:', error);
    return 'Sorry, I could not fetch your emails. Please check your Gmail settings.';
  }
}
