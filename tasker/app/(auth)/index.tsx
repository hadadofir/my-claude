import { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Image,
  useColorScheme,
} from 'react-native';
import { signInWithGoogle } from '@/services/auth';
import { colors, spacing, radius, typography } from '@/constants/theme';

export default function LoginScreen() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scheme = useColorScheme();
  const isDark = scheme === 'dark';

  async function handleSignIn() {
    setLoading(true);
    setError(null);
    try {
      await signInWithGoogle();
    } catch (e: any) {
      setError('Sign in failed. Please try again.');
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={[styles.container, isDark && styles.containerDark]}>
      <View style={styles.hero}>
        <View style={styles.iconWrapper}>
          <Text style={styles.iconText}>✓</Text>
        </View>
        <Text style={[styles.title, isDark && styles.textDark]}>Tasker</Text>
        <Text style={[styles.subtitle, isDark && styles.subtitleDark]}>
          Your family's shared task & shopping list
        </Text>
      </View>

      <View style={styles.features}>
        {[
          { icon: '📋', text: 'Shared tasks & shopping lists' },
          { icon: '📍', text: 'Location-based opportunistic reminders' },
          { icon: '📅', text: 'Google Calendar sync' },
          { icon: '👨‍👩‍👧', text: 'Real-time family sync' },
        ].map((f) => (
          <View key={f.text} style={styles.featureRow}>
            <Text style={styles.featureIcon}>{f.icon}</Text>
            <Text style={[styles.featureText, isDark && styles.textDark]}>{f.text}</Text>
          </View>
        ))}
      </View>

      {error && <Text style={styles.error}>{error}</Text>}

      <TouchableOpacity
        style={[styles.googleButton, loading && styles.googleButtonDisabled]}
        onPress={handleSignIn}
        disabled={loading}
        activeOpacity={0.8}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <>
            <Text style={styles.googleIcon}>G</Text>
            <Text style={styles.googleButtonText}>Continue with Google</Text>
          </>
        )}
      </TouchableOpacity>

      <Text style={[styles.legal, isDark && styles.subtitleDark]}>
        By signing in you agree to sync your data securely via Firebase
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    paddingHorizontal: spacing.xl,
    justifyContent: 'center',
  },
  containerDark: { backgroundColor: colors.backgroundDark },
  hero: { alignItems: 'center', marginBottom: spacing.xxl },
  iconWrapper: {
    width: 80,
    height: 80,
    borderRadius: radius.xl,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.md,
  },
  iconText: { fontSize: 40, color: '#fff' },
  title: { ...typography.h1, color: colors.text, marginBottom: spacing.sm },
  textDark: { color: colors.textDark },
  subtitle: { ...typography.body, color: colors.textSecondary, textAlign: 'center' },
  subtitleDark: { color: '#9CA3AF' },
  features: { marginBottom: spacing.xxl },
  featureRow: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.md },
  featureIcon: { fontSize: 20, marginRight: spacing.md },
  featureText: { ...typography.body, color: colors.text },
  error: { color: colors.danger, textAlign: 'center', marginBottom: spacing.md },
  googleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    marginBottom: spacing.md,
  },
  googleButtonDisabled: { opacity: 0.6 },
  googleIcon: {
    fontSize: 18,
    fontWeight: '700',
    color: '#fff',
    marginRight: spacing.sm,
  },
  googleButtonText: { ...typography.body, fontWeight: '600', color: '#fff' },
  legal: { ...typography.tiny, color: colors.textSecondary, textAlign: 'center' },
});
