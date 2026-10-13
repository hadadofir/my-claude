import { useEffect } from 'react';
import { onAuthChange } from '@/services/auth';
import { getUserHouseholdId } from '@/services/household';
import { useAuthStore } from '@/store/authStore';
import { configureGoogleSignIn } from '@/services/auth';

configureGoogleSignIn();

export function useAuth() {
  const { user, householdId, loading, setUser, setHouseholdId, setLoading } = useAuthStore();

  useEffect(() => {
    const unsub = onAuthChange(async (firebaseUser) => {
      setUser(firebaseUser);
      if (firebaseUser) {
        const hId = await getUserHouseholdId(firebaseUser.uid);
        setHouseholdId(hId);
      } else {
        setHouseholdId(null);
      }
      setLoading(false);
    });
    return unsub;
  }, []);

  return { user, householdId, loading };
}
