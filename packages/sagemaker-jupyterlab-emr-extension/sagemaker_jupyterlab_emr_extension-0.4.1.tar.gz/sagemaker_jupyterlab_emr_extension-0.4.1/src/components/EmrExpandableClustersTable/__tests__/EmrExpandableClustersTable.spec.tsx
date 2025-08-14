import React from 'react';
import { render, screen } from '@testing-library/react';
import { EmrExpandedClustersTable, TableProps } from '../EmrExpandableClustersTable';

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

//TODO: Update type here once schema is ready
const clusterManagementConfig: any[] = [
  {
    dataKey: 'name',
    label: 'Name',
    disableSort: true,
    cellRenderer: ({ row: rowData }) => rowData?.name,
  },
  {
    dataKey: 'id',
    label: 'Id',
    disableSort: true,
    cellRenderer: ({ row: rowData }) => rowData?.id,
  },
];

const mockOnRowsSelect = jest.fn();
const defaultProps: TableProps = {
  clustersList: [],
  clusterArn: '',
  accountId: '',
  onRowSelect: mockOnRowsSelect,
  tableConfig: {
    width: 100,
    height: 100,
  },
  clusterManagementListConfig: clusterManagementConfig,
  selectedClusterId: '',
  sort: () => null,
  sortDirection: 'ASC',
  sortBy: '',
  clusterDetails: undefined,
};

const getClustersList: any = () => [
  {
    id: 'cluster-1',
    name: 'first cluster',
    clusterArn: 'arn:aws:elasticmapreduce:us-west-2:331110439030:cluster/j-2SZDSOMN6OJFS',
    status: {
      state: 'RUNNING',
      stateChangeReason: 'No reason',
    },
  },
  {
    id: 'cluster-2',
    name: 'second cluster',
    clusterArn: 'arn:aws:elasticmapreduce:us-west-2:331110439030:cluster/j-2SZDSOMN6OJFP',
    status: {
      state: 'RUNNING',
      stateChangeReason: 'No reason',
    },
  },
];

//TODO:: come back to fixing unit test for this component
xdescribe('ExpandedClustersTable tests', () => {
  afterEach(() => jest.clearAllMocks());

  const renderWrapper = (props?: Partial<TableProps>) => {
    const finalProps = {
      ...defaultProps,
      ...props,
    };

    return render(<EmrExpandedClustersTable {...finalProps} />);
  };

  //TODO:: Add/Update test for loading state once we do API integration
  xdescribe('When loading is `false`', () => {
    it('calls the query functions when a different cluster is selected', () => {
      const { rerender } = renderWrapper({ clustersList: getClustersList(), selectedClusterId: '' });

      const props: TableProps = {
        ...defaultProps,
        selectedClusterId: 'cluster-1',
      };

      rerender(<EmrExpandedClustersTable {...props} />);
    });

    it('renders component when `isLoading` is false', () => {
      renderWrapper({ clustersList: getClustersList(), selectedClusterId: 'cluster-1' });

      expect(screen.queryByText('Loading')).toBeFalsy();
      screen.getByText('Cluster Information');
    });
  });
});
