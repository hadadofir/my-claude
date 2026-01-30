import OpenAI from 'openai';
import { config } from '../config.js';
import { downloadFile } from './client.js';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

let openaiClient: OpenAI | null = null;

function getOpenAIClient(): OpenAI {
  if (!openaiClient) {
    openaiClient = new OpenAI({
      apiKey: config.openaiApiKey,
    });
  }
  return openaiClient;
}

export async function transcribeVoiceNote(audioUrl: string): Promise<string> {
  const client = getOpenAIClient();

  // Download the audio file
  const audioBuffer = await downloadFile(audioUrl);

  // Create a temporary file
  const tempDir = os.tmpdir();
  const tempFilePath = path.join(tempDir, `voice_${Date.now()}.ogg`);

  try {
    // Write the audio buffer to a temp file
    fs.writeFileSync(tempFilePath, audioBuffer);

    // Use Whisper API for transcription
    const transcription = await client.audio.transcriptions.create({
      file: fs.createReadStream(tempFilePath),
      model: 'whisper-1',
      language: 'he', // Hebrew - adjust as needed
    });

    return transcription.text;
  } finally {
    // Clean up temp file
    try {
      fs.unlinkSync(tempFilePath);
    } catch {
      // Ignore cleanup errors
    }
  }
}
