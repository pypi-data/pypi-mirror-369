import { IRouter, JupyterFrontEnd } from '@jupyterlab/application';
import { URLExt } from '@jupyterlab/coreutils';
import { showErrorMessage } from '@jupyterlab/apputils';
import { i18nStrings } from '../constants/i18n';
import { describeCluster, getServerlessApplication } from '../service/presignedURL';
import { openSelectAssumableRole, openSelectAuthType, openSelectRuntimeExecRole } from './ConnectClusterUtils';
import { sleep } from '../utils/CommonUtils';
import { FETCH_EMR_ROLES, OPTIONS_TYPE, fetchApiResponse } from '../service';
import { ClusterRowType, EmrConnectRoleDataType, ServerlessApplicationRowType } from '../constants';

const i18nStringsError = i18nStrings.EmrClustersDeeplinking.errorDialog;
const i18nStringsServerlessApplicationsError = i18nStrings.EmrServerlessApplicationsDeeplinking.errorDialog;

// IRouter pattern could be matched arbitrary number of times.
// This flag is to ensure the plugin is triggered only once during re-direction.
export let isPatternMatched = false;

/**
 * Function to attach EMR cluster to a new notebook
 * @param router
 * @param app
 * @returns
 */
const executeAttachClusterToNewNb = async (router: IRouter, app: JupyterFrontEnd) => {
  if (isPatternMatched) {
    return;
  }
  try {
    const { search } = router.current;
    if (!search) {
      await showErrorMessageAsync(i18nStringsError.invalidRequestErrorMessage);
      return;
    }

    app.restored.then(async () => {
      const { clusterId, applicationId, accountId } = URLExt.queryStringToObject(search);

      if (!clusterId && !applicationId) {
        await showErrorMessageAsync(i18nStringsError.invalidRequestErrorMessage);
        return;
      }

      const fetchEmrRolesResponse = await fetchApiResponse(FETCH_EMR_ROLES, OPTIONS_TYPE.POST, undefined);
      if (!fetchEmrRolesResponse || fetchEmrRolesResponse?.error) {
        await showErrorMessageAsync(i18nStrings.Clusters.fetchEmrRolesError);
        return;
      }

      if (clusterId) {
        await attachClusterToNotebook(clusterId, app, accountId, fetchEmrRolesResponse);
      } else if (applicationId) {
        await attachServerlessApplicationToNotebook(applicationId, app, accountId, fetchEmrRolesResponse);
      }
    });
  } catch (error) {
    await showErrorMessageAsync(i18nStringsError.defaultErrorMessage);
    return;
  } finally {
    isPatternMatched = true;
  }
};

const showErrorMessageAsync = async (message: string) => {
  return showErrorMessage(i18nStringsError.errorTitle, {
    message: message,
  });
};

const createNewNotebook = async (app: JupyterFrontEnd) => {
  // Execute create new notebook command
  const notebookPanel = await app.commands.execute('notebook:create-new');
  await new Promise((resolve) => {
    notebookPanel.sessionContext.kernelChanged.connect((context: any, kernel: unknown) => {
      resolve(kernel);
    });
  });

  // Sleep for 2 sec for the kernel to start up
  await sleep(2000);
};

const attachClusterToNotebook = async (
  clusterId: string,
  app: JupyterFrontEnd,
  accountId: string | undefined,
  fetchEmrRolesResponse: EmrConnectRoleDataType,
) => {
  const describeClusterResponse = await describeCluster(clusterId, accountId);
  if (!describeClusterResponse || !describeClusterResponse?.cluster) {
    await showErrorMessageAsync(i18nStringsError.invalidClusterErrorMessage);
    return;
  }
  const clusterData: ClusterRowType = describeClusterResponse.cluster;

  await createNewNotebook(app);

  // if connecting cross account cluster, pop up assumable role widget
  if (accountId) {
    clusterData.clusterAccountId = accountId;
    openSelectAssumableRole(fetchEmrRolesResponse, app, clusterData);
  } else {
    clusterData.clusterAccountId = fetchEmrRolesResponse.CallerAccountId;
    openSelectAuthType(clusterData, fetchEmrRolesResponse, app);
  }
};

const attachServerlessApplicationToNotebook = async (
  applicationId: string,
  app: JupyterFrontEnd,
  accountId: string | undefined,
  fetchEmrRolesResponse: EmrConnectRoleDataType,
) => {
  const getApplicationResponse = await getServerlessApplication(applicationId, accountId);
  if (!getApplicationResponse || !getApplicationResponse?.application) {
    await showErrorMessageAsync(i18nStringsServerlessApplicationsError.invalidApplicationErrorMessage);
    return;
  }
  const applicationDetails: ServerlessApplicationRowType = getApplicationResponse.application;
  await createNewNotebook(app);
  // if connecting cross account cluster, pop up assumable role widget
  if (accountId) {
    openSelectAssumableRole(fetchEmrRolesResponse, app, undefined, applicationDetails);
  } else {
    openSelectRuntimeExecRole(fetchEmrRolesResponse, app, undefined, undefined, applicationDetails);
  }
};

export {
  executeAttachClusterToNewNb,
  attachClusterToNotebook,
  attachServerlessApplicationToNotebook,
  createNewNotebook,
};
