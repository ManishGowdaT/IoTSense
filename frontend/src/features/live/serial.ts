export type LiveReading = {
  sequence: number;
  mq3_raw: number;
  mq135_raw: number;
  mq3_pin_voltage_v: number;
  mq3_sensor_voltage_v: number;
  mq135_pin_voltage_v: number;
  mq135_sensor_voltage_v: number;
  temperature_c: number;
  humidity_pct: number;
  pressure_hpa: number;
  gas_resistance_kohm: number | null;
  bme680_simulated: boolean;
  received_at: number;
};

type SerialReader = ReadableStreamDefaultReader<Uint8Array>;
type SerialPortLike = {
  open(options: { baudRate: number }): Promise<void>;
  close(): Promise<void>;
  readable: ReadableStream<Uint8Array> | null;
};
type SerialApi = { requestPort(): Promise<SerialPortLike> };

// BME680 is unavailable on this device. Keep its demo values smooth and within
// plausible indoor ranges; MQ ADC counts continue to come directly from serial.
function simulatedBme(at: number) {
  const slow = at / 240_000;
  const medium = at / 95_000;
  return {
    temperature_c: 24.5 + 1.1 * Math.sin(slow),
    humidity_pct: 52 + 6 * Math.sin(medium + 0.8),
    pressure_hpa: 1013 + 3 * Math.sin(slow * 0.55 + 1.2),
    gas_resistance_kohm: 85 + 18 * Math.sin(medium * 0.7 + 0.4),
  };
}

declare global {
  interface Navigator { serial?: SerialApi }
}

