import { strHasLength, arrayHasLength } from './CommonUtils';

const objectHasProperties = <T>(obj: unknown): obj is T =>
  typeof obj === 'object' && !Array.isArray(obj) && obj != null && arrayHasLength(Object.keys(obj));

const isNumber = (x: unknown): x is number => typeof x === 'number';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const isFn = (x: unknown): x is (...args: any[]) => any => typeof x === 'function';

const setHasItem = <T>(set: Set<T>, key: any): key is T => set.has(key);

const isDefined = <T>(arg: T | undefined): arg is T => arg != null;

const isObject = (obj: unknown): obj is object => obj != null && !Array.isArray(obj) && typeof obj === 'object';

const isNotEmpty = <TValue>(value: TValue | null | undefined): value is TValue => value != null;

export {
  arrayHasLength,
  isDefined,
  isFn,
  isNumber,
  isObject,
  objectHasProperties,
  setHasItem,
  strHasLength,
  isNotEmpty,
};
