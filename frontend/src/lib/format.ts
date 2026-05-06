const sessionDateTimeFormatter = new Intl.DateTimeFormat("es-CO", {
  day: "numeric",
  month: "long",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

export function formatSessionDateTime(value: string | null): string {
  if (!value) return "Sin fecha programada";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Sin fecha programada";
  return sessionDateTimeFormatter.format(date);
}

export function formatDurationMinutes(minutes: number | null): string | null {
  if (minutes == null) return null;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours === 0) return `${mins} min`;
  if (mins === 0) return `${hours} h`;
  return `${hours} h ${mins} min`;
}

export function formatSessionMeta(
  scheduledAt: string | null,
  durationMinutes: number | null,
): string {
  const dateLabel = formatSessionDateTime(scheduledAt);
  const durationLabel = formatDurationMinutes(durationMinutes);
  return durationLabel ? `${dateLabel} • ${durationLabel}` : dateLabel;
}
