# Tasker — Setup Guide

A family task manager and shopping list app for iOS and Android with real-time sync, Google Calendar integration, and opportunistic location-based notifications.

---

## Prerequisites

- Node.js 18+
- [Expo CLI](https://docs.expo.dev/get-started/installation/): `npm install -g expo-cli eas-cli`
- Xcode (for iOS simulator) or Android Studio (for Android emulator)
- A Firebase project
- A Google Cloud project

---

## Step 1 — Install dependencies

```bash
cd tasker
npm install
```

---

## Step 2 — Create a Firebase project

1. Go to [console.firebase.google.com](https://console.firebase.google.com) → **Add project**
2. Name it `tasker` (or anything you like)
3. Enable **Google Analytics** (optional)

### Enable Authentication
- Firebase console → **Authentication** → **Get started**
- Enable **Google** sign-in provider
- Add your support email

### Create Firestore database
- Firebase console → **Firestore Database** → **Create database**
- Choose **production mode** → pick a region close to you

### Firestore security rules
In the Firestore rules editor, replace the default with:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
    match /households/{householdId} {
      allow read: if request.auth.uid in resource.data.members.uid;
      allow write: if request.auth != null;
    }
    match /tasks/{taskId} {
      allow read, write: if request.auth != null &&
        request.auth.uid in get(/databases/$(database)/documents/households/$(resource.data.householdId)).data.members[*].uid;
    }
    match /shoppingLists/{listId} {
      allow read, write: if request.auth != null;
    }
    match /shoppingItems/{itemId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### Get Firebase config
- Firebase console → **Project settings** (gear icon) → **Your apps** → **Add app** → Web (`</>`)
- Copy the `firebaseConfig` object values

### Register iOS and Android apps
- In **Project settings → Your apps**, add an iOS app (bundle ID: `com.yourname.tasker`) and an Android app (package: `com.yourname.tasker`)
- Download `google-services.json` (Android) and `GoogleService-Info.plist` (iOS) — you'll need these for EAS builds

---

## Step 3 — Set up Google OAuth (for Calendar access)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Select your Firebase project (it was auto-created there)
3. **APIs & Services** → **Enable APIs** → enable **Google Calendar API**
4. **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
   - Create one for **iOS** (bundle ID: `com.yourname.tasker`)
   - Create one for **Android** (package + SHA-1 fingerprint — run `eas credentials` to get it)
   - Create one for **Web** (needed as the `webClientId` for Google Sign-In)

---

## Step 4 — Fill in credentials

Open `constants/config.ts` and replace all placeholder values:

```ts
export const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123",
};

export const googleConfig = {
  iosClientId: "123456789-xxx.apps.googleusercontent.com",
  androidClientId: "123456789-xxx.apps.googleusercontent.com",
  webClientId: "123456789-xxx.apps.googleusercontent.com",
  scopes: [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
  ],
};
```

---

## Step 5 — Run the app

### On a simulator/emulator
```bash
npm run ios      # iOS simulator
npm run android  # Android emulator
```

### On a physical device (recommended for location features)
```bash
npx expo start
```
Then scan the QR code with the **Expo Go** app.

> **Note:** Geofencing (background location) requires a development build — it does not work in Expo Go.
> Run `npx eas build --profile development --platform ios` to create a dev build with full native features.

---

## Step 6 — Invite your partner

1. Open the app, sign in with Google
2. Tap **Create household**
3. Go to **Settings** → **Share with partner**
4. Your partner installs the app, signs in, taps **Join household**, and pastes the shared ID

---

## How opportunistic notifications work

When you add a store location (lat/lng) to a shopping list:
1. The app registers a **geofence** around that store
2. When your phone enters that area AND the list has unchecked items, a notification fires immediately: *"You're near Whole Foods! You have 3 items on your Groceries list"*
3. The geofence refreshes automatically whenever items are added or checked off

To get a store's coordinates: open Google Maps → long-press the store → copy the lat/lng shown at the bottom.

---

## Building for production

```bash
# Configure EAS
npx eas build:configure

# Build for iOS (uploads to TestFlight)
npx eas build --platform ios --profile production

# Build for Android (.aab for Play Store)
npx eas build --platform android --profile production
```

You'll need an Apple Developer account ($99/year) and Google Play Developer account ($25 one-time).

---

## Project structure

```
tasker/
├── app/
│   ├── _layout.tsx          Auth guard + root navigation
│   ├── (auth)/index.tsx     Google sign-in screen
│   ├── setup.tsx            Create / join household
│   └── (tabs)/
│       ├── tasks.tsx        Task list with filters
│       ├── shopping.tsx     Shopping lists + items
│       ├── calendar.tsx     Monthly view + Google Calendar events
│       └── settings.tsx     Profile, household sharing, toggles
├── components/              Reusable UI pieces
├── services/                Firebase, Calendar API, geofence, notifications
├── hooks/                   React hooks wrapping services
├── store/                   Zustand auth store
└── constants/               Theme tokens + credentials config
```
