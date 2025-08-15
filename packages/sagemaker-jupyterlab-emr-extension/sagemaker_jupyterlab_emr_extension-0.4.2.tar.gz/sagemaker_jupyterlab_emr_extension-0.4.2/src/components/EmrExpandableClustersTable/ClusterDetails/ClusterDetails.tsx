import React, { useEffect, useState } from 'react';
import { cx } from '@emotion/css';
import { i18nStrings } from '../../../constants/i18n';
import { ClusterTags } from './ClusterTags';
import { Cluster, ListInstanceGroupsOutput } from '../../../constants/types';
import {
  generateMasterNodesStringFromInstanceGroupData,
  generateApplicationsStringFromClusterData,
  generateCoreNodesStringFromInstanceGroupData,
} from '../../../utils/ClusterDetailUtils';
import { ClusterApplicationLinks } from '../ClusterApplicationLinks/ClusterApplicationLinks';
import * as styles from './styles';
import { OPTIONS_TYPE, fetchApiResponse } from '../../../service/fetchApiWrapper';
import { LIST_INSTANCE_GROUPS } from '../../../service';
import { getFilteredAssumableRoles } from '../../../utils/CrossAccountUtils';

interface Props {
  selectedClusterId: string;
  accountId: string;
  clusterArn: string;
  clusterData: Cluster | undefined;
  instanceGroupData?: ListInstanceGroupsOutput | undefined;
}

const expandClusterStrings = i18nStrings.Clusters.expandCluster;

const ClusterDetails: React.FunctionComponent<Props> = ({ clusterArn, accountId, selectedClusterId, clusterData }) => {
  const cluster = clusterData;
  const [instanceGroupsData, setInstanceGroupsData] = useState<any>();

  const getListInstanceGroups = async (selectedClusterId: string | undefined) => {
    const params = JSON.stringify({
      ClusterId: selectedClusterId,
    });
    const data = await fetchApiResponse(LIST_INSTANCE_GROUPS, OPTIONS_TYPE.POST, params);
    if (data.instanceGroups?.length > 0 && data.instanceGroups[0].id?.length > 0) {
      setInstanceGroupsData(data);
    } else {
      const filteredAssumableRoles = await getFilteredAssumableRoles(accountId);
      if (filteredAssumableRoles?.length > 0) {
        for (const roleArn of filteredAssumableRoles) {
          const getListInstanceGroupsInput = JSON.stringify({
            ClusterId: selectedClusterId,
            RoleArn: roleArn,
          });
          const getListInstanceGroupsOutput = await fetchApiResponse(
            LIST_INSTANCE_GROUPS,
            OPTIONS_TYPE.POST,
            getListInstanceGroupsInput,
          );
          if (
            getListInstanceGroupsOutput.instanceGroups.length > 0 &&
            getListInstanceGroupsOutput.instanceGroups[0].id
          ) {
            setInstanceGroupsData(getListInstanceGroupsOutput);
          }
        }
      }
    }
  };

  useEffect(() => {
    getListInstanceGroups(selectedClusterId);
  }, [selectedClusterId]);

  return (
    <div data-analytics-type="eventContext" data-analytics="JupyterLab" className={styles.InfoMainContainer}>
      <div className={styles.InformationContainer}>
        <h4>{expandClusterStrings.Overview}</h4>
        <div className={styles.Info}>{generateMasterNodesStringFromInstanceGroupData(instanceGroupsData)}</div>
        <div className={styles.Info}>{generateCoreNodesStringFromInstanceGroupData(instanceGroupsData)}</div>
        <div className={styles.Info}>
          {expandClusterStrings.Apps}: {generateApplicationsStringFromClusterData(cluster)}
        </div>
      </div>
      <div className={cx(styles.InformationContainer, styles.LinksContainer)}>
        <h4>{expandClusterStrings.ApplicationUserInterface}</h4>
        <ClusterApplicationLinks selectedClusterId={selectedClusterId} accountId={accountId} clusterArn={clusterArn} />
      </div>
      <div className={styles.InformationContainer}>
        <h4>{expandClusterStrings.Tags}</h4>
        <ClusterTags clusterData={clusterData} />
      </div>
    </div>
  );
};

export { ClusterDetails, Props };
