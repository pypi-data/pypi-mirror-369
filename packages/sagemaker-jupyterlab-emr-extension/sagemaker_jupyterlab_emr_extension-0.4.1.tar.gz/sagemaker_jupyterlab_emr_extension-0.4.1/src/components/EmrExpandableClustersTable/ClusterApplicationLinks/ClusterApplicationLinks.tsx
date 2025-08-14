import React, { useState } from 'react';
import { SparkServerHistoryLink } from './SparkServerHistoryLink';
import { TezServerHistoryLink } from './TezServerHistoryLink';
import * as styles from './styles';
import { i18nStrings } from '../../../constants/i18n';

interface Props {
  selectedClusterId: string;
  clusterArn: string;
  accountId: string;
}

const expandClusterStrings = i18nStrings.Clusters.expandCluster;

const ClusterApplicationLinks: React.FunctionComponent<Props> = (props) => {
  const { accountId, selectedClusterId } = props;
  const [isError, setIsError] = useState(false);

  if (isError) {
    //TODO: Add telemetry/logging
    return <div>{expandClusterStrings.NotAvailable}</div>;
  }

  return (
    <>
      <div className={styles.Info}>
        <SparkServerHistoryLink clusterId={selectedClusterId} accountId={accountId} setIsError={setIsError} />
      </div>
      <div className={styles.Info}>
        <TezServerHistoryLink clusterId={selectedClusterId} accountId={accountId} setIsError={setIsError} />
      </div>
    </>
  );
};

export { ClusterApplicationLinks };
