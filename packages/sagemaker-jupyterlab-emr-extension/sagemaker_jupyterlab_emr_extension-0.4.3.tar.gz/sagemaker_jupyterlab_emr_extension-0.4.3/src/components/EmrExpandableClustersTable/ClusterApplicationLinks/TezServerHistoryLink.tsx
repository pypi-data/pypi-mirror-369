import React from 'react';
import { CircularProgress } from '@mui/material';
import { i18nStrings } from '../../../constants/i18n';
import { EmrPresignedURL } from '../../EmrPresignedURL';
import { launcherIcon } from '@jupyterlab/ui-components';
import * as styles from './styles';

interface Props {
  clusterId: string;
  accountId: string;
  setIsError: (isError: boolean) => void;
}

const PERSISTENT_APP_UI_TYPE_TEZ = 'TEZ';
const expandClusterStrings = i18nStrings.Clusters.expandCluster;

const TezServerHistoryLink: React.FunctionComponent<Props> = ({ clusterId, accountId, setIsError }) => {
  const [isLoading] = React.useState(false);

  return (
    <div className={styles.linkContainer}>
      <div className={styles.link}>
        <EmrPresignedURL
          clusterId={clusterId}
          onError={(error) => error}
          accountId={accountId}
          persistentAppUIType={PERSISTENT_APP_UI_TYPE_TEZ}
          label={expandClusterStrings.TezUI}
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

export { TezServerHistoryLink };
