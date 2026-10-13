import {
  doc,
  setDoc,
  getDoc,
  updateDoc,
  collection,
  query,
  where,
  getDocs,
  serverTimestamp,
} from 'firebase/firestore';
import { db } from './firebase';

export interface HouseholdMember {
  uid: string;
  email: string;
  displayName: string;
  photoURL: string | null;
}

export interface Household {
  id: string;
  name: string;
  members: HouseholdMember[];
  createdBy: string;
  createdAt: unknown;
}

export async function createHousehold(userId: string, userName: string, userEmail: string, userPhoto: string | null): Promise<string> {
  const id = `household_${userId}`;
  await setDoc(doc(db, 'households', id), {
    id,
    name: `${userName}'s Family`,
    members: [{ uid: userId, email: userEmail, displayName: userName, photoURL: userPhoto }],
    createdBy: userId,
    createdAt: serverTimestamp(),
  });
  await updateDoc(doc(db, 'users', userId), { householdId: id });
  return id;
}

export async function joinHousehold(householdId: string, userId: string, userName: string, userEmail: string, userPhoto: string | null): Promise<void> {
  const ref = doc(db, 'households', householdId);
  const snap = await getDoc(ref);
  if (!snap.exists()) throw new Error('Household not found');
  const household = snap.data() as Household;
  const alreadyMember = household.members.some((m) => m.uid === userId);
  if (alreadyMember) return;
  await updateDoc(ref, {
    members: [...household.members, { uid: userId, email: userEmail, displayName: userName, photoURL: userPhoto }],
  });
  await updateDoc(doc(db, 'users', userId), { householdId });
}

export async function getHousehold(householdId: string): Promise<Household | null> {
  const snap = await getDoc(doc(db, 'households', householdId));
  return snap.exists() ? (snap.data() as Household) : null;
}

export async function getUserHouseholdId(userId: string): Promise<string | null> {
  const snap = await getDoc(doc(db, 'users', userId));
  return snap.exists() ? (snap.data().householdId ?? null) : null;
}
