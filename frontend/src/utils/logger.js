// Logger utility for frontend
const LOG_LEVELS = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR'
};

class Logger {
  constructor() {
    this.logs = [];
    this.maxLogs = 1000; // Keep last 1000 logs in memory
  }

  log(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      data
    };

    // Add to in-memory logs
    this.logs.push(logEntry);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift(); // Remove oldest log
    }

    // Log to console
    switch (level) {
      case LOG_LEVELS.DEBUG:
        console.debug(`[${timestamp}] ${message}`, data);
        break;
      case LOG_LEVELS.INFO:
        console.info(`[${timestamp}] ${message}`, data);
        break;
      case LOG_LEVELS.WARN:
        console.warn(`[${timestamp}] ${message}`, data);
        break;
      case LOG_LEVELS.ERROR:
        console.error(`[${timestamp}] ${message}`, data);
        break;
      default:
        console.log(`[${timestamp}] ${message}`, data);
    }

    // Send to backend if it's an error
    if (level === LOG_LEVELS.ERROR) {
      this.sendToBackend(logEntry);
    }
  }

  async sendToBackend(logEntry) {
    try {
      const response = await fetch('http://localhost:8000/api/logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logEntry),
      });
      if (!response.ok) {
        console.error('Failed to send log to backend');
      }
    } catch (error) {
      console.error('Error sending log to backend:', error);
    }
  }

  debug(message, data = null) {
    this.log(LOG_LEVELS.DEBUG, message, data);
  }

  info(message, data = null) {
    this.log(LOG_LEVELS.INFO, message, data);
  }

  warn(message, data = null) {
    this.log(LOG_LEVELS.WARN, message, data);
  }

  error(message, data = null) {
    this.log(LOG_LEVELS.ERROR, message, data);
  }

  getLogs() {
    return this.logs;
  }

  clearLogs() {
    this.logs = [];
  }
}

export const logger = new Logger();