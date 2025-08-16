const i18nStrings = {
  Clusters: {
    tabName: 'EMR Clusters',
    widgetTitle: 'Connect to cluster',
    connectCommand: {
      label: 'Connect',
      caption: 'Connect to a cluster',
    },
    connectMessage: {
      errorTitle: 'Error connecting to EMR cluster',
      successTitle: 'Successfully connected to EMR cluster',
      errorDefaultMessage: 'Error connecting to EMR cluster',
      successDefaultMessage: 'Connected to EMR Cluster',
    },
    selectRoleErrorMessage: {
      noEmrExecutionRole:
        'No available EMR execution role found for the cluster. Please provide one in user profile settings.',
      noEmrAssumableRole:
        'No available EMR assumable role found for the cluster. Please provide one in user profile settings.',
    },
    widgetConnected: 'The notebook is connected to',
    defaultTooltip: 'Select a cluster to connect to',
    widgetHeader:
      'Select a cluster to connect to. A code block will be added to the active cell and run automatically to establish the connection.',
    connectedWidgetHeader: 'cluster. You can submit new jobs to run on the cluster.',
    connectButton: 'Connect',
    learnMore: 'Learn more',
    noResultsMatchingFilters: 'There are no clusters matching the filter.',
    radioButtonLabels: {
      basicAccess: 'Http basic authentication',
      RBAC: 'Role-based access control',
      noCredential: 'No credential',
      kerberos: 'Kerberos',
    },
    fetchEmrRolesError: 'Failed to fetch EMR assumable and execution roles',
    listClusterError: 'Fail to list clusters, refresh the modal or try again later',
    noCluster: 'No clusters are available',
    permissionError:
      'The IAM role SageMakerStudioClassicExecutionRole does not have permissions needed to list EMR clusters. Update the role with appropriate permissions and try again. Refer to the',
    selectCluster: 'Select a cluster',
    selectAssumableRoleTitle: 'Select an assumable role for cluster',
    selectRuntimeExecRoleTitle: 'Select EMR runtime execution role for cluster',
    setUpRuntimeExecRole: 'Please make sure you have run the prerequisite steps.',
    selectAuthTitle: 'Select credential type for ',
    clusterButtonLabel: 'Cluster',
    expandCluster: {
      MasterNodes: 'Master nodes',
      CoreNodes: 'Core nodes',
      NotAvailable: 'Not available',
      NoTags: 'No tags',
      SparkHistoryServer: 'Spark History Server',
      TezUI: 'Tez UI',
      Overview: 'Overview',
      Apps: 'Apps',
      ApplicationUserInterface: 'Application user Interface',
      Tags: 'Tags',
    },
    presignedURL: {
      link: 'Link',
      error: 'Error: ',
      retry: 'Retry',
      sparkUIError: 'Spark UI Link is not available or time out. Please try ',
      sshTunnelLink: 'SSH tunnel',
      or: ' or ',
      viewTheGuide: 'view the guide',
      clusterNotReady: 'Cluster is not ready. Please try again later.',
      clusterNotConnected: 'No active cluster connection. Please connect to a cluster and try again.',
      clusterNotCompatible:
        'EMR version 5.33+ or 6.3.0+ required for direct Spark UI links. Try a compatible cluster, use ',
    },
  },
  DefaultModal: {
    CancelButton: 'Cancel',
    SubmitButton: 'Submit',
  },
  RoleSelectionModal: {
    executionRoleTooltip: 'Select an execution role',
    assumableRoleTooltip: 'Select a cross account assumable role',
  },
  TableLabels: {
    name: 'Name',
    id: 'ID',
    status: 'Status',
    creationTime: 'Creation Time',
    createdOn: 'Created On',
    accountId: 'Account ID',
  },
  EmrClustersDeeplinking: {
    errorDialog: {
      errorTitle: 'Unable to connect to EMR cluster/EMR serverless application',
      defaultErrorMessage: 'Something went wrong when connecting to the EMR cluster/EMR serverless application.',
      invalidRequestErrorMessage:
        'A request to attach the EMR cluster/EMR serverless application to the notebook is invalid.',
      invalidClusterErrorMessage: 'EMR cluster ID is invalid.',
    },
  },
  EmrServerlessApplicationsDeeplinking: {
    errorDialog: {
      invalidApplicationErrorMessage: 'EMR Serverless Application ID is invalid.',
    },
  },
  EmrServerlessApplications: {
    tabName: 'EMR Serverless Applications',
    noApplications: 'No serverless applications are available',
    noResultsMatchingFilters: 'There are no serverless applications matching the filter.',
    connectCommand: {
      label: 'Connect',
      caption: 'Connect to a cluster',
    },
    listApplicationsAccessDeniedException:
      'AccessDeniedException: Please contact your administrator to get permissions to List Applications',
    getApplicationsAccessDeniedException:
      'AccessDeniedException: Please contact your administrator to get permissions to get selected application details',
    expandApplication: {
      Overview: 'Overview',
      NotAvailable: 'Not available',
      NoTags: 'No tags',
      Tags: 'Tags',
      ReleaseLabel: 'Release Label',
      Architecture: 'Architecture',
      InteractiveLivyEndpoint: 'Interactive Livy Endpoint',
      MaximumCapacity: 'Maximum Capacity',
      Cpu: 'Cpu',
      Memory: 'Memory',
      Disk: 'Disk',
    },
  },
};

export { i18nStrings };
