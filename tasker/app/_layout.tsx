import { useEffect } from 'react';
import { Stack } from 'expo-router';
import { useRouter, useSegments } from 'expo-router';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { StatusBar } from 'expo-status-bar';
import { useAuth } from '@/hooks/useAuth';
import { useNotifications } from '@/hooks/useNotifications';

export default function RootLayout() {
  const { user, householdId, loading } = useAuth();
  useNotifications();
  const router = useRouter();
  const segments = useSegments();

  useEffect(() => {
    if (loading) return;
    const inAuth = segments[0] === '(auth)';
    const inSetup = segments[0] === 'setup';

    if (!user && !inAuth) {
      router.replace('/(auth)');
    } else if (user && !householdId && !inSetup) {
      router.replace('/setup');
    } else if (user && householdId && (inAuth || inSetup)) {
      router.replace('/(tabs)/tasks');
    }
  }, [user, householdId, loading, segments]);

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <StatusBar style="auto" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(auth)" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="setup" />
      </Stack>
    </GestureHandlerRootView>
  );
}
