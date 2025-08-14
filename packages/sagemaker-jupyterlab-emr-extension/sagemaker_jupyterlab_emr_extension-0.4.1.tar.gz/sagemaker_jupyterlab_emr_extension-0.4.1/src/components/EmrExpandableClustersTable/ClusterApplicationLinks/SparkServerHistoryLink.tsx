import React, { useState } from 'react';
import { cx } from '@emotion/css';
import { CircularProgress } from '@mui/material';
import { i18nStrings } from '../../../constants/i18n';
import { EmrClusterPluginClassNames } from '../../../constants/common';
import { EmrPresignedURL } from '../../EmrPresignedURL';
import { launcherIcon } from '@jupyterlab/ui-components';
import * as styles from './styles';

interface Props {
  clusterId: string;
  accountId: string;
  setIsError: (isError: boolean) => void;
}

const PERSISTENT_APP_UI_TYPE_SHS = 'SHS';
const expandClusterStrings = i18nStrings.Clusters.expandCluster;
const expandClusterHistoryClassNames = EmrClusterPluginClassNames.HistoryLink;

const SparkServerHistoryLink: React.FunctionComponent<Props> = ({ clusterId, accountId, setIsError }) => {
  const [isLoading] = useState(false);

  return (
    <div className={styles.linkContainer}>
      <div className={cx(expandClusterHistoryClassNames, styles.link)}>
        <EmrPresignedURL
          clusterId={clusterId}
          onError={(error) => error}
          accountId={accountId}
          persistentAppUIType={PERSISTENT_APP_UI_TYPE_SHS}
          label={expandClusterStrings.SparkHistoryServer}
        />
      </div>
      <launcherIcon.react tag="span" />
      {isLoading && (
        <span>
          <CircularProgress size="1rem" />
        </span>
      )}
    </div>
  );
};

export { SparkServerHistoryLink };
