// Browser-safe logger: uses console and avoids Node-only modules
function normalize(args) {
  return args.map((arg) => {
    if (arg instanceof Error) return arg.stack || arg.message;
    if (typeof arg === 'object') {
      try {
        return JSON.stringify(arg);
      } catch {
        return String(arg);
      }
    }
    return String(arg);
  });
}

export function info(...args) {
  console.info(...normalize(args));
}

export function warn(...args) {
  console.warn(...normalize(args));
}

export function error(...args) {
  console.error(...normalize(args));
}
