import { fetchApiResponse, OPTIONS_TYPE } from './fetchApiWrapper';
import {
  CreatePersistentAppUIInput,
  CreatePersistentAppUIOutput,
  DescribeClusterInput,
  DescribePersistentAppUIInput,
  DescribePersistentAppUIOutput,
  GetOnClusterAppUIPresignedURLInput,
  GetOnClusterAppUIPresignedURLOutput,
  GetPersistentAppUIPresignedURLInput,
  GetPersistentAppUIPresignedURLOutput,
  GetServerlessApplicationInput,
} from '../constants/types';
import {
  CREATE_PERSISTENT_APP_UI,
  DESCRIBE_CLUSTER_URL,
  DESCRIBE_PERSISTENT_APP_UI,
  DESCRIBE_SECURITY_CONFIGURATION_URL,
  GET_ON_CLUSTER_APP_UI_PRESIGNED_URL,
  GET_PERSISTENT_APP_UI_PRESIGNED_URL,
  GET_SERVERLESS_APPLICATION_URL,
} from './constants';
import { Arn } from '../utils/ArnUtils';
import { getFilteredAssumableRoles } from '../utils/CrossAccountUtils';

const ON_CLUSTER_APP_UI_TYPE = 'ApplicationMaster';
const PERSISTENT_APP_UI_READY = 'ATTACHED';

const getOnClusterAppUIPresignedURL = async (
  accountId: string | undefined,
  clusterId: string,
  applicationId?: string | undefined,
): Promise<GetOnClusterAppUIPresignedURLOutput> => {
  const filteredAssumableRoles = await getFilteredAssumableRoles(accountId);
  if (filteredAssumableRoles?.length > 0) {
    for (const roleArn of filteredAssumableRoles) {
      const onClusterInput: GetOnClusterAppUIPresignedURLInput = {
        ClusterId: clusterId,
        OnClusterAppUIType: ON_CLUSTER_APP_UI_TYPE,
        ApplicationId: applicationId,
        RoleArn: roleArn,
      };
      const params = JSON.stringify(onClusterInput);
      const data = await fetchApiResponse(GET_ON_CLUSTER_APP_UI_PRESIGNED_URL, OPTIONS_TYPE.POST, params);
      if (data?.presignedURL !== undefined) {
        return data;
      }
    }
  }
  const onClusterInput: GetOnClusterAppUIPresignedURLInput = {
    ClusterId: clusterId,
    OnClusterAppUIType: ON_CLUSTER_APP_UI_TYPE,
    ApplicationId: applicationId,
  };

  const params = JSON.stringify(onClusterInput);

  const data = await fetchApiResponse(GET_ON_CLUSTER_APP_UI_PRESIGNED_URL, OPTIONS_TYPE.POST, params);
  return data;
};

const createPersistentAppUI = async (targetResourceArn: string | undefined): Promise<CreatePersistentAppUIOutput> => {
  if (targetResourceArn === undefined) {
    throw new Error('Error describing persistent app UI: Invalid persistent app UI ID');
  }
  const clusterAccountId = Arn.fromArnString(targetResourceArn).accountId;
  const filteredAssumableRoles = await getFilteredAssumableRoles(clusterAccountId);
  if (filteredAssumableRoles?.length > 0) {
    for (const roleArn of filteredAssumableRoles) {
      const createPersistenInput: CreatePersistentAppUIInput = {
        TargetResourceArn: targetResourceArn,
        RoleArn: roleArn,
      };
      const params = JSON.stringify(createPersistenInput);
      const data = await fetchApiResponse(CREATE_PERSISTENT_APP_UI, OPTIONS_TYPE.POST, params);
      if (data?.persistentAppUIId !== undefined) {
        return data;
      }
    }
  }
  const createPersistentInput: CreatePersistentAppUIInput = {
    TargetResourceArn: targetResourceArn,
  };

  const params = JSON.stringify(createPersistentInput);

  const data = await fetchApiResponse(CREATE_PERSISTENT_APP_UI, OPTIONS_TYPE.POST, params);
  return data;
};

const describePersistentAppUI = async (
  persistentAppUIId: string | undefined,
  roleArn: string | undefined,
): Promise<DescribePersistentAppUIOutput> => {
  if (persistentAppUIId === undefined) {
    throw new Error('Error describing persistent app UI: Invalid persistent app UI ID');
  }
  if (roleArn) {
    const describePersistentInput: DescribePersistentAppUIInput = {
      PersistentAppUIId: persistentAppUIId,
      RoleArn: roleArn,
    };
    const params = JSON.stringify(describePersistentInput);

    const data = await fetchApiResponse(DESCRIBE_PERSISTENT_APP_UI, OPTIONS_TYPE.POST, params);
    return data;
  }
  const describePersistentInput: DescribePersistentAppUIInput = {
    PersistentAppUIId: persistentAppUIId,
  };

  const params = JSON.stringify(describePersistentInput);

  const data = await fetchApiResponse(DESCRIBE_PERSISTENT_APP_UI, OPTIONS_TYPE.POST, params);
  return data;
};

const delay = async (timeout: number) => await new Promise((resolve) => setTimeout(resolve, timeout));

