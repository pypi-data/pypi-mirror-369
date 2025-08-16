import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { TezServerHistoryLink } from '../TezServerHistoryLink';
import { i18nStrings } from '../../../../constants/i18n';

// Mock the closeIcon
jest.mock('@jupyterlab/ui-components', () => {
  return {
    launcher: {
      react: jest.fn().mockReturnValue(<span data-testid="launcher-icon">Launcher Icon</span>),
    },
  };
});

const expandClusterStrings = i18nStrings.Clusters.expandCluster;

xdescribe('TezServerHistoryLink', () => {
  it('renders the component without errors', () => {
    const { getByText } = render(
      <TezServerHistoryLink clusterId="j-io02302013" accountId="accountId" setIsError={() => {}} />,
    );

    expect(getByText(expandClusterStrings.TezUI)).toBeInTheDocument();
  });

  //TODO: Uncomment when we have a error state handled through API integration
  xit('calls setIsError when clicked while not loading', () => {
    const setIsErrorMock = jest.fn();

    const { getByText } = render(
      <TezServerHistoryLink clusterId="j-io02302013" accountId="accountId" setIsError={setIsErrorMock} />,
    );

    const link = getByText(expandClusterStrings.TezUI);
    fireEvent.click(link);

    expect(setIsErrorMock).toHaveBeenCalledWith(false);
  });

  xit('does not call setIsError when clicked while loading', () => {
    const setIsErrorMock = jest.fn();

    const { getByText } = render(<TezServerHistoryLink accountId="accountId" setIsError={setIsErrorMock} />);

    const link = getByText(expandClusterStrings.TezUI);
    const component = getByText(expandClusterStrings.TezUI);
    component.isLoading = true;

    fireEvent.click(link);
    expect(setIsErrorMock).not.toHaveBeenCalled();
  });
});
