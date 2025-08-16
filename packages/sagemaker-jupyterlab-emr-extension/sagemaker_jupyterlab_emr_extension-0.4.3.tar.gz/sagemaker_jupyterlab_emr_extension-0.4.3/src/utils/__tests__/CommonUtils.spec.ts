import { getISOStringFromDate, strHasLength, arrayHasLength } from '../CommonUtils';
import isDate from 'lodash/isDate';

describe('getISOStringFromDate', () => {
  it('should return ISO string when a valid Date is provided', () => {
    const date = new Date();
    const expectedISOString = isDate(date) ? date.toISOString() : undefined;

    const result = getISOStringFromDate(date);

    expect(result).toBe(expectedISOString);
  });

  it('should return undefined when an invalid Date is provided', () => {
    const invalidDate = 'not a date';

    const result = getISOStringFromDate(invalidDate as any);

    expect(result).toBeUndefined();
  });

  it('should return undefined when no Date is provided', () => {
    const result = getISOStringFromDate();

    expect(result).toBeUndefined();
  });
});

describe('strHasLength', () => {
  it('should return true for non-empty strings', () => {
    const str = 'Hello, World!';

    const result = strHasLength(str);

    expect(result).toBe(true);
  });

  it('should return false for empty strings', () => {
    const str = '';

    const result = strHasLength(str);

    expect(result).toBe(false);
  });

  it('should return false for non-string inputs', () => {
    const notAString = 42;

    const result = strHasLength(notAString);

    expect(result).toBe(false);
  });
});

describe('arrayHasLength', () => {
  it('should return true for non-empty arrays', () => {
    const arr = [1, 2, 3];

    const result = arrayHasLength(arr);

    expect(result).toBe(true);
  });

  it('should return false for empty arrays', () => {
    const arr: number[] = [];

    const result = arrayHasLength(arr);

    expect(result).toBe(false);
  });

  it('should return false for non-array inputs', () => {
    const notAnArray = 'not an array';

    const result = arrayHasLength(notAnArray);

    expect(result).toBe(false);
  });
});
