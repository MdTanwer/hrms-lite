import { useState, useEffect } from 'react';

/**
 * Returns a debounced value that updates after `delayMs` of no changes.
 * Cleans up the pending timeout on unmount or when value/delay changes.
 */
export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);

  return debouncedValue;
}
