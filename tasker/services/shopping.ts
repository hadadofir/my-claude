import {
  collection,
  addDoc,
  updateDoc,
  deleteDoc,
  doc,
  query,
  where,
  onSnapshot,
  serverTimestamp,
  orderBy,
  writeBatch,
} from 'firebase/firestore';
import { db } from './firebase';

export interface ShoppingList {
  id: string;
  householdId: string;
  name: string;
  locationId?: string;
  locationName?: string;
  locationLat?: number;
  locationLng?: number;
  locationRadius?: number;
  createdBy: string;
  createdAt: unknown;
}

export interface ShoppingItem {
  id: string;
  listId: string;
  householdId: string;
  name: string;
  quantity?: string;
  checked: boolean;
  addedBy: string;
  addedAt: unknown;
}

export function subscribeShoppingLists(householdId: string, callback: (lists: ShoppingList[]) => void) {
  const q = query(
    collection(db, 'shoppingLists'),
    where('householdId', '==', householdId),
    orderBy('createdAt', 'desc')
  );
  return onSnapshot(q, (snap) => {
    callback(snap.docs.map((d) => ({ id: d.id, ...d.data() } as ShoppingList)));
  });
}

export function subscribeShoppingItems(listId: string, callback: (items: ShoppingItem[]) => void) {
  const q = query(
    collection(db, 'shoppingItems'),
    where('listId', '==', listId),
    orderBy('addedAt', 'asc')
  );
  return onSnapshot(q, (snap) => {
    callback(snap.docs.map((d) => ({ id: d.id, ...d.data() } as ShoppingItem)));
  });
}

export async function addShoppingList(list: Omit<ShoppingList, 'id' | 'createdAt'>): Promise<string> {
  const ref = await addDoc(collection(db, 'shoppingLists'), { ...list, createdAt: serverTimestamp() });
  return ref.id;
}

export async function updateShoppingList(id: string, updates: Partial<ShoppingList>): Promise<void> {
  await updateDoc(doc(db, 'shoppingLists', id), updates);
}

export async function deleteShoppingList(id: string): Promise<void> {
  await deleteDoc(doc(db, 'shoppingLists', id));
}

export async function addShoppingItem(item: Omit<ShoppingItem, 'id' | 'addedAt'>): Promise<string> {
  const ref = await addDoc(collection(db, 'shoppingItems'), { ...item, addedAt: serverTimestamp() });
  return ref.id;
}

export async function toggleShoppingItem(id: string, checked: boolean): Promise<void> {
  await updateDoc(doc(db, 'shoppingItems', id), { checked });
}

export async function deleteShoppingItem(id: string): Promise<void> {
  await deleteDoc(doc(db, 'shoppingItems', id));
}

export async function clearCheckedItems(listId: string, items: ShoppingItem[]): Promise<void> {
  const batch = writeBatch(db);
  items.filter((i) => i.checked).forEach((i) => batch.delete(doc(db, 'shoppingItems', i.id)));
  await batch.commit();
}
