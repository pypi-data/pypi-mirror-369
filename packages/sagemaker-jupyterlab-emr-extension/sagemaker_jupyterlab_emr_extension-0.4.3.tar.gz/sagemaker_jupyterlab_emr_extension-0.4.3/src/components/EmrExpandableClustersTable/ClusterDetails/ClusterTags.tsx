import React from 'react';
import { i18nStrings } from '../../../constants/i18n';
import { Cluster } from '../../../constants/types';

import * as styles from './styles';

interface Props {
  clusterData: Cluster | undefined;
}

const expandClusterStrings = i18nStrings.Clusters.expandCluster;

const ClusterTags: React.FunctionComponent<Props> = ({ clusterData }) => {
  const tags = clusterData?.tags;

  if (tags?.length) {
    return (
      <>
        {tags.map((tag) => (
          <div className={styles.Info} key={tag?.key}>
            {tag?.key}: {tag?.value}
          </div>
        ))}
      </>
    );
  }

  return <div>{expandClusterStrings.NoTags}</div>;
};

export { ClusterTags };
