// Record Agent: Save and load session data
export function saveSession(data) {
  localStorage.setItem('session', JSON.stringify(data));
}
export function loadSession() {
  return JSON.parse(localStorage.getItem('session'));
}