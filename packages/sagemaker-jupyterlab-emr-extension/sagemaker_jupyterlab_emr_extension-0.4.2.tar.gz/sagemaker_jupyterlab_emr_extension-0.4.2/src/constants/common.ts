import { TableConfig } from '../components/EmrExpandableClustersTable/EmrExpandableClustersTable';

const EmrClusterPluginClassNames = {
  EmrClusterContainer: 'EmrClusterContainer',
  EmrClusterButton: 'EmrClusterButton',
  SelectedCellClassname: 'SelectedCell',
  HoveredCellClassname: 'HoveredCellClassname',
  ExpandedRowInformation: 'ExpandedRowInformation',
  HistoryLink: 'HistoryLink',
  SelectAuthContainer: 'SelectAuthContainer',
  SelectEMRAccessRoleContainer: 'SelectEMRAccessRoleContainer',
};

enum COMMAND_IDS {
  emrConnect = 'sagemaker-studio:emr-connect',
  emrServerlessConnect = 'sagemaker-studio:emr-serverless-connect',
}

export { EmrClusterPluginClassNames, COMMAND_IDS };

export const DEFAULT_TABLE_CONFIG: TableConfig = {
  width: 850,
  height: 500,
};

export enum ColumnConfigDataKeys {
  name = 'name',
  id = 'id',
  status = 'status',
  creationDateTime = 'creationDateTime',
  arn = 'clusterArn',
}

export const ACCESS_DENIED_EXCEPTION = 'AccessDeniedException';
