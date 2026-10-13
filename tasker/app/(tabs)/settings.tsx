import { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  useColorScheme,
  Switch,
  Alert,
  Share,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '@/store/authStore';
import { signOut } from '@/services/auth';
import { stopGeofencing } from '@/services/geofence';
import { cancelAllNotifications } from '@/services/notifications';
import { colors, spacing, radius, typography } from '@/constants/theme';

export default function SettingsScreen() {
  const isDark = useColorScheme() === 'dark';
  const { user, householdId } = useAuthStore();
  const [notifEnabled, setNotifEnabled] = useState(true);
  const [locationEnabled, setLocationEnabled] = useState(true);

  async function handleShareHouseholdId() {
    if (!householdId) return;
    await Share.share({
      message: `Join my household on Tasker! Use this ID: ${householdId}`,
      title: 'Tasker Household ID',
    });
  }

  async function handleSignOut() {
    Alert.alert('Sign out', 'Are you sure you want to sign out?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Sign out',
        style: 'destructive',
        onPress: async () => {
          await stopGeofencing().catch(() => {});
          await cancelAllNotifications().catch(() => {});
          await signOut();
        },
      },
    ]);
  }

  async function handleToggleLocation(value: boolean) {
    setLocationEnabled(value);
    if (!value) {
      await stopGeofencing().catch(() => {});
    }
  }

  async function handleToggleNotifs(value: boolean) {
    setNotifEnabled(value);
    if (!value) {
      await cancelAllNotifications().catch(() => {});
    }
  }

  const sectionStyle = [styles.section, isDark && styles.sectionDark];
  const textStyle = [styles.rowLabel, isDark && styles.textDark];

  return (
    <SafeAreaView style={[styles.container, isDark && styles.containerDark]} edges={['top']}>
      <Text style={[styles.title, isDark && styles.textDark]}>Settings</Text>
      <ScrollView showsVerticalScrollIndicator={false}>

        {/* Profile */}
        <Text style={[styles.sectionHeader, isDark && styles.sectionHeaderDark]}>Account</Text>
        <View style={sectionStyle}>
          <View style={styles.profileRow}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>
                {(user?.displayName ?? 'U')[0].toUpperCase()}
              </Text>
            </View>
            <View style={styles.profileInfo}>
              <Text style={[styles.profileName, isDark && styles.textDark]}>{user?.displayName}</Text>
              <Text style={styles.profileEmail}>{user?.email}</Text>
            </View>
          </View>
        </View>

        {/* Household */}
        <Text style={[styles.sectionHeader, isDark && styles.sectionHeaderDark]}>Household</Text>
        <View style={sectionStyle}>
          <View style={styles.row}>
            <Ionicons name="home-outline" size={20} color={colors.primary} />
            <View style={styles.rowContent}>
              <Text style={textStyle}>Household ID</Text>
              <Text style={styles.householdId} numberOfLines={1} ellipsizeMode="middle">
                {householdId ?? 'Not set'}
              </Text>
            </View>
          </View>
          <View style={styles.divider} />
          <TouchableOpacity style={styles.row} onPress={handleShareHouseholdId}>
            <Ionicons name="share-outline" size={20} color={colors.primary} />
            <Text style={textStyle}>Share with partner</Text>
            <Ionicons name="chevron-forward" size={16} color={colors.textSecondary} style={styles.chevron} />
          </TouchableOpacity>
        </View>

        {/* Notifications */}
        <Text style={[styles.sectionHeader, isDark && styles.sectionHeaderDark]}>Notifications</Text>
        <View style={sectionStyle}>
          <View style={styles.row}>
            <Ionicons name="notifications-outline" size={20} color={colors.primary} />
            <Text style={[textStyle, { flex: 1 }]}>Push notifications</Text>
            <Switch
              value={notifEnabled}
              onValueChange={handleToggleNotifs}
              trackColor={{ true: colors.primary }}
            />
          </View>
          <View style={styles.divider} />
          <View style={styles.row}>
            <Ionicons name="location-outline" size={20} color={colors.primary} />
            <View style={styles.rowContent}>
              <Text style={textStyle}>Opportunistic reminders</Text>
              <Text style={styles.rowSubtext}>Notify when near a store with items</Text>
            </View>
            <Switch
              value={locationEnabled}
              onValueChange={handleToggleLocation}
              trackColor={{ true: colors.primary }}
            />
          </View>
        </View>

        {/* About */}
        <Text style={[styles.sectionHeader, isDark && styles.sectionHeaderDark]}>About</Text>
        <View style={sectionStyle}>
          <View style={styles.row}>
            <Ionicons name="information-circle-outline" size={20} color={colors.primary} />
            <Text style={textStyle}>Version</Text>
            <Text style={styles.rowValue}>1.0.0</Text>
          </View>
        </View>

        {/* Sign out */}
        <TouchableOpacity style={[styles.signOutBtn, { marginHorizontal: spacing.md, marginTop: spacing.lg }]} onPress={handleSignOut}>
          <Ionicons name="log-out-outline" size={20} color={colors.danger} />
          <Text style={styles.signOutText}>Sign out</Text>
        </TouchableOpacity>

        <View style={{ height: spacing.xxl }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  containerDark: { backgroundColor: colors.backgroundDark },
  title: { ...typography.h2, color: colors.text, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  textDark: { color: colors.textDark },
  sectionHeader: { ...typography.small, fontWeight: '600', color: colors.textSecondary, textTransform: 'uppercase', letterSpacing: 0.8, marginHorizontal: spacing.md, marginTop: spacing.lg, marginBottom: spacing.xs },
  sectionHeaderDark: { color: '#9CA3AF' },
  section: { backgroundColor: colors.surface, marginHorizontal: spacing.md, borderRadius: radius.lg, overflow: 'hidden' },
  sectionDark: { backgroundColor: colors.surfaceDark },
  profileRow: { flexDirection: 'row', alignItems: 'center', padding: spacing.md },
  avatar: { width: 48, height: 48, borderRadius: radius.full, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center', marginRight: spacing.md },
  avatarText: { fontSize: 20, fontWeight: '700', color: '#fff' },
  profileInfo: { flex: 1 },
  profileName: { ...typography.body, fontWeight: '600', color: colors.text },
  profileEmail: { ...typography.small, color: colors.textSecondary },
  row: { flexDirection: 'row', alignItems: 'center', padding: spacing.md, gap: spacing.md },
  rowContent: { flex: 1 },
  rowLabel: { ...typography.body, color: colors.text, flex: 1 },
  rowSubtext: { ...typography.tiny, color: colors.textSecondary, marginTop: 2 },
  rowValue: { ...typography.body, color: colors.textSecondary },
  householdId: { ...typography.small, color: colors.primary, fontFamily: 'monospace' },
  chevron: { marginLeft: 'auto' },
  divider: { height: 1, backgroundColor: colors.border, marginHorizontal: spacing.md },
  signOutBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.sm, backgroundColor: colors.danger + '15', padding: spacing.md, borderRadius: radius.md },
  signOutText: { ...typography.body, color: colors.danger, fontWeight: '600' },
});
