import {
  GoogleAuthProvider,
  signInWithCredential,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  User,
} from 'firebase/auth';
import { doc, setDoc, getDoc, serverTimestamp } from 'firebase/firestore';
import { GoogleSignin } from '@react-native-google-signin/google-signin';
import { auth, db } from './firebase';
import { googleConfig } from '@/constants/config';

export function configureGoogleSignIn() {
  GoogleSignin.configure({
    webClientId: googleConfig.webClientId,
    iosClientId: googleConfig.iosClientId,
    offlineAccess: true,
    scopes: googleConfig.scopes,
  });
}

export async function signInWithGoogle(): Promise<User> {
  await GoogleSignin.hasPlayServices();
  const { data } = await GoogleSignin.signIn();
  if (!data?.idToken) throw new Error('No ID token returned from Google Sign-In');
  const credential = GoogleAuthProvider.credential(data.idToken);
  const result = await signInWithCredential(auth, credential);
  await upsertUserProfile(result.user);
  return result.user;
}

async function upsertUserProfile(user: User) {
  const ref = doc(db, 'users', user.uid);
  const snap = await getDoc(ref);
  if (!snap.exists()) {
    await setDoc(ref, {
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
      photoURL: user.photoURL,
      createdAt: serverTimestamp(),
      householdId: null,
    });
  }
}

export async function signOut() {
  await GoogleSignin.signOut();
  await firebaseSignOut(auth);
}

export function onAuthChange(callback: (user: User | null) => void) {
  return onAuthStateChanged(auth, callback);
}
