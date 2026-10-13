import { useState } from 'react';
import {
  Modal,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Switch,
  Platform,
  useColorScheme,
  Alert,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { Timestamp } from 'firebase/firestore';
import { addTask, updateTask, Task, TaskPriority } from '@/services/tasks';
import { taskToCalendarEvent, createEvent, updateEvent } from '@/services/googleCalendar';
import { scheduleTaskReminder } from '@/services/notifications';
import { colors, spacing, radius, typography } from '@/constants/theme';

interface Props {
  visible: boolean;
  onClose: () => void;
  householdId: string;
  userId: string;
  userName: string;
  members: Array<{ uid: string; displayName: string }>;
  editTask?: Task;
}

const priorities: TaskPriority[] = ['low', 'medium', 'high'];

export function AddTaskModal({ visible, onClose, householdId, userId, userName, members, editTask }: Props) {
  const isDark = useColorScheme() === 'dark';
  const [title, setTitle] = useState(editTask?.title ?? '');
  const [description, setDescription] = useState(editTask?.description ?? '');
  const [priority, setPriority] = useState<TaskPriority>(editTask?.priority ?? 'medium');
  const [assignedTo, setAssignedTo] = useState(editTask?.assignedTo ?? userId);
  const [hasDueDate, setHasDueDate] = useState(!!editTask?.dueDate);
  const [dueDate, setDueDate] = useState<Date>(editTask?.dueDate ? (editTask.dueDate as any).toDate() : new Date());
  const [syncCalendar, setSyncCalendar] = useState(false);
  const [showPicker, setShowPicker] = useState(false);
  const [loading, setLoading] = useState(false);

  const assignedMember = members.find((m) => m.uid === assignedTo);

  async function handleSave() {
    if (!title.trim()) return;
    setLoading(true);
    try {
      let calendarEventId: string | undefined = editTask?.calendarEventId;

      if (syncCalendar && hasDueDate) {
        const event = taskToCalendarEvent(title, dueDate, description);
        if (editTask?.calendarEventId) {
          await updateEvent(editTask.calendarEventId, event);
        } else {
          const created = await createEvent(event);
          calendarEventId = created.id;
        }
      }

      const payload = {
        householdId,
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        status: editTask?.status ?? 'pending' as const,
        assignedTo,
        assignedToName: assignedMember?.displayName ?? userName,
        dueDate: hasDueDate ? Timestamp.fromDate(dueDate) : undefined,
        calendarEventId,
        createdBy: editTask?.createdBy ?? userId,
      };

      if (editTask) {
        await updateTask(editTask.id, payload);
      } else {
        await addTask(payload);
        if (hasDueDate) {
          await scheduleTaskReminder(title, dueDate).catch(() => {});
        }
      }
      onClose();
    } catch (e) {
      Alert.alert('Error', 'Failed to save task. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setTitle(editTask?.title ?? '');
    setDescription(editTask?.description ?? '');
    setPriority(editTask?.priority ?? 'medium');
    setHasDueDate(!!editTask?.dueDate);
    setSyncCalendar(false);
  }

  const inputStyle = [styles.input, isDark && styles.inputDark];
  const labelStyle = [styles.label, isDark && styles.labelDark];

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet" onRequestClose={onClose}>
      <View style={[styles.container, isDark && styles.containerDark]}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => { reset(); onClose(); }}>
            <Text style={styles.cancel}>Cancel</Text>
          </TouchableOpacity>
          <Text style={[styles.title, isDark && styles.titleDark]}>
            {editTask ? 'Edit Task' : 'New Task'}
          </Text>
          <TouchableOpacity onPress={handleSave} disabled={!title.trim() || loading}>
            <Text style={[styles.save, (!title.trim() || loading) && styles.saveDisabled]}>
              {loading ? 'Saving…' : 'Save'}
            </Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.body} keyboardShouldPersistTaps="handled">
          <Text style={labelStyle}>Title *</Text>
          <TextInput
            style={inputStyle}
            placeholder="What needs to be done?"
            placeholderTextColor={colors.textSecondary}
            value={title}
            onChangeText={setTitle}
            autoFocus
          />

          <Text style={labelStyle}>Description</Text>
          <TextInput
            style={[inputStyle, styles.textarea]}
            placeholder="Optional details…"
            placeholderTextColor={colors.textSecondary}
            value={description}
            onChangeText={setDescription}
            multiline
            numberOfLines={3}
          />

          <Text style={labelStyle}>Priority</Text>
          <View style={styles.row}>
            {priorities.map((p) => (
              <TouchableOpacity
                key={p}
                style={[styles.chip, priority === p && styles.chipActive]}
                onPress={() => setPriority(p)}
              >
                <Text style={[styles.chipText, priority === p && styles.chipTextActive]}>
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={labelStyle}>Assign to</Text>
          <View style={styles.row}>
            {members.map((m) => (
              <TouchableOpacity
                key={m.uid}
                style={[styles.chip, assignedTo === m.uid && styles.chipActive]}
                onPress={() => setAssignedTo(m.uid)}
              >
                <Text style={[styles.chipText, assignedTo === m.uid && styles.chipTextActive]}>
                  {m.displayName.split(' ')[0]}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <View style={styles.switchRow}>
            <Text style={labelStyle}>Due date</Text>
            <Switch value={hasDueDate} onValueChange={setHasDueDate} trackColor={{ true: colors.primary }} />
          </View>

          {hasDueDate && (
            <>
              <TouchableOpacity style={inputStyle} onPress={() => setShowPicker(true)}>
                <Text style={isDark ? styles.labelDark : styles.label}>
                  {dueDate.toLocaleDateString()} {dueDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Text>
              </TouchableOpacity>
              {showPicker && (
                <DateTimePicker
                  value={dueDate}
                  mode="datetime"
                  display={Platform.OS === 'ios' ? 'inline' : 'default'}
                  onChange={(_, date) => { setShowPicker(false); if (date) setDueDate(date); }}
                  minimumDate={new Date()}
                />
              )}

              <View style={styles.switchRow}>
                <Text style={labelStyle}>Sync to Google Calendar</Text>
                <Switch value={syncCalendar} onValueChange={setSyncCalendar} trackColor={{ true: colors.primary }} />
              </View>
            </>
          )}
        </ScrollView>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  containerDark: { backgroundColor: colors.backgroundDark },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  cancel: { color: colors.textSecondary, ...typography.body },
  title: { ...typography.h3, color: colors.text },
  titleDark: { color: colors.textDark },
  save: { color: colors.primary, ...typography.body, fontWeight: '600' },
  saveDisabled: { opacity: 0.4 },
  body: { padding: spacing.md },
  label: { ...typography.small, fontWeight: '600', color: colors.text, marginBottom: spacing.xs, marginTop: spacing.md },
  labelDark: { ...typography.small, fontWeight: '600', color: colors.textDark, marginBottom: spacing.xs, marginTop: spacing.md },
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
  textarea: { minHeight: 80, textAlignVertical: 'top' },
  row: { flexDirection: 'row', gap: spacing.sm, flexWrap: 'wrap' },
  chip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { ...typography.small, color: colors.text },
  chipTextActive: { color: '#fff', fontWeight: '600' },
  switchRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: spacing.md },
});
