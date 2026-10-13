import { useState, useMemo } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  useColorScheme,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '@/store/authStore';
import { useTasks } from '@/hooks/useTasks';
import { TaskItem } from '@/components/TaskItem';
import { AddTaskModal } from '@/components/AddTaskModal';
import { Task } from '@/services/tasks';
import { colors, spacing, radius, typography } from '@/constants/theme';

type Filter = 'all' | 'mine' | 'pending' | 'done';

export default function TasksScreen() {
  const isDark = useColorScheme() === 'dark';
  const { user, householdId } = useAuthStore();
  const { tasks, loading } = useTasks(householdId);
  const [modalVisible, setModalVisible] = useState(false);
  const [editTask, setEditTask] = useState<Task | undefined>();
  const [filter, setFilter] = useState<Filter>('pending');

  const filtered = useMemo(() => {
    switch (filter) {
      case 'mine': return tasks.filter((t) => t.assignedTo === user?.uid && t.status !== 'done');
      case 'pending': return tasks.filter((t) => t.status !== 'done');
      case 'done': return tasks.filter((t) => t.status === 'done');
      default: return tasks;
    }
  }, [tasks, filter, user?.uid]);

  const filters: { key: Filter; label: string }[] = [
    { key: 'pending', label: 'Pending' },
    { key: 'mine', label: 'Mine' },
    { key: 'done', label: 'Done' },
    { key: 'all', label: 'All' },
  ];

  return (
    <SafeAreaView style={[styles.container, isDark && styles.containerDark]} edges={['top']}>
      <View style={styles.header}>
        <Text style={[styles.title, isDark && styles.titleDark]}>Tasks</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => { setEditTask(undefined); setModalVisible(true); }}
        >
          <Ionicons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <View style={styles.filters}>
        {filters.map((f) => (
          <TouchableOpacity
            key={f.key}
            style={[styles.filterChip, filter === f.key && styles.filterChipActive]}
            onPress={() => setFilter(f.key)}
          >
            <Text style={[styles.filterText, filter === f.key && styles.filterTextActive]}>
              {f.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading ? (
        <ActivityIndicator style={styles.loader} color={colors.primary} />
      ) : filtered.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>✓</Text>
          <Text style={[styles.emptyText, isDark && styles.titleDark]}>
            {filter === 'done' ? 'No completed tasks yet' : 'All clear! No tasks here'}
          </Text>
          {filter !== 'done' && (
            <TouchableOpacity onPress={() => { setEditTask(undefined); setModalVisible(true); }}>
              <Text style={styles.emptyAction}>Add your first task</Text>
            </TouchableOpacity>
          )}
        </View>
      ) : (
        <FlatList
          data={filtered}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <TaskItem
              task={item}
              onEdit={(t) => { setEditTask(t); setModalVisible(true); }}
            />
          )}
          contentContainerStyle={styles.list}
          showsVerticalScrollIndicator={false}
        />
      )}

      {user && householdId && (
        <AddTaskModal
          visible={modalVisible}
          onClose={() => setModalVisible(false)}
          householdId={householdId}
          userId={user.uid}
          userName={user.displayName ?? 'Me'}
          members={[{ uid: user.uid, displayName: user.displayName ?? 'Me' }]}
          editTask={editTask}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  containerDark: { backgroundColor: colors.backgroundDark },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  title: { ...typography.h2, color: colors.text },
  titleDark: { color: colors.textDark },
  addButton: {
    width: 40,
    height: 40,
    borderRadius: radius.full,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  filters: { flexDirection: 'row', paddingHorizontal: spacing.md, gap: spacing.sm, marginBottom: spacing.sm },
  filterChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  filterChipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  filterText: { ...typography.small, color: colors.textSecondary },
  filterTextActive: { color: '#fff', fontWeight: '600' },
  list: { paddingHorizontal: spacing.md, paddingBottom: spacing.xl },
  loader: { flex: 1 },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: spacing.sm },
  emptyIcon: { fontSize: 48 },
  emptyText: { ...typography.h3, color: colors.text },
  emptyAction: { color: colors.primary, ...typography.body },
});
