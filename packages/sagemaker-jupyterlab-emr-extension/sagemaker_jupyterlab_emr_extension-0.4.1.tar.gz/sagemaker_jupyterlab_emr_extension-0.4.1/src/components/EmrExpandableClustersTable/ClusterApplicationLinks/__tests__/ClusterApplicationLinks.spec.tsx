import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { ClusterApplicationLinks } from '../ClusterApplicationLinks';

// Mock the launcherIcon
jest.mock('@jupyterlab/ui-components', () => {
  return {
    launcherIcon: {
      react: jest.fn().mockReturnValue(<span data-testid="launcher-icon">Launcher Icon</span>),
    },
  };
});

describe('ClusterApplicationLinks', () => {
  it('renders the component without errors', () => {
    const { getByText } = render(
      <ClusterApplicationLinks selectedClusterId="clusterId" accountId="accountId" clusterArn="clusterArn" />,
    );

    expect(getByText('Spark History Server')).toBeInTheDocument();
    expect(getByText('Tez UI')).toBeInTheDocument();
  });

  //TODO: Uncomment when we have a error state handled through API integration
  xit('displays an error message when isError is true', () => {
    const { getByText } = render(
      <ClusterApplicationLinks selectedClusterId="clusterId" accountId="accountId" clusterArn="clusterArn" />,
    );

    // Simulate an error by setting isError to true
    fireEvent.click(getByText('Spark History Server'), { isError: true });

    expect(getByText('Not Available')).toBeInTheDocument();
  });

  xit('does not display an error message when isError is false', () => {
    const { queryByText } = render(
      <ClusterApplicationLinks selectedClusterId="clusterId" accountId="accountId" clusterArn="clusterArn" />,
    );
    expect(queryByText('Not Available')).toBeNull();

    // Click on the link to SparkServerHistoryLink (simulated success)
    fireEvent.click(getByText('Spark History Server'));

    expect(queryByText('Not Available')).toBeNull();
  });
});
