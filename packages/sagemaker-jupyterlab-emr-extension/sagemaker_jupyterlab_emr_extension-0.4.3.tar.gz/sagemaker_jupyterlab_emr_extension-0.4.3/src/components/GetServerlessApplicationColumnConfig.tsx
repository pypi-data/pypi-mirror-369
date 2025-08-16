import React from 'react';
import { i18nStrings } from '../constants/i18n';
import { Arn } from '../utils/ArnUtils';
import { ColumnConfigDataKeys, ServerlessApplicationState } from '../constants';

const widgetStrings = i18nStrings.TableLabels;

interface RowData {
  name?: string;
  id?: number;
  status?: string;
  createdAt?: string;
  arn?: string;
}

const CellStatusRenderer: React.FunctionComponent<any> = ({ status }) => {
  if (
    status === ServerlessApplicationState.Started ||
    status === ServerlessApplicationState.Stopped ||
    status === ServerlessApplicationState.Created
  ) {
    return (
      <div>
        <svg width="10" height="10">
          <circle cx="5" cy="5" r="5" fill="green" />
        </svg>
        <label htmlFor="myInput"> {status}</label>
      </div>
    );
  }

  return (
    <div>
      <label htmlFor="myInput">{status}</label>
    </div>
  );
};
const GetServerlessApplicationColumnConfig = () => {
  return [
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
      cellRenderer: ({ row: rowData }: { row: RowData }) => <CellStatusRenderer status={rowData.status} />,
    },
    {
      dataKey: ColumnConfigDataKeys.creationDateTime,
      label: widgetStrings.creationTime,
      disableSort: true,
      cellRenderer: ({ row: rowData }: { row: RowData }) => rowData?.createdAt?.split('+')[0].split('.')[0],
    },
    {
      dataKey: ColumnConfigDataKeys.arn,
      label: widgetStrings.accountId,
      disableSort: true,
      cellRenderer: ({ row: rowData }: { row: RowData }) => {
        if (rowData?.arn) {
          return Arn.fromArnString(rowData.arn).accountId;
        }
        return;
      },
    },
  ];
};

export { GetServerlessApplicationColumnConfig };
