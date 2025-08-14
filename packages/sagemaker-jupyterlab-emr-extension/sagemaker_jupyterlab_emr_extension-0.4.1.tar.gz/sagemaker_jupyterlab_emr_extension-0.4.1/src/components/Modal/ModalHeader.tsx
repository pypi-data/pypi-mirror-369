import React, { ReactElement } from 'react';
import { cx } from '@emotion/css';
import { Button } from '@jupyterlab/ui-components/lib/components/button';
import { closeIcon } from '@jupyterlab/ui-components';
import { v4 } from 'uuid';
import styles from './styles';

interface ButtonType {
  label?: string;
  onClick?: () => void;
  className?: string;
  component?: ReactElement | string;
}
interface ModalHeaderProps {
  readonly heading: string;
  readonly headingId?: string;
  readonly className?: string;
  readonly shouldDisplayCloseButton?: boolean;
  readonly onClickCloseButton?: () => void;
  readonly actionButtons?: Array<ButtonType>;
}

const ModalHeader: React.FC<ModalHeaderProps> = ({
  heading,
  headingId = 'modalHeading',
  className,
  shouldDisplayCloseButton = false,
  onClickCloseButton,
  actionButtons,
}) => {
  let closeButton = null;
  let buttons = null;
  if (shouldDisplayCloseButton) {
    closeButton = (
      <Button
        className={cx(styles.DismissButton, 'dismiss-button')}
        role="button"
        aria-label="close"
        onClick={onClickCloseButton}
        data-testid="close-button"
      >
        <closeIcon.react tag="span" />
      </Button>
    );
  }

  if (actionButtons) {
    buttons = actionButtons.map((cta) => {
      const { className, component, onClick, label } = cta;
      return component ? (
        <div key={`${v4()}`}>{component}</div>
      ) : (
        <Button className={className} type="button" role="button" onClick={onClick} aria-label={label} key={`${v4()}`}>
          {label}
        </Button>
      );
    });
  }

  return (
    <header className={cx(styles.Header, className)}>
      <h1 id={headingId}>{heading}</h1>
      <div className={cx(styles.HeaderButtons, 'header-btns')}>
        {buttons}
        {closeButton}
      </div>
    </header>
  );
};

export { ModalHeader, ModalHeaderProps, ButtonType };
