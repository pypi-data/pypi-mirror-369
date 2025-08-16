import React from 'react';
import { i18nStrings } from '../constants/i18n';
import { Arn } from '../utils/ArnUtils';
import { CellStatusRenderer } from './CellStatusRenderer';
import { ColumnConfigDataKeys } from '../constants';

const widgetStrings = i18nStrings.TableLabels;

interface RowData {
  name?: string;
  id?: number;
  status?: {
    state: string;
    timeline: {
      creationDateTime: string;
    };
  };
  clusterArn?: string;
}

const GetColumnConfig = () => {
  const columnConfig = [
    {
      dataKey: ColumnConfigDataKeys.name,
      label: widgetStrings.name,
      disableSort: true,
      cellRenderer: ({ row: rowData }: { row: RowData }) => rowData?.name,
    },
    {
      dataKey: ColumnConfigDataKeys.id,
      label: widgetStrings.id,
      disableSort: true,
      cellRenderer: ({ row: rowData }: { row: RowData }) => rowData?.id,
    },
    {
      dataKey: ColumnConfigDataKeys.status,
      label: widgetStrings.status,
      disableSort: true,
      cellRenderer: ({ row: rowData }: { row: RowData }) => <CellStatusRenderer cellData={rowData} />,
    },
    {
      dataKey: ColumnConfigDataKeys.creationDateTime,
      label: widgetStrings.creationTime,
      disableSort: true,
      cellRenderer: ({ row: rowData }: { row: RowData }) =>
        rowData?.status?.timeline.creationDateTime.split('+')[0].split('.')[0],
    },
    {
      dataKey: ColumnConfigDataKeys.arn,
      label: widgetStrings.accountId,
      disableSort: true,
      cellRenderer: ({ row: rowData }: { row: RowData }) => {
        if (rowData?.clusterArn) {
          return Arn.fromArnString(rowData.clusterArn).accountId;
        }
        return;
      },
    },
  ];
  return columnConfig;
};

export { GetColumnConfig };