const pollUntilPersistentAppUIReady = async (
  persistentAppUIId: string | undefined,
  maxTimeoutMs: number,
  attemptIntervalMs: number,
  roleArn: string | undefined,
): Promise<DescribePersistentAppUIOutput | undefined> => {
  const start = Date.now();
  let timeElapsed = 0;
  let result = undefined;

  while (timeElapsed <= maxTimeoutMs) {
    const queryResult = await describePersistentAppUI(persistentAppUIId, roleArn);
    const status = queryResult?.persistentAppUI?.persistentAppUIStatus;
    if (status && status === PERSISTENT_APP_UI_READY) {
      result = queryResult;
      break;
    }

    await delay(attemptIntervalMs);
    timeElapsed = Date.now() - start;
  }

  if (result == null) {
    throw new Error('Error waiting for persistent app UI ready: Max attempts reached');
  }
  return result;
};

const getPersistentAppUIPresignedURL = async (
  persistentAppUIId: string | undefined,
  roleArn: string | undefined,
  persistentAppUIType?: string | undefined,
  applicationId?: string | undefined,
): Promise<GetPersistentAppUIPresignedURLOutput> => {
  if (persistentAppUIId === undefined) {
    throw new Error('Error getting persistent app UI presigned URL: Invalid persistent app UI ID');
  }
  if (roleArn) {
    const getPersistentAppUIPresignedURLInput: GetPersistentAppUIPresignedURLInput = {
      PersistentAppUIId: persistentAppUIId,
      PersistentAppUIType: persistentAppUIType,
      RoleArn: roleArn,
    };
    const params = JSON.stringify(getPersistentAppUIPresignedURLInput);

    const data = await fetchApiResponse(GET_PERSISTENT_APP_UI_PRESIGNED_URL, OPTIONS_TYPE.POST, params);
    return data;
  }
  const getPersistentAppUIPresignedURLInput: GetPersistentAppUIPresignedURLInput = {
    PersistentAppUIId: persistentAppUIId,
    PersistentAppUIType: persistentAppUIType,
  };

  const params = JSON.stringify(getPersistentAppUIPresignedURLInput);

  const data = await fetchApiResponse(GET_PERSISTENT_APP_UI_PRESIGNED_URL, OPTIONS_TYPE.POST, params);
  return data;
};

const describeCluster = async (clusterId: string, accountId?: string | undefined) => {
  const describeClusterInput: DescribeClusterInput = {
    ClusterId: clusterId,
  };
  const filteredAssumableRoles = await getFilteredAssumableRoles(accountId);
  if (filteredAssumableRoles?.length > 0) {
    for (const roleArn of filteredAssumableRoles) {
      const describeClusterInput = JSON.stringify({
        ClusterId: clusterId,
        RoleArn: roleArn,
      });
      const describeClusterOutput = await fetchApiResponse(
        DESCRIBE_CLUSTER_URL,
        OPTIONS_TYPE.POST,
        describeClusterInput,
      );
      if (describeClusterOutput?.cluster !== undefined) {
        return describeClusterOutput;
      }
    }
  }

  const params = JSON.stringify(describeClusterInput);

  const data = await fetchApiResponse(DESCRIBE_CLUSTER_URL, OPTIONS_TYPE.POST, params);
  return data;
};

const describeSecurityConfiguration = async (
  clusterId: string,
  securityConfigurationName: string,
  accountId?: string | undefined,
) => {
  const describeSecurityConfigurationInput = JSON.stringify({
    ClusterId: clusterId,
    SecurityConfigurationName: securityConfigurationName,
  });
  const filteredAssumableRoles = await getFilteredAssumableRoles(accountId);
  if (filteredAssumableRoles?.length > 0) {
    for (const roleArn of filteredAssumableRoles) {
      const describeSecurityConfigurationInput = JSON.stringify({
        ClusterId: clusterId,
        RoleArn: roleArn,
        SecurityConfigurationName: securityConfigurationName,
      });
      const response = await fetchApiResponse(
        DESCRIBE_SECURITY_CONFIGURATION_URL,
        OPTIONS_TYPE.POST,
        describeSecurityConfigurationInput,
      );
      if (response && response.securityConfigurationName) {
        return response;
      }
    }
  }
  return await fetchApiResponse(
    DESCRIBE_SECURITY_CONFIGURATION_URL,
    OPTIONS_TYPE.POST,
    describeSecurityConfigurationInput,
  );
};

const getServerlessApplication = async (applicationId: string, accountId?: string | undefined) => {
  const getServerlessApplicationInput: GetServerlessApplicationInput = {
    applicationId: applicationId,
  };
  const filteredAssumableRoles = await getFilteredAssumableRoles(accountId);
  if (filteredAssumableRoles?.length > 0) {
    for (const roleArn of filteredAssumableRoles) {
      const getServerlessApplicationInput = JSON.stringify({
        applicationId: applicationId,
        RoleArn: roleArn,
      });
      const getServerlessApplicationOutput = await fetchApiResponse(
        GET_SERVERLESS_APPLICATION_URL,
        OPTIONS_TYPE.POST,
        getServerlessApplicationInput,
      );
      if (getServerlessApplicationOutput?.application !== undefined) {
        return getServerlessApplicationOutput;
      }
    }
  }

  const params = JSON.stringify(getServerlessApplicationInput);

  const data = await fetchApiResponse(GET_SERVERLESS_APPLICATION_URL, OPTIONS_TYPE.POST, params);
  return data;
};

export {
  getOnClusterAppUIPresignedURL,
  createPersistentAppUI,
  describePersistentAppUI,
  pollUntilPersistentAppUIReady,
  getPersistentAppUIPresignedURL,
  describeCluster,
  describeSecurityConfiguration,
  getServerlessApplication,
};
