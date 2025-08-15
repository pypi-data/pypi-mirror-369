import { strHasLength, arrayHasLength } from '../CommonUtils';
import { objectHasProperties, isNumber, isFn, setHasItem, isDefined, isObject, isNotEmpty } from '../TypeGuards';

describe('CommonUtils', () => {
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

  describe('objectHasProperties', () => {
    it('should return true for objects with properties', () => {
      const obj = { prop1: 'value1', prop2: 'value2' };

      const result = objectHasProperties(obj);

      expect(result).toBe(true);
    });

    it('should return false for empty objects', () => {
      const obj = {};

      const result = objectHasProperties(obj);

      expect(result).toBe(false);
    });

    it('should return false for non-object inputs', () => {
      const notAnObject = 'not an object';

      const result = objectHasProperties(notAnObject);

      expect(result).toBe(false);
    });
  });

  describe('isNumber', () => {
    it('should return true for numbers', () => {
      const num = 42;

      const result = isNumber(num);

      expect(result).toBe(true);
    });

    it('should return false for non-number inputs', () => {
      const notANumber = 'not a number';

      const result = isNumber(notANumber);

      expect(result).toBe(false);
    });
  });

  describe('isFn', () => {
    it('should return true for functions', () => {
      const func = () => {};

      const result = isFn(func);

      expect(result).toBe(true);
    });

    it('should return false for non-function inputs', () => {
      const notAFunction = 42;

      const result = isFn(notAFunction);

      expect(result).toBe(false);
    });
  });

  describe('setHasItem', () => {
    it('should return true if the set has the item', () => {
      const set = new Set([1, 2, 3]);

      const result = setHasItem(set, 2);

      expect(result).toBe(true);
    });

    it('should return false if the set does not have the item', () => {
      const set = new Set([1, 2, 3]);

      const result = setHasItem(set, 4);

      expect(result).toBe(false);
    });
  });

  describe('isDefined', () => {
    it('should return true for defined values', () => {
      const value = 42;

      const result = isDefined(value);

      expect(result).toBe(true);
    });

    it('should return false for undefined values', () => {
      const value = undefined;

      const result = isDefined(value);

      expect(result).toBe(false);
    });
  });

  describe('isObject', () => {
    it('should return true for objects', () => {
      const obj = { key: 'value' };

      const result = isObject(obj);

      expect(result).toBe(true);
    });

    it('should return false for non-object inputs', () => {
      const notAnObject = 42;

      const result = isObject(notAnObject);

      expect(result).toBe(false);
    });
  });

  describe('isNotEmpty', () => {
    it('should return true for non-empty values', () => {
      const value = 'Hello, World!';

      const result = isNotEmpty(value);

      expect(result).toBe(true);
    });

    it('should return false for null values', () => {
      const value = null;

      const result = isNotEmpty(value);

      expect(result).toBe(false);
    });

    it('should return false for undefined values', () => {
      const value = undefined;

      const result = isNotEmpty(value);

      expect(result).toBe(false);
    });
  });
});
