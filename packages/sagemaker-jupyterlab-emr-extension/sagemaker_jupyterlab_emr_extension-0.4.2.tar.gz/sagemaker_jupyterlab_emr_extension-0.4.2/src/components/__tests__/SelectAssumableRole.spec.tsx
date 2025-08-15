import React from 'react';
import { render } from '@testing-library/react';
import { SelectAssumableRole, SelectAssumableRoleProps } from '../SelectAssumableRole';
import { i18nStrings } from '../../constants/i18n';
import { JupyterFrontEnd } from '@jupyterlab/application';
import '@testing-library/jest-dom/extend-expect';

// Mock the necessary props and functions
const app = null as unknown as JupyterFrontEnd;

jest.mock('../../utils/ConnectClusterUtils', () => ({ openSelectRuntimeExecRole: jest.fn() }));

const mockProps: SelectAssumableRoleProps = {
  onCloseModal: jest.fn(),
  selectedCluster: { clusterAccountId: '012345678910', id: 'id', status: {} },
  emrConnectRoleData: {
    CallerAccountId: 'cluster-account-id',
    EmrAssumableRoleArns: [
      'arn:aws:iam::012345678910:role/service-role/AmazonSageMaker-AssumableRole-sample-role-arn1',
    ],
    EmrExecutionRoleArns: [],
  },
  app: app,
};

jest.mock('@jupyterlab/ui-components', () => ({
  HTMLSelect: (props) => {
    return (
      <select data-testid="select-assumable-role" {...props}>
        {props.children}
      </select>
    );
  },
}));

describe('SelectAssumableRole', () => {
  it('it has cancel and connect buttons in footer', () => {
    const { getByText } = render(<SelectAssumableRole {...mockProps} />);

    expect(getByText(i18nStrings.DefaultModal.CancelButton)).toBeInTheDocument();
    expect(getByText(i18nStrings.Clusters.connectButton)).toBeInTheDocument();
  });

  it('it has select component', () => {
    const { getByTestId } = render(<SelectAssumableRole {...mockProps} />);

    const select = getByTestId('select-assumable-role');
    expect(select).toBeTruthy();
  });
});
