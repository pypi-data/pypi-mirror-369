import * as DeepLinkingUtils from '../DeepLinkingUtils';

import { showErrorMessage } from '@jupyterlab/apputils';

// Mock dependencies
jest.mock('@jupyterlab/apputils', () => ({
  showErrorMessage: jest.fn(),
}));
const showErrorMessageMock = showErrorMessage as jest.Mock;
jest.mock('../../service/presignedURL', () => ({
  describeCluster: jest.fn(),
  getServerlessApplication: jest.fn(),
}));
jest.mock('../../utils/ConnectClusterUtils', () => ({
  openSelectAuthType: jest.fn(),
  openSelectAssumableRole: jest.fn(),
}));
jest.mock('../../service');
jest.mock('../../service/fetchApiWrapper');

describe('DeepLinkingUtils', () => {
  let mockApp: any;
  let mockRouter: any;

  beforeEach(() => {
    jest.resetModules();
    jest.mock('../../utils/DeepLinkingUtils', () => {
      return {
        __esModule: true,
        ...jest.requireActual('../../utils/DeepLinkingUtils'),
        createNewNotebook: jest.fn(),
        isPatternMatched: false,
      };
    });
    mockApp = {
      restored: Promise.resolve(),
      commands: {
        execute: jest.fn(),
      },
    };
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should show error message for invalid request without cluster or application ID', async () => {
    mockRouter = {
      current: {
        search:
          'https://xtiazqb2qkxve3m.studio.us-east-2.sagemaker.aws/jupyterlab/default/lab?command=attach-emr-to-notebook',
      },
    };

    await DeepLinkingUtils.executeAttachClusterToNewNb(mockRouter, mockApp);
    expect(showErrorMessageMock).toHaveBeenCalledWith('Unable to connect to EMR cluster/EMR serverless application', {
      message: 'A request to attach the EMR cluster/EMR serverless application to the notebook is invalid.',
    });
  });
  it('should show error message for invalid request', async () => {
    mockRouter = {
      current: {
        search: '',
      },
    };
    // @ts-ignore
    DeepLinkingUtils.isPatternMatched = false;
    await DeepLinkingUtils.executeAttachClusterToNewNb(mockRouter, mockApp);
    expect(showErrorMessageMock).toHaveBeenCalledWith('Unable to connect to EMR cluster/EMR serverless application', {
      message: 'A request to attach the EMR cluster/EMR serverless application to the notebook is invalid.',
    });
  });

  describe('attachClusterToNotebook', () => {
    it('should show error message for invalid cluster', async () => {
      await DeepLinkingUtils.attachClusterToNotebook('invalid-cluster-id', mockApp, undefined, {});
      expect(showErrorMessageMock).toHaveBeenCalledWith('Unable to connect to EMR cluster/EMR serverless application', {
        message: 'EMR cluster ID is invalid.',
      });
    });
  });

  describe('attachServerlessApplicationToNotebook', () => {
    it('should show error message for invalid application', async () => {
      await DeepLinkingUtils.attachServerlessApplicationToNotebook('invalid-app-id', mockApp, undefined, {});
      expect(showErrorMessageMock).toHaveBeenCalledWith('Unable to connect to EMR cluster/EMR serverless application', {
        message: 'EMR Serverless Application ID is invalid.',
      });
    });
  });
});
