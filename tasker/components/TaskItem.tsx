import { View, Text, TouchableOpacity, StyleSheet, useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Task, completeTask, deleteTask } from '@/services/tasks';
import { colors, spacing, radius, typography } from '@/constants/theme';
import { format } from 'date-fns';

interface Props {
  task: Task;
  onEdit: (task: Task) => void;
}

const priorityColors: Record<string, string> = {
  high: colors.danger,
  medium: colors.warning,
  low: colors.secondary,
};

export function TaskItem({ task, onEdit }: Props) {
  const isDark = useColorScheme() === 'dark';
  const isDone = task.status === 'done';

  return (
    <View style={[styles.container, isDark && styles.containerDark, isDone && styles.containerDone]}>
      <TouchableOpacity
        style={[styles.checkbox, isDone && styles.checkboxDone]}
        onPress={() => !isDone && completeTask(task.id)}
      >
        {isDone && <Ionicons name="checkmark" size={16} color="#fff" />}
      </TouchableOpacity>

      <View style={styles.content}>
        <Text style={[styles.title, isDark && styles.textDark, isDone && styles.titleDone]}>
          {task.title}
        </Text>
        {task.description ? (
          <Text style={[styles.description, isDark && styles.descDark]} numberOfLines={2}>
            {task.description}
          </Text>
        ) : null}
        <View style={styles.meta}>
          <View style={[styles.priorityBadge, { backgroundColor: priorityColors[task.priority] + '22' }]}>
            <Text style={[styles.priorityText, { color: priorityColors[task.priority] }]}>
              {task.priority}
            </Text>
          </View>
          {task.assignedToName && (
            <Text style={[styles.metaText, isDark && styles.metaDark]}>👤 {task.assignedToName}</Text>
          )}
          {task.dueDate && (
            <Text style={[styles.metaText, isDark && styles.metaDark]}>
              📅 {format((task.dueDate as any).toDate(), 'MMM d')}
            </Text>
          )}
          {task.calendarEventId && (
            <Ionicons name="calendar" size={12} color={colors.primary} />
          )}
        </View>
      </View>

      <View style={styles.actions}>
        {!isDone && (
          <TouchableOpacity onPress={() => onEdit(task)} style={styles.actionBtn}>
            <Ionicons name="pencil-outline" size={18} color={colors.textSecondary} />
          </TouchableOpacity>
        )}
        <TouchableOpacity onPress={() => deleteTask(task.id)} style={styles.actionBtn}>
          <Ionicons name="trash-outline" size={18} color={colors.danger} />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  containerDark: { backgroundColor: colors.surfaceDark },
  containerDone: { opacity: 0.6 },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: radius.full,
    borderWidth: 2,
    borderColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
    marginTop: 2,
    flexShrink: 0,
  },
  checkboxDone: { backgroundColor: colors.primary, borderColor: colors.primary },
  content: { flex: 1 },
  title: { ...typography.body, fontWeight: '600', color: colors.text, marginBottom: 2 },
  textDark: { color: colors.textDark },
  titleDone: { textDecorationLine: 'line-through', color: colors.textSecondary },
  description: { ...typography.small, color: colors.textSecondary, marginBottom: spacing.xs },
  descDark: { color: '#9CA3AF' },
  meta: { flexDirection: 'row', alignItems: 'center', flexWrap: 'wrap', gap: spacing.xs },
  priorityBadge: { paddingHorizontal: spacing.xs, paddingVertical: 2, borderRadius: radius.sm },
  priorityText: { ...typography.tiny, fontWeight: '600', textTransform: 'capitalize' },
  metaText: { ...typography.tiny, color: colors.textSecondary },
  metaDark: { color: '#9CA3AF' },
  actions: { flexDirection: 'row', gap: spacing.xs, marginLeft: spacing.sm },
  actionBtn: { padding: spacing.xs },
});
