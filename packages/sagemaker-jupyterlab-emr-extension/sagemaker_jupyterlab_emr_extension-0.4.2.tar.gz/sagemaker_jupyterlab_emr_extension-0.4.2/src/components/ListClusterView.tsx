import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { cx } from '@emotion/css';
import { CircularProgress } from '@mui/material';
import { Footer } from './Footer';
import { GetColumnConfig } from './GetColumnConfig';
import { EmrExpandedClustersTable } from './EmrExpandableClustersTable/EmrExpandableClustersTable';
import { arrayHasLength, recordEventDetail, strHasLength } from '../utils/CommonUtils';
import { i18nStrings } from '../constants/i18n';
import { ModalBodyContainer, GridWrapper } from './EmrExpandableClustersTable/styles';
import { Cluster, ClusterRowType, EmrConnectRoleDataType } from '../constants/types';
import { FETCH_EMR_ROLES, LIST_CLUSTERS_URL } from '../service/constants';
import { fetchApiResponse, OPTIONS_TYPE } from '../service/fetchApiWrapper';
import { Arn } from '../utils/ArnUtils';
import { JupyterFrontEnd } from '@jupyterlab/application';
import {
  handleSpecialClusterConnect,
  openSelectAuthType,
  openSelectRuntimeExecRole,
} from '../utils/ConnectClusterUtils';
import { openSelectAssumableRole } from '../utils/ConnectClusterUtils';
import { describeCluster, describeSecurityConfiguration } from '../service/presignedURL';
import { DEFAULT_TABLE_CONFIG } from '../constants';
import { isTIPEnabledCluster, isLdapCluster } from '../utils/AuthTypeUtil';

interface ListClusterProps extends React.HTMLAttributes<HTMLElement> {
  readonly onCloseModal: () => void;
  readonly header: JSX.Element;
  readonly app: JupyterFrontEnd;
}