export async function connectSerial(onReading: (reading: LiveReading) => void, onStatus: (message: string) => void) {
  if (!navigator.serial) throw new Error('Web Serial is unavailable. Open this page in Chrome or Edge on localhost, then try again.');
  const port = await navigator.serial.requestPort();
  try {
    await port.open({ baudRate: 115200 });
  } catch (error) {
    const detail = error instanceof Error ? ` (${error.message})` : '';
    throw new Error(`Could not open the ESP32 serial port. Close Arduino Serial Monitor/Serial Plotter and any other app using this COM port, then reconnect. Confirm the selected port is the ESP32.${detail}`);
  }
  const reader: SerialReader | null = port.readable?.getReader() ?? null;
  if (!reader) {
    await port.close();
    throw new Error('The selected serial port did not provide a readable stream.');
  }

  let buffer = '';
  const decoder = new TextDecoder();
  let stopped = false;
  let closing = false;
  let sequence = 0;
  let partial: { mq3?: number; mq3Pin?: number; mq3Out?: number; mq135?: number; mq135Pin?: number; mq135Out?: number; temperature?: number; humidity?: number; pressure?: number; gas?: number; bmeOffline?: boolean } = {};
  const mq3Ratio = (10 + 18) / 18;
  const mq135Ratio = (10 + 22) / 22;

  const emitTextReading = () => {
    if (partial.mq3 === undefined || partial.mq135 === undefined) return;
    const receivedAt = Date.now();
    const bme = simulatedBme(receivedAt);
    onReading({
      sequence: sequence++,
      mq3_raw: partial.mq3,
      mq135_raw: partial.mq135,
      mq3_pin_voltage_v: partial.mq3Pin ?? (partial.mq3 / 4095) * 3.3,
      mq3_sensor_voltage_v: partial.mq3Out ?? ((partial.mq3 / 4095) * 3.3 * mq3Ratio),
      mq135_pin_voltage_v: partial.mq135Pin ?? (partial.mq135 / 4095) * 3.3,
      mq135_sensor_voltage_v: partial.mq135Out ?? ((partial.mq135 / 4095) * 3.3 * mq135Ratio),
      ...bme,
      bme680_simulated: true,
      received_at: receivedAt,
    });
    partial = {};
  };

  const parseLine = (rawLine: string) => {
    const line = rawLine.trim();
    if (!line) { emitTextReading(); return; }

    try {
      const data = JSON.parse(line) as Record<string, unknown>;
      if (data.type === 'iotsense_ready') onStatus('ESP32 connected · waiting for first reading');
      if (data.type !== 'telemetry') return;
      if (!['sequence', 'mq3_raw', 'mq135_raw'].every((key) => typeof data[key] === 'number' && Number.isFinite(data[key]))) return;
      const receivedAt = Date.now();
      const bme = simulatedBme(receivedAt);
      onReading({
        sequence: data.sequence as number,
        mq3_raw: data.mq3_raw as number,
        mq135_raw: data.mq135_raw as number,
        mq3_pin_voltage_v: typeof data.mq3_pin_voltage_v === 'number' ? data.mq3_pin_voltage_v : ((data.mq3_raw as number) / 4095) * 3.3,
        mq3_sensor_voltage_v: typeof data.mq3_sensor_voltage_v === 'number' ? data.mq3_sensor_voltage_v : ((data.mq3_raw as number) / 4095) * 3.3 * mq3Ratio,
        mq135_pin_voltage_v: typeof data.mq135_pin_voltage_v === 'number' ? data.mq135_pin_voltage_v : ((data.mq135_raw as number) / 4095) * 3.3,
        mq135_sensor_voltage_v: typeof data.mq135_sensor_voltage_v === 'number' ? data.mq135_sensor_voltage_v : ((data.mq135_raw as number) / 4095) * 3.3 * mq135Ratio,
        ...bme,
        bme680_simulated: true,
        received_at: receivedAt,
      });
      return;
    } catch { /* This sketch uses readable text rather than JSON. */ }

    const mq3 = line.match(/MQ-3\b.*?Raw\s*=\s*(\d+)/i);
    const mq135 = line.match(/MQ-135\b.*?Raw\s*=\s*(\d+)/i);
    const mq3Volts = /MQ-3\b/i.test(line) && line.match(/Pin\s*=\s*([\d.]+)\s*V\s*\|\s*Sensor\s*=\s*([\d.]+)\s*V/i);
    const mq135Volts = /MQ-135\b/i.test(line) && line.match(/Pin\s*=\s*([\d.]+)\s*V\s*\|\s*Sensor\s*=\s*([\d.]+)\s*V/i);
    const temperature = line.match(/Temperature\s*:\s*(-?\d+(?:\.\d+)?)/i);
    const humidity = line.match(/Humidity\s*:\s*(-?\d+(?:\.\d+)?)/i);
    const pressure = line.match(/Pressure\s*:\s*(-?\d+(?:\.\d+)?)/i);
    const gas = line.match(/Gas Resistance\s*:\s*([\d.]+)\s*KOhms/i);
    if (mq3) partial.mq3 = Number(mq3[1]);
    if (mq135) partial.mq135 = Number(mq135[1]);
    if (mq3Volts) { partial.mq3Pin = Number(mq3Volts[1]); partial.mq3Out = Number(mq3Volts[2]); }
    if (mq135Volts) { partial.mq135Pin = Number(mq135Volts[1]); partial.mq135Out = Number(mq135Volts[2]); }
    if (temperature) partial.temperature = Number(temperature[1]);
    if (humidity) partial.humidity = Number(humidity[1]);
    if (pressure) partial.pressure = Number(pressure[1]);
    if (gas) partial.gas = Number(gas[1]);
    if (/BME680:\s*Offline|Failed to perform BME680 reading/i.test(line)) {
      partial.bmeOffline = true;
      emitTextReading();
    }
  };

  const done = (async () => {
    try {
      while (!stopped) {
        const { value, done: streamDone } = await reader.read();
        if (streamDone) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split(/\r?\n/);
        buffer = lines.pop() ?? '';
        for (const line of lines) parseLine(line);
      }
    } catch (error) {
      if (!stopped) onStatus(error instanceof Error ? `Serial connection lost · ${error.message}` : 'Serial connection lost');
    }
  })();

  return {
    close: async () => {
      if (closing) return;
      closing = true;
      stopped = true;
      await reader.cancel().catch(() => undefined);
      await done.catch(() => undefined);
      reader.releaseLock();
      await port.close().catch(() => undefined);
    },
  };
}
