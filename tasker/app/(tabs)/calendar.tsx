import { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  useColorScheme,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Calendar } from 'react-native-calendars';
import { format, isSameDay, parseISO } from 'date-fns';
import { getUpcomingEvents, CalendarEvent } from '@/services/googleCalendar';
import { useTasks } from '@/hooks/useTasks';
import { useAuthStore } from '@/store/authStore';
import { colors, spacing, radius, typography } from '@/constants/theme';

interface MarkedDate {
  marked?: boolean;
  dotColor?: string;
  selected?: boolean;
  selectedColor?: string;
}

export default function CalendarScreen() {
  const isDark = useColorScheme() === 'dark';
  const { householdId } = useAuthStore();
  const { pending } = useTasks(householdId);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loadingEvents, setLoadingEvents] = useState(true);
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [errorEvents, setErrorEvents] = useState(false);

  useEffect(() => {
    getUpcomingEvents(50)
      .then(setEvents)
      .catch(() => setErrorEvents(true))
      .finally(() => setLoadingEvents(false));
  }, []);

  const markedDates: Record<string, MarkedDate> = {};

  pending.forEach((task) => {
    if (task.dueDate) {
      const d = format((task.dueDate as any).toDate(), 'yyyy-MM-dd');
      markedDates[d] = { marked: true, dotColor: colors.primary };
    }
  });

  events.forEach((ev) => {
    const d = ev.start.dateTime ? format(parseISO(ev.start.dateTime), 'yyyy-MM-dd') : null;
    if (d) {
      markedDates[d] = {
        ...markedDates[d],
        marked: true,
        dotColor: markedDates[d]?.dotColor ?? colors.secondary,
      };
    }
  });

  if (selectedDate) {
    markedDates[selectedDate] = {
      ...markedDates[selectedDate],
      selected: true,
      selectedColor: colors.primary,
    };
  }

  const selectedDateObj = parseISO(selectedDate);

  const tasksForDay = pending.filter((t) => {
    if (!t.dueDate) return false;
    return isSameDay((t.dueDate as any).toDate(), selectedDateObj);
  });

  const eventsForDay = events.filter((ev) => {
    if (!ev.start.dateTime) return false;
    return isSameDay(parseISO(ev.start.dateTime), selectedDateObj);
  });

  return (
    <SafeAreaView style={[styles.container, isDark && styles.containerDark]} edges={['top']}>
      <Text style={[styles.title, isDark && styles.titleDark]}>Calendar</Text>

      <Calendar
        current={selectedDate}
        onDayPress={(day: { dateString: string }) => setSelectedDate(day.dateString)}
        markedDates={markedDates}
        theme={{
          backgroundColor: isDark ? colors.backgroundDark : colors.background,
          calendarBackground: isDark ? colors.backgroundDark : colors.background,
          textSectionTitleColor: colors.textSecondary,
          selectedDayBackgroundColor: colors.primary,
          selectedDayTextColor: '#fff',
          todayTextColor: colors.primary,
          dayTextColor: isDark ? colors.textDark : colors.text,
          dotColor: colors.primary,
          arrowColor: colors.primary,
          monthTextColor: isDark ? colors.textDark : colors.text,
        }}
      />

      <View style={styles.daySection}>
        <Text style={[styles.dayTitle, isDark && styles.titleDark]}>
          {format(selectedDateObj, 'EEEE, MMMM d')}
        </Text>

        {tasksForDay.length === 0 && eventsForDay.length === 0 ? (
          <Text style={[styles.nothingText, isDark && styles.nothingDark]}>Nothing scheduled</Text>
        ) : (
          <FlatList
            data={[
              ...tasksForDay.map((t) => ({ type: 'task' as const, id: t.id, title: t.title, time: (t.dueDate as any).toDate() })),
              ...eventsForDay.map((e) => ({ type: 'event' as const, id: e.id ?? e.summary, title: e.summary, time: parseISO(e.start.dateTime) })),
            ].sort((a, b) => a.time.getTime() - b.time.getTime())}
            keyExtractor={(item) => `${item.type}-${item.id}`}
            renderItem={({ item }) => (
              <View style={[styles.eventRow, isDark && styles.eventRowDark]}>
                <View style={[styles.typeDot, { backgroundColor: item.type === 'task' ? colors.primary : colors.secondary }]} />
                <View style={styles.eventInfo}>
                  <Text style={[styles.eventTitle, isDark && styles.titleDark]}>{item.title}</Text>
                  <Text style={styles.eventTime}>{format(item.time, 'h:mm a')}</Text>
                </View>
                <View style={[styles.typeTag, { backgroundColor: (item.type === 'task' ? colors.primary : colors.secondary) + '22' }]}>
                  <Text style={[styles.typeTagText, { color: item.type === 'task' ? colors.primary : colors.secondary }]}>
                    {item.type === 'task' ? 'Task' : 'Event'}
                  </Text>
                </View>
              </View>
            )}
          />
        )}

        {errorEvents && (
          <Text style={styles.errorText}>Google Calendar unavailable — check sign-in permissions</Text>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  containerDark: { backgroundColor: colors.backgroundDark },
  title: { ...typography.h2, color: colors.text, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  titleDark: { color: colors.textDark },
  daySection: { flex: 1, padding: spacing.md },
  dayTitle: { ...typography.h3, color: colors.text, marginBottom: spacing.md },
  nothingText: { ...typography.body, color: colors.textSecondary, textAlign: 'center', marginTop: spacing.xl },
  nothingDark: { color: '#9CA3AF' },
  eventRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
    gap: spacing.md,
  },
  eventRowDark: { backgroundColor: colors.surfaceDark },
  typeDot: { width: 10, height: 10, borderRadius: 5 },
  eventInfo: { flex: 1 },
  eventTitle: { ...typography.body, fontWeight: '600', color: colors.text },
  eventTime: { ...typography.small, color: colors.textSecondary },
  typeTag: { paddingHorizontal: spacing.sm, paddingVertical: 2, borderRadius: radius.full },
  typeTagText: { ...typography.tiny, fontWeight: '600' },
  errorText: { ...typography.small, color: colors.danger, textAlign: 'center', marginTop: spacing.md },
});
