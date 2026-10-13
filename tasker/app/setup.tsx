import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  useColorScheme,
  Alert,
} from 'react-native';
import { useAuthStore } from '@/store/authStore';
import { createHousehold, joinHousehold } from '@/services/household';
import { colors, spacing, radius, typography } from '@/constants/theme';

type Mode = 'choose' | 'create' | 'join';

export default function SetupScreen() {
  const [mode, setMode] = useState<Mode>('choose');
  const [householdName, setHouseholdName] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [loading, setLoading] = useState(false);
  const { user, setHouseholdId } = useAuthStore();
  const scheme = useColorScheme();
  const isDark = scheme === 'dark';

  async function handleCreate() {
    if (!user) return;
    setLoading(true);
    try {
      const id = await createHousehold(
        user.uid,
        user.displayName ?? 'User',
        user.email ?? '',
        user.photoURL
      );
      setHouseholdId(id);
    } catch (e) {
      Alert.alert('Error', 'Failed to create household. Try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleJoin() {
    if (!user || !joinCode.trim()) return;
    setLoading(true);
    try {
      await joinHousehold(
        joinCode.trim(),
        user.uid,
        user.displayName ?? 'User',
        user.email ?? '',
        user.photoURL
      );
      setHouseholdId(joinCode.trim());
    } catch (e) {
      Alert.alert('Error', 'Household not found. Check the code and try again.');
    } finally {
      setLoading(false);
    }
  }

  const inputStyle = [styles.input, isDark && styles.inputDark];
  const textStyle = [styles.label, isDark && styles.textDark];

  return (
    <View style={[styles.container, isDark && styles.containerDark]}>
      <Text style={[styles.title, isDark && styles.textDark]}>Set up your family</Text>
      <Text style={[styles.subtitle, isDark && styles.subtitleDark]}>
        Create a household or join one your partner already set up
      </Text>

      {mode === 'choose' && (
        <View style={styles.choices}>
          <TouchableOpacity style={styles.card} onPress={() => setMode('create')} activeOpacity={0.8}>
            <Text style={styles.cardIcon}>🏠</Text>
            <Text style={styles.cardTitle}>Create household</Text>
            <Text style={styles.cardDesc}>Start a new family space and invite your partner</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.card} onPress={() => setMode('join')} activeOpacity={0.8}>
            <Text style={styles.cardIcon}>🔗</Text>
            <Text style={styles.cardTitle}>Join household</Text>
            <Text style={styles.cardDesc}>Enter the household ID your partner shared with you</Text>
          </TouchableOpacity>
        </View>
      )}

      {mode === 'create' && (
        <View style={styles.form}>
          <TouchableOpacity onPress={() => setMode('choose')}>
            <Text style={styles.back}>← Back</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.primaryButton, loading && styles.buttonDisabled]}
            onPress={handleCreate}
            disabled={loading}
          >
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.primaryButtonText}>Create Household</Text>}
          </TouchableOpacity>
          <Text style={[styles.hint, isDark && styles.subtitleDark]}>
            After creating, share your household ID with your partner from Settings.
          </Text>
        </View>
      )}

      {mode === 'join' && (
        <View style={styles.form}>
          <TouchableOpacity onPress={() => setMode('choose')}>
            <Text style={styles.back}>← Back</Text>
          </TouchableOpacity>
          <Text style={textStyle}>Household ID</Text>
          <TextInput
            style={inputStyle}
            placeholder="Paste household ID here"
            placeholderTextColor={colors.textSecondary}
            value={joinCode}
            onChangeText={setJoinCode}
            autoCapitalize="none"
          />
          <TouchableOpacity
            style={[styles.primaryButton, (!joinCode.trim() || loading) && styles.buttonDisabled]}
            onPress={handleJoin}
            disabled={!joinCode.trim() || loading}
          >
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.primaryButtonText}>Join Household</Text>}
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.xl, justifyContent: 'center' },
  containerDark: { backgroundColor: colors.backgroundDark },
  title: { ...typography.h1, color: colors.text, marginBottom: spacing.sm },
  textDark: { color: colors.textDark },
  subtitle: { ...typography.body, color: colors.textSecondary, marginBottom: spacing.xl },
  subtitleDark: { color: '#9CA3AF' },
  choices: { gap: spacing.md },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardIcon: { fontSize: 32, marginBottom: spacing.sm },
  cardTitle: { ...typography.h3, color: colors.text, marginBottom: spacing.xs },
  cardDesc: { ...typography.small, color: colors.textSecondary },
  form: { gap: spacing.md },
  back: { color: colors.primary, ...typography.body },
  label: { ...typography.small, fontWeight: '600', color: colors.text },
  input: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
    ...typography.body,
    color: colors.text,
  },
  inputDark: { backgroundColor: colors.surfaceDark, borderColor: colors.borderDark, color: colors.textDark },
  primaryButton: {
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    padding: spacing.md,
    alignItems: 'center',
  },
  buttonDisabled: { opacity: 0.5 },
  primaryButtonText: { ...typography.body, fontWeight: '600', color: '#fff' },
  hint: { ...typography.small, color: colors.textSecondary },
});
