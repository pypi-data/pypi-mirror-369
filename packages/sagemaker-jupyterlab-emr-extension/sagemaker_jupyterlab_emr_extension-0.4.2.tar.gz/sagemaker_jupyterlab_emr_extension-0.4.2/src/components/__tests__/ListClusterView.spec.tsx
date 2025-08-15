import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ListClusterView } from '../ListClusterView';
import { fetchApiResponse } from '../../service/fetchApiWrapper';
import { i18nStrings } from '../../constants/i18n';
import { JupyterFrontEnd } from '@jupyterlab/application';

jest.mock('@jupyterlab/ui-components', () => ({
  caretDownIcon: {
    react: jest.fn().mockReturnValue(<span data-testid="caret-down-icon">Caret Down Icon</span>),
  },
  caretRightIcon: {
    react: jest.fn().mockReturnValue(<span data-testid="caret-right-icon">Caret Right Icon</span>),
  },
}));

jest.mock('../../utils/CommonUtils', () => ({
  arrayHasLength: jest.fn(() => true),
}));

jest.mock('../../service/fetchApiWrapper');
jest.mock('../../utils/ConnectClusterUtils', () => ({
  openSelectAuthType: jest.fn(),
  openSelectAssumableRole: jest.fn(),
}));

describe('ListClusterView Error Handling', () => {
  const onCloseModalMock = jest.fn();
  let app: JupyterFrontEnd;
  const headerMock = <div>Test Header</div>;

  beforeEach(() => {
    // Clear all mocks before each test
    jest.mocked(fetchApiResponse, { shallow: true }).mockClear();
  });

  // Helper function for rendering ListClusterView
  function renderListClusterView() {
    render(<ListClusterView onCloseModal={onCloseModalMock} header={headerMock} app={app} />);
  }

  it('displays a general error message when the API call fails', async () => {
    jest.mocked(fetchApiResponse).mockRejectedValue(new Error('Unable to fetch data'));
    renderListClusterView();
    await waitFor(() => expect(screen.getByText('Unable to fetch data')).toBeInTheDocument());
  });

  it('displays a permission error message when the API returns an AccessDeniedException', async () => {
    jest.mocked(fetchApiResponse).mockRejectedValue(new Error(i18nStrings.Clusters.permissionError));
    renderListClusterView();
    await waitFor(() =>
      expect(
        screen.getByText(/The IAM role.*does not have permissions needed to list EMR clusters/),
      ).toBeInTheDocument(),
    );
  });

  it('displays a no clusters message when API returns an empty list', async () => {
    jest.mocked(fetchApiResponse).mockResolvedValue({ clusters: [] });
    renderListClusterView();
    await waitFor(() => expect(screen.getByText(i18nStrings.Clusters.noResultsMatchingFilters)).toBeInTheDocument());
  });
});
