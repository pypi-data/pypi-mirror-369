/**
 * Urls
 */
const DESCRIBE_CLUSTER_URL = '/aws/sagemaker/api/emr/describe-cluster';
const DESCRIBE_SECURITY_CONFIGURATION_URL = '/aws/sagemaker/api/emr/describe-security-configuration';
const LIST_CLUSTERS_URL = '/aws/sagemaker/api/emr/list-clusters';
const GET_ON_CLUSTER_APP_UI_PRESIGNED_URL = '/aws/sagemaker/api/emr/get-on-cluster-app-ui-presigned-url';
const CREATE_PERSISTENT_APP_UI = '/aws/sagemaker/api/emr/create-persistent-app-ui';
const DESCRIBE_PERSISTENT_APP_UI = '/aws/sagemaker/api/emr/describe-persistent-app-ui';
const GET_PERSISTENT_APP_UI_PRESIGNED_URL = '/aws/sagemaker/api/emr/get-persistent-app-ui-presigned-url';
const LIST_INSTANCE_GROUPS = '/aws/sagemaker/api/emr/list-instance-groups';
const FETCH_EMR_ROLES = '/aws/sagemaker/api/sagemaker/fetch-emr-roles';
const LIST_SERVERLESS_APPLICATIONS_URL = '/aws/sagemaker/api/emr-serverless/list-applications';
const GET_SERVERLESS_APPLICATION_URL = '/aws/sagemaker/api/emr-serverless/get-application';

/**
 * API calls constants
 */
const SUCCESS_RESPONSE_STATUS = [200, 201];

export {
  DESCRIBE_CLUSTER_URL,
  DESCRIBE_SECURITY_CONFIGURATION_URL,
  LIST_CLUSTERS_URL,
  SUCCESS_RESPONSE_STATUS,
  GET_ON_CLUSTER_APP_UI_PRESIGNED_URL,
  CREATE_PERSISTENT_APP_UI,
  DESCRIBE_PERSISTENT_APP_UI,
  GET_PERSISTENT_APP_UI_PRESIGNED_URL,
  LIST_INSTANCE_GROUPS,
  FETCH_EMR_ROLES,
  LIST_SERVERLESS_APPLICATIONS_URL,
  GET_SERVERLESS_APPLICATION_URL,
};
