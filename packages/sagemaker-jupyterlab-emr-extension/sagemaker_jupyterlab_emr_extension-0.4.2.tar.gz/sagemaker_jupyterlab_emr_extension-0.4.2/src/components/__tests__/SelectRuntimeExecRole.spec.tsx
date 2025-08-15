import React from 'react';
import { render } from '@testing-library/react';
import { SelectRuntimeExecRole, SelectRuntimeExecRoleProps } from '../SelectRuntimeExecRole';
import { i18nStrings } from '../../constants/i18n';
import { JupyterFrontEnd } from '@jupyterlab/application';
import '@testing-library/jest-dom';

// Mock the necessary props and functions
const app = null as unknown as JupyterFrontEnd;

// Mock the launcherIcon
jest.mock('@jupyterlab/ui-components', () => {
  return {
    launcherIcon: {
      react: jest.fn().mockReturnValue(<span data-testid="launcher-icon">Launcher Icon</span>),
    },
    HTMLSelect: (props) => {
      return (
        <select data-testid="select-runtime-exec-role" {...props}>
          {props.children}
        </select>
      );
    },
  };
});
describe('SelectRuntimeExecRole', () => {
  it('renders select component', () => {
    const mockProps: SelectRuntimeExecRoleProps = {
      onCloseModal: jest.fn(),
      selectedCluster: { clusterAccountId: '012345678910', id: 'id', status: {} },
      emrConnectRoleData: {
        CallerAccountId: 'account-id',
        EmrAssumableRoleArns: [],
        EmrExecutionRoleArns: [
          'arn:aws:iam::012345678910:role/service-role/AmazonSageMaker-ExecutionRole-sample-role-arn1',
        ],
      },
      app: app,
    };

    const { getByTestId } = render(<SelectRuntimeExecRole {...mockProps} />);

    const select = getByTestId('select-runtime-exec-role');
    expect(select).toBeTruthy();
  });

  it('renders error message if no execution role', () => {
    const mockProps: SelectRuntimeExecRoleProps = {
      onCloseModal: jest.fn(),
      selectedCluster: { id: 'id', status: {} },
      emrConnectRoleData: { CallerAccountId: 'cluster-account-id', EmrAssumableRoleArns: [], EmrExecutionRoleArns: [] },
      app: app,
    };

    const { getByText } = render(<SelectRuntimeExecRole {...mockProps} />);
    expect(getByText(i18nStrings.Clusters.selectRoleErrorMessage.noEmrExecutionRole)).toBeInTheDocument();
  });

  it('it has cancel and connect buttons in footer', () => {
    const mockProps: SelectRuntimeExecRoleProps = {
      onCloseModal: jest.fn(),
      selectedCluster: { id: 'id', status: {} },
      emrConnectRoleData: { CallerAccountId: 'cluster-account-id', EmrAssumableRoleArns: [], EmrExecutionRoleArns: [] },
      app: app,
    };

    const { getByText } = render(<SelectRuntimeExecRole {...mockProps} />);
    expect(getByText(i18nStrings.DefaultModal.CancelButton)).toBeInTheDocument();
    expect(getByText(i18nStrings.Clusters.connectButton)).toBeInTheDocument();
  });
});
