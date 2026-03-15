import winston from 'winston';

const { combine, errors, colorize, printf } = winston.format;

function formatArg(arg: unknown): string {
  if (arg === null) return 'null';
  if (arg === undefined) return 'undefined';
  if (typeof arg === 'object') return JSON.stringify(arg, null, 2);
  return String(arg);
}

const devFormat = printf(({ level, message, stack }) => {
  const log = `${level}: ${message}`;

  return stack
    ? `${log}\n${stack}`
    : log;
});

const winstonLogger = winston.createLogger({
  level: 'debug',
  format: combine(
    errors({ stack: true }),
    colorize(),
    devFormat
  ),
  transports: [
    new winston.transports.Console(),
  ],
});

export const logger = {
  debug: (...args: unknown[]) =>
    winstonLogger.debug(args.map(formatArg).join(' ')),
  info: (...args: unknown[]) =>
    winstonLogger.info(args.map(formatArg).join(' ')),
  warn: (...args: unknown[]) =>
    winstonLogger.warn(args.map(formatArg).join(' ')),
  error: (...args: unknown[]) =>
    winstonLogger.error(args.map(formatArg).join(' ')),
};