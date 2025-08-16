import { JupyterFrontEnd, JupyterFrontEndPlugin, IRouter } from '@jupyterlab/application';
import { executeAttachClusterToNewNb } from '../utils/DeepLinkingUtils';

const PLUGIN_ID = '@sagemaker-studio:DeepLinking';
/**
 * Plugin to attach EMR cluster to a new notebook via deep linking
 */
const DeepLinkingPlugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  requires: [IRouter],
  autoStart: true,
  activate: async (app: JupyterFrontEnd, router: IRouter) => {
    const { commands } = app;
    const commandName = 'emrCluster:open-notebook-for-deeplinking';

    commands.addCommand(commandName, {
      execute: () => executeAttachClusterToNewNb(router, app),
    });

    router.register({
      command: commandName,
      pattern: new RegExp('[?]command=attach-emr-to-notebook'),
      rank: 10, // arbitrary ranking to lift this pattern
    });
  },
};

export { DeepLinkingPlugin };
