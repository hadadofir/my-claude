import { useEffect, useState } from 'react';
import {
  subscribeShoppingLists,
  subscribeShoppingItems,
  ShoppingList,
  ShoppingItem,
} from '@/services/shopping';
import { refreshGeofences } from '@/services/geofence';

export function useShoppingLists(householdId: string | null) {
  const [lists, setLists] = useState<ShoppingList[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!householdId) {
      setLists([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    const unsub = subscribeShoppingLists(householdId, (l) => {
      setLists(l);
      setLoading(false);
    });
    return unsub;
  }, [householdId]);

  return { lists, loading };
}

export function useShoppingItems(listId: string | null, lists: ShoppingList[]) {
  const [itemsByList, setItemsByList] = useState<Record<string, ShoppingItem[]>>({});

  useEffect(() => {
    if (!listId) return;
    const unsub = subscribeShoppingItems(listId, (items) => {
      setItemsByList((prev) => {
        const next = { ...prev, [listId]: items };
        // Refresh geofences whenever item counts change
        const itemCounts: Record<string, number> = {};
        Object.entries(next).forEach(([lid, its]) => {
          itemCounts[lid] = its.filter((i) => !i.checked).length;
        });
        refreshGeofences(lists, itemCounts).catch(console.error);
        return next;
      });
    });
    return unsub;
  }, [listId, lists]);

  return itemsByList;
}
