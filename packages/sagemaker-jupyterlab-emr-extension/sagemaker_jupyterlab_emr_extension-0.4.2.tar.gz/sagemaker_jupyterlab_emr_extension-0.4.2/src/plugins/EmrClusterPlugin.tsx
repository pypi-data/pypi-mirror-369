import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { INotebookModel, INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { IDisposable } from '@lumino/disposable';
import { createEmrClusterWidget } from '../EmrClusterWidget';
import { COMMANDS } from '../utils/CommandUtils';
import { i18nStrings } from '../constants/i18n';
import { isDefined } from '../utils/TypeGuards';
import {
  getFirstVisibleNotebookPanel,
  insertNotebookCellAndExecute,
  updateConnectionStatus,
} from '../utils/NotebookUtils';
import { SparkWidgetPresignedURLInjector } from '../SparkWidgetPresignedURLInjector';

export const EMR_CONNECT_CLI_COMMAND = '%sm_analytics emr connect';
export const EMR_SERVERLESS_CONNECT_CLI_COMMAND = '%sm_analytics emr-serverless connect';
export const EMR_VERIFY_CERTIFICATE_FLASE = '--verify-certificate False';
const TOOLBAR_KERNEL_SWITCHER_ITEM_NAME = 'kernelName';
const PLUGIN_ID = '@sagemaker-studio:EmrCluster';
const emrClusterPluginStrings = i18nStrings.Clusters;

const EmrClusterPlugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  optional: [INotebookTracker as any],
  activate: async (app: JupyterFrontEnd, notebookTracker: INotebookTracker) => {
    // Presigned URL injector setup
    if (notebookTracker == null) {
      //TODO: Add logging
      //  logger.error({
      //   schema: ClientSchemas.ClientError,
      //   message: ClientErrorMessage.EmrMissingNotebookTrackerError,
      // });
    } else {
      const presignedURLInjector = new SparkWidgetPresignedURLInjector(notebookTracker);
      presignedURLInjector.run();
    }

    app.docRegistry.addWidgetExtension('Notebook', new EmrClusterExtension(app));

    app.commands.addCommand(COMMANDS.emrConnect.id, {
      label: (args) => emrClusterPluginStrings.connectCommand.label,
      isEnabled: () => true,
      isVisible: () => true,
      caption: () => emrClusterPluginStrings.connectCommand.caption,
      execute: async (args) => {
        try {
          const { clusterId, authType, language, crossAccountArn, executionRoleArn, notebookPanelToInjectCommandInto } =
            args;
          const loadExtension = '%load_ext sagemaker_studio_analytics_extension.magics';
          const languageParam = isDefined(language) ? `--language ${language}` : '';
          const crossAccountParam = isDefined(crossAccountArn) ? `--assumable-role-arn ${crossAccountArn}` : '';
          const executionRoleParam = isDefined(executionRoleArn) ? `--emr-execution-role-arn ${executionRoleArn}` : '';
          const connectCommand = `${loadExtension}\n${EMR_CONNECT_CLI_COMMAND} ${EMR_VERIFY_CERTIFICATE_FLASE} --cluster-id ${clusterId} --auth-type ${authType} ${languageParam} ${crossAccountParam} ${executionRoleParam}`;
          const notebookPanel = notebookPanelToInjectCommandInto
            ? notebookPanelToInjectCommandInto
            : getFirstVisibleNotebookPanel(app);

          await insertNotebookCellAndExecute(connectCommand, notebookPanel);
        } catch (exception: any) {
          if (exception.message !== undefined) {
            // TODO: Add logging for sure and Telmetry if needed
            throw exception;
          } else {
            throw exception;
          }
        }
      },
    });

    app.commands.addCommand(COMMANDS.emrServerlessConnect.id, {
      label: (args) => emrClusterPluginStrings.connectCommand.label,
      isEnabled: () => true,
      isVisible: () => true,
      caption: () => emrClusterPluginStrings.connectCommand.caption,
      execute: async (args) => {
        try {
          const {
            serverlessApplicationId,
            language,
            assumableRoleArn,
            executionRoleArn,
            notebookPanelToInjectCommandInto,
          } = args;
          const loadExtension = '%load_ext sagemaker_studio_analytics_extension.magics';
          const languageParam = isDefined(language) ? ` --language ${language}` : '';
          const assumableRoleParam = isDefined(assumableRoleArn) ? ` --assumable-role-arn ${assumableRoleArn}` : '';
          const executionRoleParam = isDefined(executionRoleArn) ? ` --emr-execution-role-arn ${executionRoleArn}` : '';
          const connectCommand = `${loadExtension}\n${EMR_SERVERLESS_CONNECT_CLI_COMMAND} --application-id ${serverlessApplicationId}${languageParam}${assumableRoleParam}${executionRoleParam}`;
          const notebookPanel = notebookPanelToInjectCommandInto
            ? notebookPanelToInjectCommandInto
            : getFirstVisibleNotebookPanel(app);

          await insertNotebookCellAndExecute(connectCommand, notebookPanel);
        } catch (exception: any) {
          if (exception.message !== undefined) {
            // TODO: Add logging for sure and Telmetry if needed
            throw exception;
          } else {
            throw exception;
          }
        }
      },
    });
  },
};

class EmrClusterExtension implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {
  appContext: JupyterFrontEnd<JupyterFrontEnd.IShell, 'desktop' | 'mobile'>;
  /**
   * @param widget - the notebook panel.
   * @param _context - the context of notebook model.
   */
  constructor(app: JupyterFrontEnd) {
    this.appContext = app;
  }

  createNew(widget: NotebookPanel, _context: DocumentRegistry.IContext<INotebookModel>): IDisposable {
    const emrClusterWidget = createEmrClusterWidget(widget.sessionContext, this.appContext);
    widget.context.sessionContext.kernelChanged.connect((sessionContext) => {
      const kernelConnection = sessionContext.session?.kernel;
      sessionContext.iopubMessage.connect((session, message) => {
        updateConnectionStatus(
          message,
          widget,
          emrClusterWidget.selectedCluster,
          emrClusterWidget.updateConnectedCluster,
        );
      });
      if (kernelConnection) {
        kernelConnection.spec.then((specs) => {
          if (specs && specs.metadata) {
            emrClusterWidget.updateKernel(kernelConnection.id);
          }
        });
      }
      emrClusterWidget.updateKernel(null);
    });
    widget.toolbar.insertBefore(TOOLBAR_KERNEL_SWITCHER_ITEM_NAME, 'emrCluster', emrClusterWidget);
    return emrClusterWidget;
  }
}

export { EmrClusterPlugin };
