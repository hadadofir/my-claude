import { create } from 'zustand';
import { User } from 'firebase/auth';

interface AuthState {
  user: User | null;
  householdId: string | null;
  loading: boolean;
  setUser: (user: User | null) => void;
  setHouseholdId: (id: string | null) => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  householdId: null,
  loading: true,
  setUser: (user) => set({ user }),
  setHouseholdId: (householdId) => set({ householdId }),
  setLoading: (loading) => set({ loading }),
}));
