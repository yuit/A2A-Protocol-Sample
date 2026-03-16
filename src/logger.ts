import winston from 'winston';

const { combine, errors, colorize, printf, timestamp } = winston.format;

const isDebugMode = process.execArgv.some((arg) =>
  arg.includes('--inspect') || arg.includes('--debug'),
);

function formatArg(arg: unknown): string {
  if (arg === null) return 'null';
  if (arg === undefined) return 'undefined';
  if (typeof arg === 'object') return JSON.stringify(arg, null, 2);
  return String(arg);
}

const devFormat = printf(({ level, message, stack, timestamp: ts }) => {
  const header = ts ? `${ts} ${level}: ${message}` : `${level}: ${message}`;

  return stack ? `${header}\n${stack}` : header;
});

const winstonLogger = winston.createLogger({
  level: 'debug',
  format: combine(
    timestamp({
      format: () => new Date().toLocaleString(),
    }),
    errors({ stack: true }),
    colorize(),
    devFormat,
  ),
  transports: [
    // Console for warnings and errors only (avoids stdout noise for info/debug).
    new winston.transports.Console({ level: 'warn' }),
    // Info-level logs written to a file named "info".
    new winston.transports.File({
      filename: 'logs/info',
      level: 'info',
      options: { flags: 'w' },
    }),
    // Debug-level logs written to a file named "debug".
    new winston.transports.File({
      filename: 'logs/debug',
      level: 'debug',
      options: { flags: 'w' },
    }),
  ],
});

export const logger = {
  debug: (...args: unknown[]) => {
    if (!isDebugMode) return;
    winstonLogger.debug(args.map(formatArg).join(' '));
  },
  info: (...args: unknown[]) =>
    winstonLogger.info(args.map(formatArg).join(' ')),
  warn: (...args: unknown[]) => {
    const msg = args.map(formatArg).join(' ');
    console.error(msg);
    winstonLogger.warn(msg);
  },
  error: (...args: unknown[]) => {
    const msg = args.map(formatArg).join(' ');
    console.error(msg);
    winstonLogger.error(msg);
  },
};

// Capture any library output that uses console.log (e.g., dotenv debug)
// and route it through our error logger / stderr instead of stdout.
// eslint-disable-next-line no-console
console.log = (...args: unknown[]) => {
  logger.error(...args);
};
