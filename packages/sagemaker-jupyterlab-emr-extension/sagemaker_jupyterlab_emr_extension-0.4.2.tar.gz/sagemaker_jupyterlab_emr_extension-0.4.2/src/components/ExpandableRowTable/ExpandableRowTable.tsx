import React, { useEffect, useRef, useState } from 'react';
import {
  Column,
  defaultTableCellDataGetter,
  Table,
  TableCellProps,
  TableCellDataGetter,
  Index,
  TableRowRenderer,
} from 'react-virtualized';
import { defaultRowRenderer } from 'react-virtualized/dist/commonjs/Table';
import { cx } from '@emotion/css';
import { caretDownIcon, caretRightIcon } from '@jupyterlab/ui-components';
import * as Styles from './styles';

interface TableConfig {
  width: number;
  height: number;
  className?: string;
}

interface IconProps {
  isSelected: boolean;
}

interface ResourceBaseType {
  readonly id: string;
}

const RowIcon: React.FunctionComponent<IconProps> = ({ isSelected }) => {
  if (isSelected) {
    return <caretDownIcon.react tag="span" />;
  }

  return <caretRightIcon.react tag="span" />;
};

//TODO: update columnConfig type when api schema is ready
interface TableProps<T extends ResourceBaseType> {
  readonly dataList: T[];
  readonly tableConfig: TableConfig;
  readonly columnConfig: any[];
  readonly isLoading?: boolean;
  readonly selectedId: string;
  readonly showIcon?: boolean;
  readonly expandedView: JSX.Element | null;
  readonly noResultsView: JSX.Element | null;
  /* methods */
  readonly onRowSelect: (rowData: T) => void;
}

const DEFAULT_ROW_HEIGHT = 40;
const DEFAULT_COLUMN_WIDTH = 150;

const ExpandableRowTable = <RowType extends ResourceBaseType>({
  dataList,
  tableConfig,
  selectedId,
  expandedView,
  noResultsView,
  showIcon,
  isLoading,
  columnConfig,
  onRowSelect,
  ...rest
}: TableProps<RowType>): ReturnType<React.FunctionComponent<TableProps<RowType>>> => {
  const tableRef = useRef<Table>(null);
  const expandedRef = useRef<HTMLDivElement>(null);
  const [hoveredRowIndex, setHoveredRowIndex] = useState(-1);
  const [expandedRowHeight, setExpandedRowHeight] = useState(0);

  const recomputeRowHeights = () => {
    setExpandedRowHeight(expandedRef?.current?.clientHeight || DEFAULT_ROW_HEIGHT);
    tableRef.current?.recomputeRowHeights();
  };

  useEffect(() => {
    recomputeRowHeights();
  }, [selectedId, isLoading, tableConfig.width, tableConfig.height]);

  /**
   * Cell rendering methods
   */
  //TODO: Update cellRenderer row type once api shchema is ready
  const cellDataGetter: TableCellDataGetter = ({ rowData, ...rest }) =>
    rowData ? defaultTableCellDataGetter({ rowData, ...rest }) : null;

  const renderCellData = (rendererProps: TableCellProps, cellRenderer: any | undefined) => {
    const { rowIndex, columnIndex } = rendererProps;
    const isSelected = dataList[rowIndex].id === selectedId;
    const isFirstColumn = columnIndex === 0;
    let cellContentToRender: React.ReactNode = null;

    if (cellRenderer) {
      cellContentToRender = cellRenderer({
        row: dataList[rowIndex],
        rowIndex,
        columnIndex,
        onCellSizeChange: () => null,
      });
    }

    if (isFirstColumn && showIcon) {
      return (
        <>
          <RowIcon isSelected={isSelected} /> {cellContentToRender}
        </>
      );
    }

    return cellContentToRender;
  };

  /**
   * Row rendering methods
   **/
  const getRowHeight: (params: Index) => number = ({ index }) =>
    dataList[index].id && dataList[index].id === selectedId ? expandedRowHeight : DEFAULT_ROW_HEIGHT;

  const rowRenderer: TableRowRenderer = (rendererProps) => {
    const { style, key, rowData, index, className } = rendererProps;
    const isRowSelected = selectedId === rowData.id;
    const isRowHovered = hoveredRowIndex === index;

    const rowClassName = cx(Styles.ExpandableRow, className, {
      [Styles.SelectedRowInfo]: isRowSelected,
      [Styles.HoveredRow]: isRowSelected ? false : isRowHovered,
    });

    if (isRowSelected) {
      return (
        <div
          key={key}
          ref={expandedRef}
          style={{ ...style, ...Styles.ExpandedRowContainer }}
          onMouseEnter={() => setHoveredRowIndex(index)}
          onMouseLeave={() => setHoveredRowIndex(-1)}
          className={rowClassName}
        >
          {defaultRowRenderer({
            ...rendererProps,
            style: {
              width: style.width,
              ...Styles.Row,
            },
          })}
          <div className={Styles.ExpandedRowInfo}>{expandedView}</div>
        </div>
      );
    }

    return (
      <div key={key} onMouseEnter={() => setHoveredRowIndex(index)} onMouseLeave={() => setHoveredRowIndex(-1)}>
        {defaultRowRenderer({
          ...rendererProps,
          className: rowClassName,
        })}
      </div>
    );
  };

  return (
    <Table
      {...rest}
      {...tableConfig}
      headerStyle={Styles.TableHeaderRow}
      ref={tableRef}
      headerHeight={DEFAULT_ROW_HEIGHT}
      overscanRowCount={10}
      rowCount={dataList.length}
      rowData={dataList}
      noRowsRenderer={() => noResultsView}
      rowHeight={getRowHeight}
      rowRenderer={rowRenderer}
      onRowClick={({ rowData }) => onRowSelect(rowData)}
      rowGetter={({ index }) => dataList[index]}
    >
      {columnConfig.map(({ dataKey, label, disableSort, cellRenderer: cellRendererFromConfig }) => (
        <Column
          key={dataKey}
          dataKey={dataKey}
          label={label}
          flexGrow={1}
          width={DEFAULT_COLUMN_WIDTH}
          disableSort={disableSort}
          cellDataGetter={cellDataGetter}
          cellRenderer={(cellRendererProps) => renderCellData(cellRendererProps, cellRendererFromConfig)}
        />
      ))}
    </Table>
  );
};

export { ExpandableRowTable, TableProps, TableConfig, ResourceBaseType };
