import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ClusterTabs } from '../ListClusterWidget';
import { JupyterFrontEnd } from '@jupyterlab/application';
import '@testing-library/jest-dom';

jest.mock('@jupyterlab/ui-components', () => ({
  caretDownIcon: {
    react: jest.fn().mockReturnValue(<span data-testid="caret-down-icon">Caret Down Icon</span>),
  },
  caretRightIcon: {
    react: jest.fn().mockReturnValue(<span data-testid="caret-right-icon">Caret Right Icon</span>),
  },
}));

jest.mock('../utils/ConnectClusterUtils', () => ({ openSelectRuntimeExecRole: jest.fn() }));

describe('ClusterTabs', () => {
  const mockOnCloseModal = jest.fn();
  const mockHeader = <div>Header</div>;
  let mockApp: JupyterFrontEnd;

  it('renders the tabs correctly', async () => {
    render(<ClusterTabs onCloseModal={mockOnCloseModal} header={mockHeader} app={mockApp} />);
    expect(screen.getByText('EMR Serverless Applications')).toBeInTheDocument();
    expect(screen.getByText('EMR Clusters')).toBeInTheDocument();
  });

  it('switches tabs correctly', () => {
    render(<ClusterTabs onCloseModal={mockOnCloseModal} header={mockHeader} app={mockApp} />);

    const serverlessTab = screen.getByText('EMR Serverless Applications');
    const clusterTab = screen.getByText('EMR Clusters');

    fireEvent.click(serverlessTab);
    expect(screen.getByTestId('list-serverless-applications-view')).toBeInTheDocument();

    fireEvent.click(clusterTab);
    expect(screen.getByTestId('list-cluster-view')).toBeInTheDocument();
  });
});
