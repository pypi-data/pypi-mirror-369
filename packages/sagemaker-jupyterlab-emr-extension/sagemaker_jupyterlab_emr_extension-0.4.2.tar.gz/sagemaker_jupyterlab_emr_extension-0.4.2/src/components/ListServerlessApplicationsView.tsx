import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { cx } from '@emotion/css';
import { CircularProgress } from '@mui/material';
import { Footer } from './Footer';
import { GetServerlessApplicationColumnConfig } from './GetServerlessApplicationColumnConfig';
import { arrayHasLength, strHasLength } from '../utils/CommonUtils';
import { i18nStrings } from '../constants/i18n';
import { ModalBodyContainer, GridWrapper } from './EmrExpandableClustersTable/styles';
import {
  ServerlessApplicationRowType,
  ListClusterProps,
  ServerlessApplication,
  ServerlessApplicationState,
  EmrConnectRoleDataType,
} from '../constants/types';
import { FETCH_EMR_ROLES, LIST_SERVERLESS_APPLICATIONS_URL } from '../service/constants';
import { fetchApiResponse, OPTIONS_TYPE } from '../service/fetchApiWrapper';
import { ACCESS_DENIED_EXCEPTION, DEFAULT_TABLE_CONFIG } from '../constants';
import { Arn } from '../utils/ArnUtils';
import { getServerlessApplication } from '../service';
import { EmrServerlessExpandableApplicationsTable } from './EmrServerlessExpandableApplicationsTable/EmrServerlessExpandableApplicationsTable';
import { openSelectAssumableRole, openSelectRuntimeExecRole } from '../utils/ConnectClusterUtils';
import { ErrorBanner } from '../utils/ErrorBanner';

