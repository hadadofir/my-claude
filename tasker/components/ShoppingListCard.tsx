import { View, Text, TouchableOpacity, StyleSheet, useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ShoppingList } from '@/services/shopping';
import { colors, spacing, radius, typography } from '@/constants/theme';

interface Props {
  list: ShoppingList;
  itemCount: number;
  checkedCount: number;
  onPress: () => void;
  onDelete: () => void;
}

export function ShoppingListCard({ list, itemCount, checkedCount, onPress, onDelete }: Props) {
  const isDark = useColorScheme() === 'dark';
  const progress = itemCount > 0 ? checkedCount / itemCount : 0;

  return (
    <TouchableOpacity
      style={[styles.container, isDark && styles.containerDark]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      <View style={styles.top}>
        <View style={styles.info}>
          <Text style={[styles.name, isDark && styles.textDark]}>{list.name}</Text>
          {list.locationName && (
            <View style={styles.locationRow}>
              <Ionicons name="location-outline" size={12} color={colors.primary} />
              <Text style={styles.locationText}>{list.locationName}</Text>
            </View>
          )}
        </View>
        <View style={styles.actions}>
          <View style={styles.badge}>
            <Text style={styles.badgeText}>{itemCount - checkedCount} left</Text>
          </View>
          <TouchableOpacity onPress={onDelete} style={styles.deleteBtn} hitSlop={8}>
            <Ionicons name="trash-outline" size={16} color={colors.danger} />
          </TouchableOpacity>
        </View>
      </View>

      {itemCount > 0 && (
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${progress * 100}%` as any }]} />
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: spacing.md,
    marginBottom: spacing.sm,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  containerDark: { backgroundColor: colors.surfaceDark },
  top: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  info: { flex: 1 },
  name: { ...typography.h3, color: colors.text, marginBottom: 4 },
  textDark: { color: colors.textDark },
  locationRow: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  locationText: { ...typography.tiny, color: colors.primary },
  actions: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  badge: {
    backgroundColor: colors.primary + '22',
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: radius.full,
  },
  badgeText: { ...typography.tiny, color: colors.primary, fontWeight: '600' },
  deleteBtn: { padding: 4 },
  progressBar: { height: 4, backgroundColor: colors.border, borderRadius: 2, marginTop: spacing.sm },
  progressFill: { height: 4, backgroundColor: colors.secondary, borderRadius: 2 },
});
