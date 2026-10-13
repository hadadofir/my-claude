import { useEffect, useState } from 'react';
import { subscribeTasks, Task } from '@/services/tasks';

export function useTasks(householdId: string | null) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!householdId) {
      setTasks([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    const unsub = subscribeTasks(householdId, (t) => {
      setTasks(t);
      setLoading(false);
    });
    return unsub;
  }, [householdId]);

  const pending = tasks.filter((t) => t.status !== 'done');
  const done = tasks.filter((t) => t.status === 'done');

  return { tasks, pending, done, loading };
}
