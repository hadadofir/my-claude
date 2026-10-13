import { useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  useColorScheme,
  Modal,
  TextInput,
  ScrollView,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '@/store/authStore';
import { useShoppingLists, useShoppingItems } from '@/hooks/useShopping';
import {
  ShoppingList,
  ShoppingItem,
  addShoppingList,
  deleteShoppingList,
  addShoppingItem,
  clearCheckedItems,
} from '@/services/shopping';
import { ShoppingListCard } from '@/components/ShoppingListCard';
import { ShoppingItemRow } from '@/components/ShoppingItemRow';
import { colors, spacing, radius, typography } from '@/constants/theme';

export default function ShoppingScreen() {
  const isDark = useColorScheme() === 'dark';
  const { user, householdId } = useAuthStore();
  const { lists, loading } = useShoppingLists(householdId);
  const [selectedList, setSelectedList] = useState<ShoppingList | null>(null);
  const itemsByList = useShoppingItems(selectedList?.id ?? null, lists);
  const [showNewList, setShowNewList] = useState(false);
  const [newListName, setNewListName] = useState('');
  const [newListStore, setNewListStore] = useState('');
  const [newListLat, setNewListLat] = useState('');
  const [newListLng, setNewListLng] = useState('');
  const [newListRadius, setNewListRadius] = useState('300');
  const [newItemName, setNewItemName] = useState('');
  const [newItemQty, setNewItemQty] = useState('');

  const currentItems: ShoppingItem[] = selectedList ? (itemsByList[selectedList.id] ?? []) : [];
  const uncheckedCount = currentItems.filter((i) => !i.checked).length;
  const checkedCount = currentItems.filter((i) => i.checked).length;

  async function handleCreateList() {
    if (!newListName.trim() || !householdId || !user) return;
    const lat = parseFloat(newListLat);
    const lng = parseFloat(newListLng);
    const hasLocation = !isNaN(lat) && !isNaN(lng);
    await addShoppingList({
      householdId,
      name: newListName.trim(),
      locationName: newListStore.trim() || undefined,
      locationLat: hasLocation ? lat : undefined,
      locationLng: hasLocation ? lng : undefined,
      locationRadius: hasLocation ? parseInt(newListRadius) : undefined,
      createdBy: user.uid,
    });
    setNewListName('');
    setNewListStore('');
    setNewListLat('');
    setNewListLng('');
    setNewListRadius('300');
    setShowNewList(false);
  }

  async function handleAddItem() {
    if (!newItemName.trim() || !selectedList || !user) return;
    await addShoppingItem({
      listId: selectedList.id,
      householdId: selectedList.householdId,
      name: newItemName.trim(),
      quantity: newItemQty.trim() || undefined,
      checked: false,
      addedBy: user.uid,
    });
    setNewItemName('');
    setNewItemQty('');
  }

  const inputStyle = [styles.input, isDark && styles.inputDark];

  if (selectedList) {
    return (
      <SafeAreaView style={[styles.container, isDark && styles.containerDark]} edges={['top']}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => setSelectedList(null)} style={styles.backBtn}>
            <Ionicons name="arrow-back" size={24} color={isDark ? colors.textDark : colors.text} />
          </TouchableOpacity>
          <View style={styles.headerInfo}>
            <Text style={[styles.title, isDark && styles.titleDark]}>{selectedList.name}</Text>
            {selectedList.locationName && (
              <Text style={styles.storeLabel}>📍 {selectedList.locationName}</Text>
            )}
          </View>
          {checkedCount > 0 && (
            <TouchableOpacity
              onPress={() => clearCheckedItems(selectedList.id, currentItems)}
              style={styles.clearBtn}
            >
              <Text style={styles.clearText}>Clear done</Text>
            </TouchableOpacity>
          )}
        </View>

        <FlatList
          data={currentItems}
          keyExtractor={(i) => i.id}
          renderItem={({ item }) => <ShoppingItemRow item={item} />}
          ListEmptyComponent={
            <View style={styles.empty}>
              <Text style={styles.emptyIcon}>🛒</Text>
              <Text style={[styles.emptyText, isDark && styles.titleDark]}>List is empty</Text>
            </View>
          }
        />

        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
          <View style={[styles.addItemBar, isDark && styles.addItemBarDark]}>
            <TextInput
              style={[styles.addItemInput, isDark && styles.inputDark]}
              placeholder="Add item…"
              placeholderTextColor={colors.textSecondary}
              value={newItemName}
              onChangeText={setNewItemName}
              onSubmitEditing={handleAddItem}
              returnKeyType="done"
            />
            <TextInput
              style={[styles.addItemQty, isDark && styles.inputDark]}
              placeholder="Qty"
              placeholderTextColor={colors.textSecondary}
              value={newItemQty}
              onChangeText={setNewItemQty}
            />
            <TouchableOpacity
              style={[styles.addItemBtn, !newItemName.trim() && styles.addItemBtnDisabled]}
              onPress={handleAddItem}
              disabled={!newItemName.trim()}
            >
              <Ionicons name="add" size={22} color="#fff" />
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, isDark && styles.containerDark]} edges={['top']}>
      <View style={styles.header}>
        <Text style={[styles.title, isDark && styles.titleDark]}>Shopping</Text>
        <TouchableOpacity style={styles.addButton} onPress={() => setShowNewList(true)}>
          <Ionicons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      {loading ? (
        <ActivityIndicator style={styles.loader} color={colors.primary} />
      ) : lists.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>🛒</Text>
          <Text style={[styles.emptyText, isDark && styles.titleDark]}>No lists yet</Text>
          <TouchableOpacity onPress={() => setShowNewList(true)}>
            <Text style={styles.emptyAction}>Create your first list</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={lists}
          keyExtractor={(l) => l.id}
          renderItem={({ item }) => {
            const items = itemsByList[item.id] ?? [];
            return (
              <ShoppingListCard
                list={item}
                itemCount={items.length}
                checkedCount={items.filter((i) => i.checked).length}
                onPress={() => setSelectedList(item)}
                onDelete={() =>
                  Alert.alert('Delete list?', `Delete "${item.name}"?`, [
                    { text: 'Cancel', style: 'cancel' },
                    { text: 'Delete', style: 'destructive', onPress: () => deleteShoppingList(item.id) },
                  ])
                }
              />
            );
          }}
          contentContainerStyle={styles.list}
        />
      )}

      <Modal visible={showNewList} animationType="slide" presentationStyle="pageSheet">
        <View style={[styles.modal, isDark && styles.containerDark]}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowNewList(false)}>
              <Text style={styles.cancel}>Cancel</Text>
            </TouchableOpacity>
            <Text style={[styles.modalTitle, isDark && styles.titleDark]}>New List</Text>
            <TouchableOpacity onPress={handleCreateList} disabled={!newListName.trim()}>
              <Text style={[styles.saveText, !newListName.trim() && styles.saveDisabled]}>Create</Text>
            </TouchableOpacity>
          </View>
          <ScrollView style={styles.modalBody} keyboardShouldPersistTaps="handled">
            <Text style={[styles.label, isDark && styles.labelDark]}>List name *</Text>
            <TextInput
              style={inputStyle}
              placeholder="e.g. Weekly Groceries"
              placeholderTextColor={colors.textSecondary}
              value={newListName}
              onChangeText={setNewListName}
              autoFocus
            />
            <Text style={[styles.sectionTitle, isDark && styles.titleDark]}>
              Location-based reminders (optional)
            </Text>
            <Text style={[styles.hint, isDark && styles.hintDark]}>
              You'll get an opportunistic notification when you're near this store and the list has items.
            </Text>
            <Text style={[styles.label, isDark && styles.labelDark]}>Store name</Text>
            <TextInput
              style={inputStyle}
              placeholder="e.g. Whole Foods"
              placeholderTextColor={colors.textSecondary}
              value={newListStore}
              onChangeText={setNewListStore}
            />
            <Text style={[styles.label, isDark && styles.labelDark]}>Latitude</Text>
            <TextInput
              style={inputStyle}
              placeholder="e.g. 37.7749"
              placeholderTextColor={colors.textSecondary}
              value={newListLat}
              onChangeText={setNewListLat}
              keyboardType="decimal-pad"
            />
            <Text style={[styles.label, isDark && styles.labelDark]}>Longitude</Text>
            <TextInput
              style={inputStyle}
              placeholder="e.g. -122.4194"
              placeholderTextColor={colors.textSecondary}
              value={newListLng}
              onChangeText={setNewListLng}
              keyboardType="decimal-pad"
            />
            <Text style={[styles.label, isDark && styles.labelDark]}>Trigger radius (meters)</Text>
            <TextInput
              style={inputStyle}
              placeholder="300"
              placeholderTextColor={colors.textSecondary}
              value={newListRadius}
              onChangeText={setNewListRadius}
              keyboardType="number-pad"
            />
            <Text style={[styles.hint, isDark && styles.hintDark]}>
              💡 Tip: Open Google Maps, long-press your store to get its coordinates.
            </Text>
          </ScrollView>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  containerDark: { backgroundColor: colors.backgroundDark },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  headerInfo: { flex: 1, marginLeft: spacing.sm },
  backBtn: { padding: spacing.xs },
  title: { ...typography.h2, color: colors.text },
  titleDark: { color: colors.textDark },
  storeLabel: { ...typography.tiny, color: colors.primary },
  addButton: { width: 40, height: 40, borderRadius: radius.full, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center' },
  clearBtn: { paddingHorizontal: spacing.sm },
  clearText: { ...typography.small, color: colors.danger },
  list: { paddingHorizontal: spacing.md, paddingBottom: spacing.xl },
  loader: { flex: 1 },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: spacing.sm },
  emptyIcon: { fontSize: 48 },
  emptyText: { ...typography.h3, color: colors.text },
  emptyAction: { color: colors.primary, ...typography.body },
  addItemBar: { flexDirection: 'row', alignItems: 'center', padding: spacing.md, gap: spacing.sm, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  addItemBarDark: { backgroundColor: colors.surfaceDark, borderTopColor: colors.borderDark },
  addItemInput: { flex: 1, backgroundColor: colors.background, borderRadius: radius.md, paddingHorizontal: spacing.md, paddingVertical: spacing.sm, ...typography.body, color: colors.text },
  addItemQty: { width: 70, backgroundColor: colors.background, borderRadius: radius.md, paddingHorizontal: spacing.sm, paddingVertical: spacing.sm, ...typography.body, color: colors.text, textAlign: 'center' },
  addItemBtn: { width: 40, height: 40, borderRadius: radius.full, backgroundColor: colors.secondary, alignItems: 'center', justifyContent: 'center' },
  addItemBtnDisabled: { opacity: 0.4 },
  modal: { flex: 1, backgroundColor: colors.background },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border },
  modalTitle: { ...typography.h3, color: colors.text },
  cancel: { color: colors.textSecondary, ...typography.body },
  saveText: { color: colors.primary, ...typography.body, fontWeight: '600' },
  saveDisabled: { opacity: 0.4 },
  modalBody: { padding: spacing.md },
  sectionTitle: { ...typography.h3, color: colors.text, marginTop: spacing.lg, marginBottom: spacing.xs },
  label: { ...typography.small, fontWeight: '600', color: colors.text, marginBottom: spacing.xs, marginTop: spacing.md },
  labelDark: { ...typography.small, fontWeight: '600', color: colors.textDark, marginBottom: spacing.xs, marginTop: spacing.md },
  input: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, padding: spacing.md, ...typography.body, color: colors.text },
  inputDark: { backgroundColor: colors.surfaceDark, borderColor: colors.borderDark, color: colors.textDark },
  hint: { ...typography.small, color: colors.textSecondary, marginTop: spacing.sm },
  hintDark: { color: '#9CA3AF' },
});
