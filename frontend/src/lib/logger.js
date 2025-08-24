import fs from 'fs';
import path from 'path';

const logDir = path.resolve('logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

const logFile = path.join(logDir, 'webui.log');

function write(level, ...args) {
  const message = args
    .map((arg) => {
      if (arg instanceof Error) return arg.stack || arg.message;
      if (typeof arg === 'object') return JSON.stringify(arg);
      return String(arg);
    })
    .join(' ');
  const line = `[${new Date().toISOString()}] [${level.toUpperCase()}] ${message}\n`;
  fs.appendFileSync(logFile, line);
}

export function info(...args) {
  write('info', ...args);
}

export function warn(...args) {
  write('warn', ...args);
}

export function error(...args) {
  write('error', ...args);
}
