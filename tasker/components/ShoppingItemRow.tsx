import { View, Text, TouchableOpacity, StyleSheet, useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ShoppingItem, toggleShoppingItem, deleteShoppingItem } from '@/services/shopping';
import { colors, spacing, radius, typography } from '@/constants/theme';

interface Props {
  item: ShoppingItem;
}

export function ShoppingItemRow({ item }: Props) {
  const isDark = useColorScheme() === 'dark';

  return (
    <View style={[styles.container, isDark && styles.containerDark]}>
      <TouchableOpacity
        style={[styles.checkbox, item.checked && styles.checkboxChecked]}
        onPress={() => toggleShoppingItem(item.id, !item.checked)}
      >
        {item.checked && <Ionicons name="checkmark" size={14} color="#fff" />}
      </TouchableOpacity>
      <View style={styles.content}>
        <Text style={[styles.name, isDark && styles.textDark, item.checked && styles.nameChecked]}>
          {item.name}
        </Text>
        {item.quantity && (
          <Text style={[styles.qty, isDark && styles.qtyDark]}>{item.quantity}</Text>
        )}
      </View>
      <TouchableOpacity onPress={() => deleteShoppingItem(item.id)} hitSlop={8}>
        <Ionicons name="close-circle-outline" size={18} color={colors.textSecondary} />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  containerDark: { backgroundColor: colors.surfaceDark, borderBottomColor: colors.borderDark },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: radius.sm,
    borderWidth: 2,
    borderColor: colors.secondary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  checkboxChecked: { backgroundColor: colors.secondary, borderColor: colors.secondary },
  content: { flex: 1 },
  name: { ...typography.body, color: colors.text },
  textDark: { color: colors.textDark },
  nameChecked: { textDecorationLine: 'line-through', color: colors.textSecondary },
  qty: { ...typography.tiny, color: colors.textSecondary },
  qtyDark: { color: '#9CA3AF' },
});
