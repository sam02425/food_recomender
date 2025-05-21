// Social Agent: Generate a share link for results
export function getShareLink(results) {
  return `mailto:?subject=My Food Experience&body=${encodeURIComponent(JSON.stringify(results))}`;
}