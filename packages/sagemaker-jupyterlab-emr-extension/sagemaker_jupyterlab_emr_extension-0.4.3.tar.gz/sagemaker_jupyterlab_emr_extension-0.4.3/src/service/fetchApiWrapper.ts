//Source: https://code.amazon.com/packages/SageMakerStudioJupyterLabExtension
import { ServerConnection } from '@jupyterlab/services';
import { URLExt } from '@jupyterlab/coreutils';
import { SUCCESS_RESPONSE_STATUS } from './constants';

enum OPTIONS_TYPE {
  POST = 'POST',
  GET = 'GET',
  PUT = 'PUT',
}

type OptionsType = OPTIONS_TYPE;

/**
 * Function call to make API calls for the plugin
 */
const fetchApiResponse = async (endpoint: string, type: OptionsType, params?: BodyInit) => {
  // @TODO: add in logger
  const settings = ServerConnection.makeSettings();
  const requestUrl = URLExt.join(settings.baseUrl, endpoint);
  try {
    const response = await ServerConnection.makeRequest(requestUrl, { method: type, body: params }, settings);
    if (!SUCCESS_RESPONSE_STATUS.includes(response.status) && requestUrl.includes('list-clusters')) {
      if (response.status === 400) {
        throw new Error('permission error');
      } else {
        throw new Error('Unable to fetch data');
      }
    }
    return response.json();
  } catch (error: any) {
    return { error: error };
    // @TODO: add in logger
    // const { current: logger } = rootLoggerContainer;
    // if (logger) {
    //   logger.warn({
    //     schema: ClientSchemas.ClientError,
    //     message: ClientErrorMessage.InstanceTypeNetworkError,
    //     error,
    //   });
    // }
  }
};

export { fetchApiResponse, OPTIONS_TYPE };
