/**
 * Helper script to get Google OAuth refresh token
 *
 * Usage:
 * 1. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
 * 2. Run: npx tsx scripts/get-google-token.ts
 * 3. Open the URL in your browser
 * 4. Authorize the app
 * 5. Copy the authorization code
 * 6. Paste it when prompted
 * 7. Copy the refresh token to your .env file
 */

import { google } from 'googleapis';
import * as readline from 'readline';
import dotenv from 'dotenv';

dotenv.config();

const SCOPES = [
  'https://www.googleapis.com/auth/calendar',
  'https://www.googleapis.com/auth/gmail.readonly',
];

async function getRefreshToken() {
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    console.error('Error: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env');
    process.exit(1);
  }

  const oauth2Client = new google.auth.OAuth2(
    clientId,
    clientSecret,
    'urn:ietf:wg:oauth:2.0:oob' // Redirect URI for desktop apps
  );

  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    prompt: 'consent', // Force consent screen to get refresh token
  });

  console.log('\n=== Google OAuth Token Generator ===\n');
  console.log('1. Open this URL in your browser:\n');
  console.log(authUrl);
  console.log('\n2. Authorize the application');
  console.log('3. Copy the authorization code\n');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const code = await new Promise<string>((resolve) => {
    rl.question('Enter the authorization code: ', (answer) => {
      resolve(answer);
      rl.close();
    });
  });

  try {
    const { tokens } = await oauth2Client.getToken(code);

    console.log('\n=== Success! ===\n');
    console.log('Add this to your .env file:\n');
    console.log(`GOOGLE_REFRESH_TOKEN=${tokens.refresh_token}`);
    console.log('\n');

    if (!tokens.refresh_token) {
      console.log('Warning: No refresh token received.');
      console.log('This can happen if you already authorized this app before.');
      console.log('Try revoking access at https://myaccount.google.com/permissions');
      console.log('Then run this script again.');
    }
  } catch (error) {
    console.error('Error getting tokens:', error);
  }
}

getRefreshToken();
