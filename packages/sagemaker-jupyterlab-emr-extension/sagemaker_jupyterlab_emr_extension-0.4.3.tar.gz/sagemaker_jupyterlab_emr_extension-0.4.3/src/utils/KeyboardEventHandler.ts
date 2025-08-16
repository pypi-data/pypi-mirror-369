enum KeyCode {
  tab = 'Tab',
  enter = 'Enter',
  escape = 'Escape',
  arrowDown = 'ArrowDown',
}
interface KeyboardNavigationProps {
  keyboardEvent: KeyboardEvent | React.KeyboardEvent<Element>;
  onEscape?: Function;
  onShiftTab?: Function;
  onShiftEnter?: Function;
  onTab?: Function;
  onEnter?: Function;
}

const handleKeyboardEvent = ({
  keyboardEvent,
  onEscape,
  onShiftTab,
  onShiftEnter,
  onTab,
  onEnter: onEnter,
}: KeyboardNavigationProps) => {
  const { key, shiftKey } = keyboardEvent;

  if (shiftKey) {
    if (key === KeyCode.tab && onShiftTab) {
      onShiftTab();
    } else if (key === KeyCode.enter && onShiftEnter) {
      onShiftEnter();
    }
  } else {
    if (key === KeyCode.tab && onTab) {
      onTab();
    } else if (key === KeyCode.enter && onEnter) {
      onEnter();
    } else if (key === KeyCode.escape && onEscape) {
      onEscape();
    }
  }
};

export { handleKeyboardEvent };
