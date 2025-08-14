import { ClusterRowType } from '../constants/types';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { CodeCell } from '@jupyterlab/cells';
import { INotebookModel, Notebook, NotebookActions, NotebookPanel } from '@jupyterlab/notebook';
import { KernelMessage } from '@jupyterlab/services';
import { Widget } from '@lumino/widgets';

const EMR_CONNECT_NAMESPACE = 'sagemaker-analytics';

type InsertCellAndExecuteResult = {
  html: string[];
  cell: CodeCell;
};

//TODO: Adding few types as ant which are not straighforward and would need some types to be imported
const insertNotebookCellAndExecute = async (
  pythonCode: string,
  notebookPanel: any,
  execute = true,
): Promise<InsertCellAndExecuteResult> => {
  /* eslint-disable no-async-promise-executor */
  return new Promise(async (resolve, reject) => {
    if (notebookPanel) {
      const notebook = notebookPanel.content;
      const notebookModel: INotebookModel = notebook.model;

      const sessionContext = notebookPanel.context.sessionContext;
      const { metadata } = notebookModel.sharedModel.toJSON();
      const clones = {
        cell_type: 'code',
        metadata,
        source: pythonCode,
      };

      const cell = notebook.activeCell;
      const newIndex = cell ? notebook.activeCellIndex : 0;
      notebookModel.sharedModel.insertCell(newIndex, clones);
      // Make the newly inserted cell active.
      notebook.activeCellIndex = newIndex;

      // execution code
      if (execute) {
        try {
          await NotebookActions.run(notebook, sessionContext);
        } catch (error) {
          reject(error);
        }
      }

      const htmlArray: string[] = [];
      for (const output of cell.outputArea.node.children) {
        htmlArray.push(output.innerHTML as string);
      }
      resolve({ html: htmlArray, cell: cell as CodeCell });
    }
    reject('No notebook panel');
  });
};

const getFirstVisibleNotebookPanel = (app: JupyterFrontEnd) => {
  const mainWidgets = app.shell.widgets('main');
  let widget: Widget = mainWidgets.next().value as Widget;
  while (widget) {
    const type = widget.hasClass('jp-NotebookPanel');
    if (type) {
      if (widget.isVisible) {
        return widget;
      }
    }
    widget = mainWidgets.next().value as Widget;
  }
  return null;
};

type EmrConnResult = {
  isConnSuccess?: boolean;
  isConnError?: boolean;
  clusterId?: string | undefined;
};

const getEmrConnResult = (message: KernelMessage.IMessage<KernelMessage.MessageType>): EmrConnResult => {
  // Sample content text: "{\"cluster_id\": \"j-BOTRBAGQEQWV\", \"error_message\": null, \"success\": true}\n"
  let isConnSuccess = false;
  let clusterId;

  if ((message.content as any).text) {
    const parsedMessage = JSON.parse((message.content as any).text);
    if (parsedMessage.namespace !== EMR_CONNECT_NAMESPACE) return {};
    clusterId = parsedMessage.cluster_id;
    isConnSuccess = parsedMessage.success;
  }

  return { isConnSuccess, clusterId };
};

const updateConnectionStatus = (
  message: KernelMessage.IMessage<KernelMessage.MessageType>,
  notebookPanel: NotebookPanel,
  selectedCluster: ClusterRowType | null,
  setConnectedCluster: (cluster: ClusterRowType) => void,
) => {
  if (!selectedCluster) return;
  try {
    if ((message.content as any).text) {
      const { isConnSuccess, clusterId } = getEmrConnResult(message);
      if (isConnSuccess && selectedCluster.id === clusterId) {
        setConnectedCluster(selectedCluster);
      }
    }
  } catch (e) {
    // silent failure
    return;
  }
};

const updateCompatibilityStatus = (
  message: KernelMessage.IMessage<KernelMessage.MessageType>,
  notebookPanel: NotebookPanel,
  updateLabelStatus: (isCompatible: boolean) => void,
) => {
  if (message.header.msg_type === 'stream') {
    const payload = (message.content as any).text;
    if (payload) {
      try {
        const parsedMessage = JSON.parse(payload);
        if (parsedMessage?.namespace !== EMR_CONNECT_NAMESPACE) {
          updateLabelStatus(false);
          return;
        }
        const isCompatible = parsedMessage?.emr?.compatible;
        isCompatible !== undefined && updateLabelStatus(isCompatible);
      } catch (e) {
        // silently fail and don't show the feature since kernel selected is not compatible
        return;
      }
    }
  }
};

/**
 * Search a notebook panel for any CodeCell which contains a given code string.
 *
 * @param notebookPanel the notebook
 * @param command the code string to search for
 * @returns a list of CodeCells which contain the code string, or an empty list if none
 */
const findCodeCellsWithCommand = (notebookPanel: NotebookPanel, command: string): CodeCell[] => {
  const notebook = notebookPanel.content as Notebook;
  // Access the list of cells
  const cells = notebook.widgets;
  const cellsMatched = cells.filter((cell: any) => {
    const cellSource = cell.model.sharedModel.source;
    return cellSource.includes(command);
  });
  return cellsMatched as any;
};

/**
 * Search a notebook panel for any CodeCell whose input text matches the given regex.
 *
 * @param notebookPanel the notebook
 * @param regex the pattern to test
 * @returns a list of CodeCells which match the regex, or an empty list if none
 */
const findCodeCellsWithRegex = (notebookPanel: NotebookPanel, regex: RegExp): CodeCell[] => {
  const cells = notebookPanel?.content?.widgets as CodeCell[];
  const cellsMatched = cells?.filter((cell: CodeCell) => {
    const cellModel = cell.model.sharedModel;
    return regex.test(cellModel.source);
  });
  return cellsMatched;
};

export {
  insertNotebookCellAndExecute,
  getFirstVisibleNotebookPanel,
  updateConnectionStatus,
  findCodeCellsWithCommand,
  updateCompatibilityStatus,
  findCodeCellsWithRegex,
};
