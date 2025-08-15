import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { SelectAuthType, SelectAuthTypeProps } from '../SelectAuthType';
import { i18nStrings } from '../../constants/i18n';
import { JupyterFrontEnd } from '@jupyterlab/application';

// Mock the necessary props and functions
const app = null as unknown as JupyterFrontEnd;

jest.mock('../../utils/ConnectClusterUtils', () => ({ openSelectRuntimeExecRole: jest.fn() }));

const mockProps: SelectAuthTypeProps = {
  onCloseModal: jest.fn(),
  selectedCluster: { id: 'id', status: {} },
  emrConnectRoleData: { CallerAccountId: 'cluster-account-id', EmrAssumableRoleArns: [], EmrExecutionRoleArns: [] },
  app: app,
};

describe('SelectAuthType', () => {
  it('renders component with default auth type', () => {
    const { getByLabelText } = render(<SelectAuthType {...mockProps} />);

    // Ensure that the component renders with default auth type 'Basic_Access'
    expect(getByLabelText(i18nStrings.Clusters.radioButtonLabels.basicAccess)).toBeInTheDocument();
    expect(getByLabelText(i18nStrings.Clusters.radioButtonLabels.RBAC)).toBeInTheDocument();
    expect(getByLabelText(i18nStrings.Clusters.radioButtonLabels.noCredential)).toBeInTheDocument();
    expect(getByLabelText(i18nStrings.Clusters.radioButtonLabels.kerberos)).toBeInTheDocument();

    // basic access will be checked by default
    const basicAccessRadio = getByLabelText(i18nStrings.Clusters.radioButtonLabels.basicAccess);
    expect(basicAccessRadio).toBeChecked();
  });
});
