import React from 'react';
import { CircularProgress } from '@mui/material';
import { ExpandableRowTable } from '../ExpandableRowTable/ExpandableRowTable';
import { i18nStrings } from '../../constants/i18n';
import { SortDirectionType } from 'react-virtualized';
import * as Styles from '../EmrExpandableClustersTable/styles';
import { ServerlessApplication, ServerlessApplicationRowType } from '../../constants/types';
import { ServerlessApplicationDetails } from './ServerlessApplicationDetails/ServerlessApplicationDetails';

type TableConfig = {
  width: number;
  height: number;
  className?: string;
};

interface TableProps {
  selectedApplicationId: string;
  applicationArn: string;
  accountId: string | undefined;
  applicationsList: ServerlessApplicationRowType[];
  applicationDetails: ServerlessApplication | undefined;
  tableConfig: TableConfig;
  applicationManagementListConfig: any;
  onRowSelect: (clusterRowData: any) => void;
  sort?: (sortBy: string, sortDirection: SortDirectionType) => void;
  sortBy?: string | undefined;
  sortDirection?: SortDirectionType;
  applicationDetailsLoading: boolean;
}

const widgetStrings = i18nStrings.Clusters;

const noResultsView = (
  <div className={Styles.NoResultsContainer}>
    <p className={Styles.NoResultsMessage}>{widgetStrings.noResultsMatchingFilters}</p>
  </div>
);

const EmrServerlessExpandableApplicationsTable: React.FunctionComponent<TableProps> = ({
  applicationsList,
  tableConfig,
  applicationManagementListConfig,
  selectedApplicationId,
  applicationArn,
  accountId,
  onRowSelect,
  applicationDetails,
  applicationDetailsLoading,
  ...rest
}) => {
  const rowTable = (
    <ExpandableRowTable
      {...rest}
      tableConfig={tableConfig}
      showIcon
      dataList={applicationsList}
      selectedId={selectedApplicationId}
      columnConfig={applicationManagementListConfig}
      isLoading={applicationDetailsLoading}
      noResultsView={noResultsView}
      onRowSelect={onRowSelect}
      expandedView={
        applicationDetailsLoading ? (
          <span>
            <CircularProgress size="1rem" />
          </span>
        ) : (
          <ServerlessApplicationDetails applicationData={applicationDetails} />
        )
      }
    />
  );
  return rowTable;
};

export { EmrServerlessExpandableApplicationsTable, TableConfig, TableProps };
