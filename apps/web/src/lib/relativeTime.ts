const MINUTE = 60;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;
const MONTH = 30 * DAY;

const format = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

export function relativeTime(at: string, now: Date = new Date()): string {
  const then = new Date(at);
  const seconds = Math.round((now.getTime() - then.getTime()) / 1000);
  if (seconds < MINUTE) return "just now";
  if (seconds < HOUR) return format.format(-Math.floor(seconds / MINUTE), "minute");
  if (seconds < DAY) return format.format(-Math.floor(seconds / HOUR), "hour");
  if (seconds < MONTH) return format.format(-Math.floor(seconds / DAY), "day");
  return then.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}
