import winston from 'winston';

const { combine, errors, colorize, printf } = winston.format;

const devFormat = printf(({ level, message, stack }) => {
  const log = `${level}: ${message}`;

  return stack
    ? `${log}\n${stack}`
    : log;
});

export const logger = winston.createLogger({
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