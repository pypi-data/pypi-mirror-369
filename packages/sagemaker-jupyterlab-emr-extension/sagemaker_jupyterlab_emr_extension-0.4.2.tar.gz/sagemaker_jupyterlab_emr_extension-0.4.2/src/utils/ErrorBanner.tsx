import { IconButton } from '@mui/material';
import React, { useEffect, useState } from 'react';
import * as styles from '../styles';
import { closeIcon } from '@jupyterlab/ui-components';

export interface IErrorBannerProps {
  error?: string;
}

export const ErrorBanner = (props: IErrorBannerProps) => {
  const [acknowledged, setAcknowledged] = useState(false);
  const { error } = props;

  useEffect(() => {
    setAcknowledged(false);
  }, [error]);

  const onCancelClick = () => {
    setAcknowledged(true);
  };

  return error && !acknowledged ? (
    <div className={styles.ErrorBannerContainer}>
      <p className={styles.ErrorBannerMessage}>{error}</p>

      <IconButton sx={{ padding: '4px', color: 'inherit' }} onClick={onCancelClick}>
        <closeIcon.react elementPosition="center" tag="span" />
      </IconButton>
    </div>
  ) : null;
};
