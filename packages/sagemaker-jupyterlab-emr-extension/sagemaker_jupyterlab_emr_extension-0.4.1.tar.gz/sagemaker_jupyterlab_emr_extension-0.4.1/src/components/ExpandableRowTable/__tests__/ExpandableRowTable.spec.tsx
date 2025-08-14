import React from 'react';
import { screen, render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ExpandableRowTable, TableProps, ResourceBaseType } from '../ExpandableRowTable';

jest.mock('@jupyterlab/ui-components', () => {
  return {
    Button: jest.fn(),
    caretDownIcon: jest.fn(),
    caretRightIcon: jest.fn(),
  };
});

// Mock the caretDownIcon
jest.mock('@jupyterlab/ui-components', () => {
  return {
    caretDownIcon: {
      react: jest.fn().mockReturnValue(<span data-testid="caret-down-icon">Caret Down Icon</span>),
    },
  };
});

// Mock the caretRightIcon
jest.mock('@jupyterlab/ui-components', () => {
  return {
    caretRightIcon: {
      react: jest.fn().mockReturnValue(<span data-testid="caret-right-icon">Caret Right Icon</span>),
    },
  };
});

type TestRowType = ResourceBaseType & {
  readonly name: string;
  readonly age: number;
  readonly phoneNumber: string;
};

const noResultsView = (
  <div>
    <span>No results to show</span>
  </div>
);

const expandedView = <div>This is the expanded view</div>;

const mockRowData: TestRowType[] = [
  { id: 'id-1', name: 'name-1', age: 32, phoneNumber: '7778889090' },
  { id: 'id-2', name: 'name-2', age: 33, phoneNumber: '7778889091' },
  { id: 'id-3', name: 'name-3', age: 34, phoneNumber: '7778889092' },
  { id: 'id-4', name: 'name-4', age: 35, phoneNumber: '7778889093' },
];

const mockOnRowsSelect = jest.fn();

describe('ExpandableRowTable tests', () => {
  const defaultProps: TableProps<TestRowType> = {
    dataList: [],
    isLoading: false,
    selectedId: '',
    columnConfig: [
      { label: 'Id', dataKey: 'id', disableSort: true, cellRenderer: ({ row }) => row?.id },
      { label: 'Name', dataKey: 'name', disableSort: true, cellRenderer: ({ row }) => row?.name },
      { label: 'Age', dataKey: 'age', disableSort: true, cellRenderer: ({ row }) => row?.age },
      { label: 'phoneNumber', dataKey: 'phoneNumber', disableSort: true, cellRenderer: ({ row }) => row?.phoneNumber },
    ],
    tableConfig: {
      width: 1000,
      height: 1000,
    },
    showIcon: false,
    expandedView: expandedView,
    noResultsView: noResultsView,
    onRowSelect: mockOnRowsSelect,
  };

  const renderWrapper = (newProps?: Partial<TableProps<TestRowType>>) => {
    const props = {
      ...defaultProps,
      ...newProps,
    };
    return render(<ExpandableRowTable {...props} />);
  };

  describe('Empty state tests', () => {
    afterEach(() => {
      jest.resetAllMocks();
    });

    it('renders `Table` in empty state when no data list is passed', () => {
      renderWrapper();

      screen.getByText('No results to show');
    });

    it('renders row header regardless of list size', () => {
      renderWrapper();

      screen.getByText('No results to show');
      expect(screen.getAllByRole('columnheader')).toHaveLength(4);
    });
  });

  describe('With data', () => {
    it('renders the right number of rows', () => {
      renderWrapper({ dataList: mockRowData });

      expect(screen.getAllByRole('row')).toHaveLength(mockRowData.length + 1);
    });

    it('expands selected row', async () => {
      const { rerender } = renderWrapper({ dataList: mockRowData, selectedId: 'id-1' });

      const rows = screen.getAllByRole('row');
      rows.shift(); // remove first header row

      await userEvent.click(rows[1]);
      screen.getByText('This is the expanded view');

      const props: TableProps<TestRowType> = {
        ...defaultProps,
        dataList: mockRowData,
        selectedId: '',
      };
      rerender(<ExpandableRowTable {...props} />);

      await userEvent.click(rows[1]);
      expect(await screen.queryByText('This is the expanded view')).toBeFalsy();
    });

    it('calls onRowsSelect when row is selected', async () => {
      renderWrapper({ dataList: mockRowData, selectedId: '' });

      await userEvent.click(screen.getByText('name-2'));
      expect(mockOnRowsSelect).toHaveBeenCalled();
      expect(mockOnRowsSelect).toHaveBeenCalledWith({ id: 'id-2', name: 'name-2', age: 33, phoneNumber: '7778889091' });
    });
  });
});
