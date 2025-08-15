import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { SparkServerHistoryLink } from '../SparkServerHistoryLink';
import { i18nStrings } from '../../../../constants/i18n';

// Mock the launcherIcon
jest.mock('@jupyterlab/ui-components', () => {
  return {
    launcherIcon: {
      react: jest.fn().mockReturnValue(<span data-testid="launcher-icon">Launcher Icon</span>),
    },
  };
});

const expandClusterStrings = i18nStrings.Clusters.expandCluster;

xdescribe('SparkServerHistoryLink', () => {
  it('renders the component without errors', () => {
    const { getByText } = render(
      <SparkServerHistoryLink clusterId="j-io02302013" accountId="accountId" setIsError={() => {}} />,
    );

    // You can use RTL queries to assert that specific elements are present based on your component's structure
    expect(getByText(expandClusterStrings.SparkHistoryServer)).toBeInTheDocument();
  });

  //TODO: Fix this test once error handling is added
  xit('does not call setIsError when clicked while loading', () => {
    const setIsErrorMock = jest.fn();

    const { getByText } = render(
      <SparkServerHistoryLink clusterId="j-io02302013" accountId="accountId" setIsError={setIsErrorMock} />,
    );

    const link = getByText('Spark History Server');

    // Simulate a click on the link
    fireEvent.click(link);

    // Assert that setIsErrorMock was not called
    expect(setIsErrorMock).not.toHaveBeenCalled();
  });
});
