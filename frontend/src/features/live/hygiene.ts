import type { LiveReading } from './serial';

// MVP reference ranges from the user-provided formula. Keep these visible in the UI
// and tune them against local sensor baselines before treating the score as operational.
export const HYGIENE_RANGES = {
  mq135Low: 300,
  mq135High: 1800,
  mq3Low: 300,
  mq3High: 1500,
  bmeGasCleanKohm: 150,
  bmeGasContaminatedKohm: 10,
  cleaningBonus: 10,
  humidityRisePct: 0.15,
  cleaningSignalHigh: 0.6,
};

export function normalize(value: number, low: number, high: number) {
  return Math.max(0, Math.min(1, (value - low) / (high - low)));
}

function signals(reading: LiveReading) {
  return {
    gas: normalize(reading.mq135_raw, HYGIENE_RANGES.mq135Low, HYGIENE_RANGES.mq135High),
    voc: reading.gas_resistance_kohm === null
      ? 0
      : normalize(HYGIENE_RANGES.bmeGasCleanKohm - reading.gas_resistance_kohm, 0,
        HYGIENE_RANGES.bmeGasCleanKohm - HYGIENE_RANGES.bmeGasContaminatedKohm),
    cleaning: normalize(reading.mq3_raw, HYGIENE_RANGES.mq3Low, HYGIENE_RANGES.mq3High),
  };
}

export type HygieneResult = {
  gas: number;
  voc: number;
  cleaning: number;
  dirtyIndex: number;
  rawScore: number;
  cleaningBonus: number;
  score: number;
  status: 'Clean' | 'Moderate' | 'Dirty';
  humidityRising: boolean;
  contaminationDecreasing: boolean;
  cleaningDetected: boolean;
  cause: string;
  alert: boolean;
};

export function calculateHygiene(reading: LiveReading, history: LiveReading[]): HygieneResult {
  const current = signals(reading);
  const previousReading = [...history].reverse().find((item) => item.received_at < reading.received_at);
  const previous = previousReading ? signals(previousReading) : null;
  const dirtyIndex = 0.5 * current.gas + 0.5 * current.voc;
  const rawScore = 100 - dirtyIndex * 100;
  const humidityRising = previousReading !== undefined
    && reading.humidity_pct - previousReading.humidity_pct >= HYGIENE_RANGES.humidityRisePct;
  const cleaningDetected = current.cleaning >= HYGIENE_RANGES.cleaningSignalHigh && humidityRising;
  const cleaningBonus = cleaningDetected ? HYGIENE_RANGES.cleaningBonus : 0;
  const score = Math.min(100, Math.max(0, Math.round(rawScore + cleaningBonus)));
  const status = score >= 80 ? 'Clean' : score >= 50 ? 'Moderate' : 'Dirty';
  const contaminationDecreasing = previous !== null && dirtyIndex < 0.5 * previous.gas + 0.5 * previous.voc - 0.01;

  let cause = 'No strong cause signal; continue monitoring the sensor trend.';
  if (cleaningDetected && contaminationDecreasing) {
    cause = 'Possible cleaning in progress: MQ-3 signal is high, humidity is rising, and contamination index is decreasing.';
  } else if (current.gas >= 0.65 && current.cleaning < HYGIENE_RANGES.cleaningSignalHigh) {
    cause = 'Possible odor/gas response while the cleaning signal is low; check flushing and ventilation.';
  } else if (previous && current.voc > previous.voc + 0.03 && current.cleaning < HYGIENE_RANGES.cleaningSignalHigh) {
    cause = 'VOC response is increasing while the cleaning signal is low; possible cleaning delay.';
  } else if (cleaningDetected) {
    cause = 'Possible cleaning activity detected; wait for the contamination index to decrease to confirm the trend.';
  }

  return {
    gas: current.gas,
    voc: current.voc,
    cleaning: current.cleaning,
    dirtyIndex,
    rawScore,
    cleaningBonus,
    score,
    status,
    humidityRising,
    contaminationDecreasing,
    cleaningDetected,
    cause,
    alert: status === 'Dirty',
  };
}
