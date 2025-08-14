import React from 'react';
import { CircularProgress } from '@mui/material';
import { ExpandableRowTable } from '../ExpandableRowTable/ExpandableRowTable';
import { i18nStrings } from '../../constants/i18n';
import { SortDirectionType } from 'react-virtualized';
import * as Styles from './styles';
import { ClusterDetails } from './ClusterDetails/ClusterDetails';
import { Cluster, ClusterRowType, ListInstanceGroupsOutput } from '../../constants/types';

type TableConfig = {
  width: number;
  height: number;
  className?: string;
};

//TODO: Add clusterManagementListConfig type as DataGridColumnConfig.See if we need dataGrid type here to resolve
interface TableProps {
  selectedClusterId: string;
  clusterArn: string;
  accountId: string | undefined;
  clustersList: ClusterRowType[];
  clusterDetails: Cluster | undefined;
  tableConfig: TableConfig;
  clusterManagementListConfig: any;
  onRowSelect: (clusterRowData: any) => void;
  sort?: (sortBy: string, sortDirection: SortDirectionType) => void;
  sortBy?: string | undefined;
  sortDirection?: SortDirectionType;
}

const widgetStrings = i18nStrings.Clusters;

const noResultsView = (
  <div className={Styles.NoResultsContainer}>
    <p className={Styles.NoResultsMessage}>{widgetStrings.noResultsMatchingFilters}</p>
  </div>
);

const EmrExpandedClustersTable: React.FunctionComponent<TableProps> = ({
  clustersList,
  tableConfig,
  clusterManagementListConfig,
  selectedClusterId,
  clusterArn,
  accountId,
  onRowSelect,
  clusterDetails,
  ...rest
}) => {
  //TODO:ADD handling of instanceGroupData
  const isLoading = !clusterDetails && false;

  const clusterDescriptionData: Cluster | undefined = clusterDetails;
  const instanceGroupsData: ListInstanceGroupsOutput | undefined = undefined;

  const rowTable = (
    <ExpandableRowTable
      {...rest}
      tableConfig={tableConfig}
      showIcon
      dataList={clustersList}
      selectedId={selectedClusterId}
      columnConfig={clusterManagementListConfig}
      isLoading={isLoading}
      noResultsView={noResultsView}
      onRowSelect={onRowSelect}
      expandedView={
        isLoading ? (
          <span>
            <CircularProgress size="1rem" />
          </span>
        ) : (
          <ClusterDetails
            selectedClusterId={selectedClusterId}
            accountId={accountId || ''}
            clusterArn={clusterArn}
            clusterData={clusterDescriptionData}
            instanceGroupData={instanceGroupsData}
          />
        )
      }
    />
  );
  return rowTable;
};

export { EmrExpandedClustersTable, TableConfig, TableProps };