const ListServerlessApplicationsView: React.FC<ListClusterProps> = (ListClusterProps) => {
  const { onCloseModal, header, app } = ListClusterProps;
  const [applicationsData, setApplicationsData] = useState<any>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [applicationDetails, setApplicationDetails] = useState<ServerlessApplication | undefined>(undefined);
  const [applicationDetailsLoading, setApplicationDetailsLoading] = useState(false);
  const [selectedId, setSelectedId] = useState<string | undefined>();
  const [selectedAccountId, setSelectedAccountId] = useState<string>('');
  const [isConnectButtonDisabled, setIsConnectButtonDisabled] = useState<boolean>(true);
  const columnConfig = GetServerlessApplicationColumnConfig();

  const getListApplicationsDataFromArn = async (nextToken = '', roleArn?: string | undefined) => {
    do {
      const params = JSON.stringify({
        states: [
          ServerlessApplicationState.Started,
          ServerlessApplicationState.Created,
          ServerlessApplicationState.Stopped,
        ],
        ...(nextToken && { nextToken: nextToken }),
        roleArn: roleArn,
      });
      const data = await fetchApiResponse(LIST_SERVERLESS_APPLICATIONS_URL, OPTIONS_TYPE.POST, params);
      if (data && data.applications) {
        setApplicationsData((prevData: ServerlessApplicationRowType[]) => [
          ...new Map([...prevData, ...data.applications].map((application) => [application.id, application])).values(),
        ]);
      }
      nextToken = data?.nextToken;
      if (data.code || data.errorMessage) {
        setIsLoading(false);
        if (data.code === ACCESS_DENIED_EXCEPTION) {
          setError(i18nStrings.EmrServerlessApplications.listApplicationsAccessDeniedException);
        } else {
          setError(`${data.code}: ${data.errorMessage}`);
        }
      } else {
        setError('');
      }
    } while (strHasLength(nextToken));
  };

  const getListApplicationsData = async (nextToken = '') => {
    try {
      setIsLoading(true);
      const fetchEmrRolesInput = JSON.stringify({});
      const fetchEmrRolesOutput = await fetchApiResponse(FETCH_EMR_ROLES, OPTIONS_TYPE.POST, fetchEmrRolesInput);
      await getListApplicationsDataFromArn();
      if (fetchEmrRolesOutput?.EmrAssumableRoleArns?.length > 0) {
        for (const roleArn of fetchEmrRolesOutput.EmrAssumableRoleArns) {
          await getListApplicationsDataFromArn('', roleArn);
        }
      }
      setIsLoading(false);
    } catch (error: any) {
      setIsLoading(false);
      setError(error.message);
    }
  };

  useEffect(() => {
    getListApplicationsData();
  }, []);

  //sort the listApplications data by Name
  const applicationsList = useMemo(
    () =>
      applicationsData?.sort((a: ServerlessApplicationRowType, b: ServerlessApplicationRowType) => {
        const applicationA = a.name as string;
        const applicationB = b.name as string;
        return applicationA?.localeCompare(applicationB);
      }),
    [applicationsData],
  );
  const getServerlessApplicationDetails = async (selectedId: string) => {
    setApplicationDetailsLoading(true);
    setIsConnectButtonDisabled(true);
    const selectedApplication = applicationsData.find(
      (application: { id: string }) => application.id === selectedId,
    ) as unknown as ServerlessApplication;
    let applicationAccountId = '';
    const applicationArn = selectedApplication?.arn;

    if (applicationArn && Arn.isValid(applicationArn))
      applicationAccountId = Arn.fromArnString(applicationArn).accountId;
    const data = await getServerlessApplication(selectedId, applicationAccountId);
    setApplicationDetails(data.application);
    if (data.code || data.errorMessage) {
      setApplicationDetailsLoading(false);
      if (data.code === ACCESS_DENIED_EXCEPTION) {
        setError(i18nStrings.EmrServerlessApplications.getApplicationsAccessDeniedException);
      } else {
        setError(`${data.code}: ${data.errorMessage}`);
      }
    } else {
      setError('');
    }
    setApplicationDetailsLoading(false);
    setIsConnectButtonDisabled(false);
  };

  useEffect(() => {
    if (selectedId) {
      setApplicationDetails(getServerlessApplicationDetails(selectedId) as any);
    }
  }, [selectedId]);

  const getSelectedApplicationAccountId = useCallback(
    (selectedApplicationId: string) => {
      const selectedApplication = applicationsList.find(
        (application: { id: string }) => application.id === selectedApplicationId,
      ) as unknown as ServerlessApplication;
      let accountId = '';
      const applicationArn = selectedApplication?.arn;

      if (applicationArn && Arn.isValid(applicationArn)) accountId = Arn.fromArnString(applicationArn).accountId;
      return accountId;
    },
    [applicationsList],
  );

  const getSelectedApplicationArn = useCallback(
    (selectedApplicationId: string) => {
      const application: any = applicationsList.find(
        (application: { id: string }) => application.id === selectedApplicationId,
      );
      const applicationArn = application?.arn;
      if (applicationArn && Arn.isValid(applicationArn)) return applicationArn;
      return '';
    },
    [applicationsList],
  );

  const handleRowSelection = useCallback(
    (selectedRow: ServerlessApplicationRowType): void => {
      const selectedRowId = selectedRow?.id;
      if (selectedRowId && selectedRowId === selectedId) {
        setSelectedId(selectedRowId);
        setSelectedAccountId('');
        setIsConnectButtonDisabled(true);
      } else {
        setSelectedId(selectedRowId);
        setSelectedAccountId(getSelectedApplicationAccountId(selectedRowId));
        setIsConnectButtonDisabled(false);
      }
    },
    [selectedId, getSelectedApplicationAccountId],
  );

  const ListDataGrid = () => {
    return (
      <>
        <div className={cx(GridWrapper, 'grid-wrapper')}>
          <EmrServerlessExpandableApplicationsTable
            applicationsList={applicationsList}
            selectedApplicationId={selectedId ?? ''}
            applicationArn={getSelectedApplicationArn(selectedId ?? '')}
            accountId={getSelectedApplicationAccountId(selectedId ?? '')}
            tableConfig={DEFAULT_TABLE_CONFIG}
            applicationManagementListConfig={columnConfig}
            onRowSelect={handleRowSelection}
            applicationDetails={applicationDetails}
            applicationDetailsLoading={applicationDetailsLoading}
          />
        </div>
      </>
    );
  };

  const onConnect = async () => {
    try {
      const emrConnectRoleData: EmrConnectRoleDataType = await fetchApiResponse(FETCH_EMR_ROLES, OPTIONS_TYPE.POST);

      if (emrConnectRoleData.CallerAccountId === 'MISSING_AWS_ACCOUNT_ID') {
        throw new Error('Failed to get caller account Id');
      }
      if (!applicationDetails) {
        throw new Error('Error in getting serverless application details');
      }
      if (!selectedAccountId) {
        throw new Error('Error in getting serverless application account Id');
      }

      if (selectedAccountId !== emrConnectRoleData.CallerAccountId) {
        onCloseModal();
        openSelectAssumableRole(emrConnectRoleData, app, undefined, applicationDetails);
      } else {
        onCloseModal();
        openSelectRuntimeExecRole(emrConnectRoleData, app, undefined, undefined, applicationDetails);
      }
    } catch (error: any) {
      setError(error.message);
    }
  };

  return (
    <>
      <div data-testid="list-serverless-applications-view">
        {error && <ErrorBanner error={error} />}
        {isLoading ? (
          <span>
            <CircularProgress size="1rem" />
          </span>
        ) : arrayHasLength(applicationsData) ? (
          <div className={cx(ModalBodyContainer, 'modal-body-container')}>
            {header}
            {ListDataGrid()}
          </div>
        ) : (
          <div className="no-cluster-msg">{i18nStrings.EmrServerlessApplications.noApplications}</div>
        )}
        <Footer onCloseModal={onCloseModal} onConnect={onConnect} disabled={isConnectButtonDisabled} />
      </div>
    </>
  );
};

export { ListClusterProps, ListServerlessApplicationsView };
