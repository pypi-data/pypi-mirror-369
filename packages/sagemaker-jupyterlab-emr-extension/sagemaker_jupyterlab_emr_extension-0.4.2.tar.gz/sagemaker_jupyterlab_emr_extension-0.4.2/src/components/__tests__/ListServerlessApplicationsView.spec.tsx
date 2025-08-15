import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ListServerlessApplicationsView } from '../ListServerlessApplicationsView';
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
  closeIcon: {
    react: jest.fn().mockReturnValue(<span data-testid="close-icon">Close Icon</span>),
  },
}));

jest.mock('../../utils/CommonUtils', () => ({
  arrayHasLength: jest.fn(() => true),
}));

jest.mock('../../utils/ConnectClusterUtils', () => ({
  openSelectAuthType: jest.fn(),
  openSelectAssumableRole: jest.fn(),
}));

jest.mock('../../service/fetchApiWrapper');

describe('ListServerlessApplicationsView Error Handling', () => {
  const onCloseModalMock = jest.fn();
  let app: JupyterFrontEnd;
  const headerMock = <div>Test Header</div>;

  beforeEach(() => {
    jest.mocked(fetchApiResponse, { shallow: true }).mockClear();
  });

  // Helper function for rendering ListServerlessApplicationsView
  function renderListServerlessApplicationsView() {
    render(<ListServerlessApplicationsView onCloseModal={onCloseModalMock} header={headerMock} app={app} />);
  }

  it('displays a no clusters message when API returns an empty list', async () => {
    const mockFetchApiResponse = jest.mocked(fetchApiResponse);
    mockFetchApiResponse.mockReturnValueOnce(Promise.resolve({ applications: [] }));
    mockFetchApiResponse.mockReturnValueOnce(Promise.resolve({ CallerAccountId: 'mockId' })); // for fetch emr roles api

    renderListServerlessApplicationsView();
    await waitFor(() => expect(screen.getByText(i18nStrings.Clusters.noResultsMatchingFilters)).toBeInTheDocument());
  });
});
