/**
 * formatters.ts - Standardized formatting utilities for WindScope frontend.
 */

/**
 * Format an ISO date string (e.g. "2026-01-02") into unambiguous UK format ("2 Jan 2026").
 */
export function formatUnambiguousDate(isoDate: string): string {
  if (!isoDate) return '';
  const parts = isoDate.split('-');
  if (parts.length < 3) return isoDate;
  const year = parts[0];
  const monthIdx = parseInt(parts[1], 10) - 1;
  const day = parseInt(parts[2], 10);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const monthName = months[monthIdx] || parts[1];
  return `${day} ${monthName} ${year}`;
}

/**
 * Format an ISO timestamp string into unambiguous UK format ("25 Oct 2026").
 */
export function formatFetchDate(dateStr?: string): string {
  if (!dateStr) return '25 Oct 2026';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  } catch {
    return dateStr.slice(0, 10);
  }
}
