export function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleString();
}

export function formatNumber(num) {
  return num.toLocaleString();
}
