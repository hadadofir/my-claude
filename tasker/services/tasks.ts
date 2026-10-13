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
  Timestamp,
  orderBy,
} from 'firebase/firestore';
import { db } from './firebase';

export type TaskPriority = 'low' | 'medium' | 'high';
export type TaskStatus = 'pending' | 'in_progress' | 'done';

export interface Task {
  id: string;
  householdId: string;
  title: string;
  description?: string;
  assignedTo?: string;
  assignedToName?: string;
  priority: TaskPriority;
  status: TaskStatus;
  dueDate?: Timestamp;
  calendarEventId?: string;
  locationId?: string;
  locationName?: string;
  createdBy: string;
  createdAt: unknown;
  updatedAt: unknown;
}

export function subscribeTasks(householdId: string, callback: (tasks: Task[]) => void) {
  const q = query(
    collection(db, 'tasks'),
    where('householdId', '==', householdId),
    orderBy('createdAt', 'desc')
  );
  return onSnapshot(q, (snap) => {
    const tasks = snap.docs.map((d) => ({ id: d.id, ...d.data() } as Task));
    callback(tasks);
  });
}

export async function addTask(task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>): Promise<string> {
  const ref = await addDoc(collection(db, 'tasks'), {
    ...task,
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
  });
  return ref.id;
}

export async function updateTask(id: string, updates: Partial<Task>): Promise<void> {
  await updateDoc(doc(db, 'tasks', id), { ...updates, updatedAt: serverTimestamp() });
}

export async function deleteTask(id: string): Promise<void> {
  await deleteDoc(doc(db, 'tasks', id));
}

export async function completeTask(id: string): Promise<void> {
  await updateDoc(doc(db, 'tasks', id), { status: 'done', updatedAt: serverTimestamp() });
}
