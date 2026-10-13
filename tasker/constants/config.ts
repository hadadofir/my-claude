// Replace these with your actual Firebase and Google credentials
// See SETUP.md for instructions

export const firebaseConfig = {
  apiKey: "YOUR_FIREBASE_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID",
};

export const googleConfig = {
  iosClientId: "YOUR_IOS_CLIENT_ID",
  androidClientId: "YOUR_ANDROID_CLIENT_ID",
  webClientId: "YOUR_WEB_CLIENT_ID",
  scopes: [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
  ],
};
