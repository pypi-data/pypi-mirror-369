import { i18nStrings } from '../constants/i18n';
import { Cluster, ListInstanceGroupsOutput } from '../constants/types';

const expandClusterStrings = i18nStrings.Clusters.expandCluster;

const MASTER = 'MASTER';
const CORE = 'CORE';

export const generateMasterNodesStringFromInstanceGroupData = (
  instanceGroupsData: ListInstanceGroupsOutput | undefined,
) => {
  const masterNode = instanceGroupsData?.instanceGroups?.find(
    (instanceGroup) => instanceGroup?.instanceGroupType === MASTER,
  );

  if (masterNode) {
    const numberOfNodes = masterNode.runningInstanceCount;
    const instanceType = masterNode.instanceType;

    return `${expandClusterStrings.MasterNodes}: ${numberOfNodes}, ${instanceType}`;
  }

  return `${expandClusterStrings.MasterNodes}: ${expandClusterStrings.NotAvailable}`;
};

export const generateCoreNodesStringFromInstanceGroupData = (
  instanceGroupsData: ListInstanceGroupsOutput | undefined,
) => {
  const coreNode = instanceGroupsData?.instanceGroups?.find(
    (instanceGroup) => instanceGroup?.instanceGroupType === CORE,
  );

  if (coreNode) {
    const numberOfNodes = coreNode.runningInstanceCount;
    const instanceType = coreNode.instanceType;

    return `${expandClusterStrings.CoreNodes}: ${numberOfNodes}, ${instanceType}`;
  }

  return `${expandClusterStrings.CoreNodes}: ${expandClusterStrings.NotAvailable}`;
};

export const generateApplicationsStringFromClusterData = (cluster: Cluster | undefined) => {
  const applications = cluster?.applications;

  if (applications?.length) {
    return applications.map((application, i) => {
      const lastIndex = applications.length - 1;
      const suffix = i === lastIndex ? '.' : ', ';

      return `${application?.name} ${application?.version}${suffix}`;
    });
  }

  return `${expandClusterStrings.NotAvailable}`;
};