const ListClusterView: React.FC<ListClusterProps> = (ListClusterProps) => {
  const { onCloseModal, header, app } = ListClusterProps;
  const [clustersData, setClustersData] = useState<any>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState<string>('');
  const [clusterDetails, setClusterDetails] = useState<Cluster | undefined>(undefined);
  const [selectedId, setSelectedId] = useState<string | undefined>();
  const [selectedAccountId, setSelectedAccountId] = useState<string>(''); // Need accountId later for phase2
  const [isConnectButtonDisabled, setIsConnectButtonDisabled] = useState<boolean>(true);
  const columnConfig = GetColumnConfig();

  const getListClusterDataFromArn = async (marker = '', roleArn?: string | undefined) => {
    try {
      do {
        const params = JSON.stringify({
          ClusterStates: ['RUNNING', 'WAITING'],
          ...(marker && { Marker: marker }),
          RoleArn: roleArn,
        });
        const data = await fetchApiResponse(LIST_CLUSTERS_URL, OPTIONS_TYPE.POST, params);
        if (data && data.clusters) {
          setClustersData((prevData: any) => [
            ...new Map([...prevData, ...data.clusters].map((cluster) => [cluster.id, cluster])).values(),
          ]);
        }
        marker = data?.Marker;
      } while (strHasLength(marker));
    } catch (error: any) {
      setIsError(error.message);
    }
  };

  const getListClusterData = async () => {
    try {
      setIsLoading(true);
      const fetchEmrRolesInput = JSON.stringify({});
      const fetchEmrRolesOutput = await fetchApiResponse(FETCH_EMR_ROLES, OPTIONS_TYPE.POST, fetchEmrRolesInput);
      if (fetchEmrRolesOutput?.EmrAssumableRoleArns?.length > 0) {
        for (const roleArn of fetchEmrRolesOutput.EmrAssumableRoleArns) {
          await getListClusterDataFromArn('', roleArn);
        }
      }
      await getListClusterDataFromArn();
      setIsLoading(false);
    } catch (error: any) {
      setIsLoading(false);
      setIsError(error.message);
    }
  };

  useEffect(() => {
    getListClusterData();
  }, []);

  const getClusterDetails = async (selectedId: string) => {
    const selectedCluster = clustersList.find(
      (cluster: { id: string }) => cluster.id === selectedId,
    ) as unknown as Cluster;
    let clusterAccountId = '';
    const clusterArn = selectedCluster?.clusterArn;

    if (clusterArn && Arn.isValid(clusterArn)) clusterAccountId = Arn.fromArnString(clusterArn).accountId;
    const data = await describeCluster(selectedId, clusterAccountId);
    if (data?.cluster.id) {
      const securityConfigName =
        typeof data?.cluster.securityConfiguration === 'string'
          ? data?.cluster.securityConfiguration
          : data?.cluster.securityConfiguration?.name;

      if (securityConfigName) {
        const defaultSecurityConfig = {
          securityConfigurationName: securityConfigName,
          authentication: '',
        };
        try {
          const securityConfig = await describeSecurityConfiguration(
            data?.cluster.id,
            securityConfigName,
            clusterAccountId,
          );
          data.cluster.securityConfiguration = securityConfig || defaultSecurityConfig;
        } catch (error) {
          data.cluster.securityConfiguration = defaultSecurityConfig;
        }
      }

      setClusterDetails(data.cluster);
    }
  };

  useEffect(() => {
    if (selectedId) {
      setClusterDetails(getClusterDetails(selectedId) as any);
    }
  }, [selectedId]);

  //sort the listCluster data by Name
  const clustersList = useMemo(
    () =>
      clustersData?.sort((a: ClusterRowType, b: ClusterRowType) => {
        const clusterA = a.name as string;
        const clusterB = b.name as string;
        return clusterA?.localeCompare(clusterB);
      }),
    [clustersData],
  );

  const getSelectedClusterAccountId = useCallback(
    (selectedClusterId: string) => {
      const selectedCluster = clustersList.find(
        (cluster: { id: string }) => cluster.id === selectedClusterId,
      ) as unknown as Cluster;
      let accountId = '';
      const clusterArn = selectedCluster?.clusterArn;

      if (clusterArn && Arn.isValid(clusterArn)) accountId = Arn.fromArnString(clusterArn).accountId;
      return accountId;
    },
    [clustersList],
  );

  const getSelectedClusterArn = useCallback(
    (selectedClusterId: string) => {
      const cluster: any = clustersList.find((cluster: { id: string }) => cluster.id === selectedClusterId);
      const clusterArn = cluster?.clusterArn;
      if (clusterArn && Arn.isValid(clusterArn)) return clusterArn;
      return '';
    },
    [clustersList],
  );

  const handleRowSelection = useCallback(
    (selectedRow: ClusterRowType): void => {
      const selectedRowId = selectedRow?.id;

      if (selectedRowId && selectedRowId === selectedId) {
        setSelectedId(selectedRowId);
        setSelectedAccountId('');
        setIsConnectButtonDisabled(true);
      } else {
        setSelectedId(selectedRowId);
        setSelectedAccountId(getSelectedClusterAccountId(selectedRowId));
        setIsConnectButtonDisabled(false);

        recordEventDetail('EMR-Modal-ClusterRow', 'JupyterLab');
      }
    },
    [selectedId, getSelectedClusterAccountId],
  );

  const ListDataGrid = () => {
    return (
      <>
        <div className={cx(GridWrapper, 'grid-wrapper')}>
          <EmrExpandedClustersTable
            clustersList={clustersList}
            selectedClusterId={selectedId ?? ''}
            clusterArn={getSelectedClusterArn(selectedId ?? '')}
            accountId={getSelectedClusterAccountId(selectedId ?? '')}
            tableConfig={DEFAULT_TABLE_CONFIG}
            clusterManagementListConfig={columnConfig}
            onRowSelect={handleRowSelection}
            clusterDetails={clusterDetails}
          />
        </div>
      </>
    );
  };

  const onConnect = async () => {
    try {
      // fetch AWS account Id, assumable role and execution role Arns
      const emrConnectRoleData: EmrConnectRoleDataType = await fetchApiResponse(
        FETCH_EMR_ROLES,
        OPTIONS_TYPE.POST,
        undefined,
      );

      if (emrConnectRoleData.CallerAccountId === 'MISSING_AWS_ACCOUNT_ID') {
        throw new Error('Failed to get caller account Id');
      }
      if (!clusterDetails) {
        throw new Error('Error in getting cluster details');
      }
      if (!selectedAccountId) {
        throw new Error('Error in getting cluster account Id');
      }

      const clusterRow = clusterDetails as ClusterRowType;
      clusterRow.clusterAccountId = selectedAccountId;

      // Handle TIP-enabled clusters
      if (isTIPEnabledCluster(clusterRow)) {
        onCloseModal();
        openSelectRuntimeExecRole(emrConnectRoleData, app, undefined, clusterRow, undefined);
        return;
      }

      if (clusterRow.clusterAccountId === emrConnectRoleData.CallerAccountId) {
        onCloseModal();
        // if Kerberos or LDAP cluster, no need to select auth type
        if (isLdapCluster(clusterRow)) {
          handleSpecialClusterConnect(app, clusterRow);
          return;
        }
        openSelectAuthType(clusterRow, emrConnectRoleData, app);
      } else {
        onCloseModal();
        openSelectAssumableRole(emrConnectRoleData, app, clusterRow);
      }

      recordEventDetail('EMR-Select-Cluster', 'JupyterLab');
    } catch (error: any) {
      setIsError(error.message);
    }
  };

  const getErrorMessage = (errorMessage: string) => {
    const documentationLink = (
      <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/studio-notebooks-configure-discoverability-emr-cluster.html">
        documentation
      </a>
    );

    if (errorMessage.includes('permission error')) {
      return (
        <span className="error-msg">
          {i18nStrings.Clusters.permissionError} {documentationLink}
        </span>
      );
    } else {
      return <span className="error-msg">{errorMessage}</span>;
    }
  };

  return (
    <>
      <div data-testid="list-cluster-view">
        {isError && <span className="no-cluster-msg">{getErrorMessage(isError)}</span>}
        {isLoading ? (
          <span>
            <CircularProgress size="1rem" />
          </span>
        ) : arrayHasLength(clustersData) ? (
          <div className={cx(ModalBodyContainer, 'modal-body-container')}>
            {header}
            {ListDataGrid()}
          </div>
        ) : (
          <div className="no-cluster-msg">{i18nStrings.Clusters.noCluster}</div>
        )}
        <Footer onCloseModal={onCloseModal} onConnect={onConnect} disabled={isConnectButtonDisabled} />
      </div>
    </>
  );
};

export { ListClusterProps, ListClusterView };
