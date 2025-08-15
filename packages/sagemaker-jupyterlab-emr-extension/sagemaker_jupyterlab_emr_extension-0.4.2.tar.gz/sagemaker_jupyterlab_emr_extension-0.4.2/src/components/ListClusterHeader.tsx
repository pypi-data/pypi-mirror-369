import React, { ReactElement } from 'react';
import { cx } from '@emotion/css';
import { i18nStrings } from '../constants/i18n';
import { Link, LinkType } from '../components/Link/Link';

import styles from './styles';
import { getDocLinkDomain } from '../utils/DocLinkUtils';
import { AWSRegions } from '../service/schemaTypes';

interface ListClusterHeaderPropsType extends React.HTMLAttributes<HTMLElement> {
  clusterName?: string;
}

const ListClusterHeader: React.FC<ListClusterHeaderPropsType> = ({ clusterName }) => {
  //TODO: Check how to get region
  // const { getState } = useStore<AppState, AppAction>();
  // const region = getRegion(getState());
  const docLinkDomain = getDocLinkDomain(AWSRegions['us-west-2']);

  const getTitle = () => {
    let title: string | ReactElement;
    if (!clusterName) {
      title = `${i18nStrings.Clusters.widgetHeader} `;
    } else {
      const clusterConnected = <span className={styles.ConnectCluster}>{clusterName}</span>;
      const connectedInfoPart1 = `${i18nStrings.Clusters.widgetConnected} `;
      const connectedInfoPart2 = ` ${i18nStrings.Clusters.connectedWidgetHeader} `;
      title = (
        <div className={cx(styles.ClusterDescription, 'list-cluster-description')}>
          {connectedInfoPart1}
          {clusterConnected}
          {connectedInfoPart2}
        </div>
      );
    }
    return title;
  };

  return (
    <div className={cx(styles.ModalHeader, 'list-cluster-modal-header')}>
      {getTitle()}
      <Link href={`${docLinkDomain}/sagemaker/latest/dg/studio-notebooks-emr-cluster.html`} type={LinkType.External}>
        {i18nStrings.Clusters.learnMore}
      </Link>
    </div>
  );
};

export { ListClusterHeader, ListClusterHeaderPropsType };
