import React from 'react';
import ReactDOM from 'react-dom';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { CodeCell } from '@jupyterlab/cells';
import { KernelMessage } from '@jupyterlab/services';
import { EmrPresignedURL } from './components/EmrPresignedURL';
import { EmrPresignedURLErrorMessage } from './EmrPresignedURLErrorMessage';
import { i18nStrings } from './constants/i18n';
import { findCodeCellsWithCommand, findCodeCellsWithRegex } from './utils/NotebookUtils';
import { getColumnIndexOfTableHeader, injectTableRowAfterDataRow, removeAllChildNodes } from './utils/DomUtils';
import { EMR_CONNECT_CLI_COMMAND } from './plugins/EmrClusterPlugin';
import { Arn } from './utils/ArnUtils';
import { arrayHasLength } from './utils/CommonUtils';

const YARN_ID = 'YARN Application ID';
const SPARK_UI = 'Spark UI';
const DRIVER_LOG = 'Driver log';
const EMR_CONNECT_CLUSTER_ID_PARAM = '--cluster-id';
const EMR_CONNECT_ROLE_ARN_PARAM = '--assumable-role-arn';
const WS_CODE_EXECUTE_MSG = 'execute_input';
const INFO_COMMAND = '%info';
const CONFIGURE_COMMAND = '%configure';

const SUBTREE_MUTATION_OPTIONS: MutationObserverInit = {
  childList: true,
  subtree: true,
};

// Content for a web socket message containing code to be executed
type WSCodeExecuteMsgContent = {
  code: string;
  execution_count: number;
  data: string;
};

// Styles to be added with vanilla JS during SparkMagic widget interception
const ErrorRowStyles = {
  textAlign: 'left',
  background: '#212121',
};

// When we upgrade to the latest version of jupyterlab, there is an event that will
// greatly simplify the logic of this class. Note to future selves, we should refactor this.
// https://jupyterlab.readthedocs.io/en/stable/api/classes/notebook.notebookactions-1.html#executionscheduled
class SparkWidgetPresignedURLInjector {
  private trackedPanels: Set<NotebookPanel>;
  private trackedCells: Set<CodeCell>;
  private notebookTracker: INotebookTracker;
  private triggers: string[];
  private kernelChanged: boolean;
  private lastConnectedClusterId: string | null;
  private lastConnectedAccountId: string | undefined;

  /**
   * Construct a new instance of the SparkWidgetPresignedURLInjector.
   * Be sure to call run() to begin monitoring for valid SparkWidgets to inject into.
   */
  constructor(notebookTracker: INotebookTracker) {
    this.trackedPanels = new Set<NotebookPanel>();
    this.trackedCells = new Set<CodeCell>();
    this.notebookTracker = notebookTracker;
    this.triggers = [EMR_CONNECT_CLI_COMMAND, INFO_COMMAND, CONFIGURE_COMMAND];
    this.kernelChanged = false;
    this.lastConnectedClusterId = null;
    this.lastConnectedAccountId = undefined;
  }

  /**
   * Run the injector. If a notebook panel is compatible, it will handle injection of a presigned URL
   * into any available SparkWidget outputs. It will watch for and handle any existing notebooks or newly created notebooks.
   */
  public run() {
    // Setup callback for the currentChanged signal
    // Everytime we change notebooks (open new one or change tabs), it will try to setup presigned URL injection
    this.notebookTracker.currentChanged.connect((tracker, panel) => {
      if (!panel) return;
      if (this.isTrackedPanel(panel)) return;
      // Track changes in kernel in case the kernel becomes incompatible
      panel.context.sessionContext.kernelChanged.connect((session, args) => {
        this.kernelChanged = true;
      });
      // Watch IOPub to respond to code execution
      panel.context.sessionContext.iopubMessage.connect((session, message) => {
        if (!this.isTrackedPanel(panel) || this.kernelChanged) {
          if (message) {
            this.trackPanel(panel);
            this.handleExistingSparkWidgetsOnPanelLoad(panel);
          } else {
            this.stopTrackingPanel(panel);
          }
          this.kernelChanged = false;
        } else if (this.isTrackedPanel(panel)) {
          this.checkMessageForEmrConnectAndInject(message, panel);
        }
      });
    });
  }

  private isTrackedCell(cell: CodeCell): boolean {
    return this.trackedCells.has(cell);
  }

  private trackCell(cell: CodeCell): void {
    this.trackedCells.add(cell);
  }

  private stopTrackingCell(cell: CodeCell): void {
    this.trackedCells.delete(cell);
  }

  private isTrackedPanel(panel: NotebookPanel): boolean {
    return this.trackedPanels.has(panel);
  }

  private trackPanel(panel: NotebookPanel): void {
    this.trackedPanels.add(panel);
  }

  private stopTrackingPanel(panel: NotebookPanel): void {
    this.trackedPanels.delete(panel);
  }

  private handleExistingSparkWidgetsOnPanelLoad(panel: NotebookPanel) {
    panel.revealed.then(() => {
      const triggerRegex = new RegExp(this.triggers.join('|'));
      const emrConnectCells = findCodeCellsWithRegex(panel, triggerRegex);

      emrConnectCells.forEach((cell) => {
        if (this.containsSparkMagicTable(cell.outputArea.node)) {
          // Table exists, directly inject
          const cellModel = cell.model.sharedModel as any;
          const clusterId = this.getClusterId(cellModel.source);
          const accountId = this.getAccountId(cellModel.source);
          this.injectPresignedURL(cell, clusterId, accountId);
        } else {
          // Table is loading, watch it and inject when it renders
          this.injectPresignedURLOnTableRender(cell);
        }
      });
    });
  }

  private checkMessageForEmrConnectAndInject(
    message: KernelMessage.IMessage<KernelMessage.MessageType>,
    panel: NotebookPanel,
  ) {
    if (!(message.header.msg_type === WS_CODE_EXECUTE_MSG)) return;
    const executedCode = (message.content as WSCodeExecuteMsgContent).code;

    if (this.codeContainsTrigger(executedCode)) {
      const emrConnectCells = findCodeCellsWithCommand(panel, executedCode);
      emrConnectCells.forEach((cell) => {
        this.injectPresignedURLOnTableRender(cell);
      });
    }
  }

  private codeContainsTrigger(code: string): boolean {
    const triggerArray = this.triggers.filter((trigger) => {
      return code.includes(trigger);
    });

    return arrayHasLength(triggerArray);
  }

  private getParameterFromEmrConnectCommand(command: string, param: string): string | undefined {
    const split = command.split(' ');
    const paramIndex = split.indexOf(param);
    // Make sure we found the right index and are in bounds
    if (paramIndex === -1 || paramIndex + 1 > split.length - 1) return undefined;
    return split[paramIndex + 1];
  }

  private getClusterId(command: string | null): string | null {
    // Check for cluster id - if not found, make sure to return null instead of undefined
    // if we're missing cluster ID we want to fail,
    // so use null as a marker
    //
    // Also, if the command doesn't include --cluster-id it must be the %%info command, in which case
    // the correct behaviour is to return the last used cluster id or null if we haven't connected yet
    if (command && command.includes(EMR_CONNECT_CLUSTER_ID_PARAM)) {
      return this.getParameterFromEmrConnectCommand(command, EMR_CONNECT_CLUSTER_ID_PARAM) || null;
    } else {
      return this.lastConnectedClusterId;
    }
  }

  private getAccountId(command: string | null): string | undefined {
    if (!command) return this.lastConnectedAccountId;
    if (command.includes(INFO_COMMAND)) {
      // %info use last successfully connected account ID (or undefined it was single account)
      return this.lastConnectedAccountId;
    }
    if (command.includes(EMR_CONNECT_ROLE_ARN_PARAM)) {
      // making cross account connection, return the cross account ID
      const roleArn = this.getParameterFromEmrConnectCommand(command, EMR_CONNECT_ROLE_ARN_PARAM);
      const accountId = roleArn !== undefined ? Arn.fromArnString(roleArn).accountId : undefined;
      return accountId;
    }
    // making regular single account connection - no account ID, return undefined
    return undefined;
  }

  private getSparkMagicTableBodyNodes(node: HTMLElement): HTMLElement[] {
    const tableBodyTags = Array.from(node.getElementsByTagName('tbody'));
    if (!arrayHasLength(tableBodyTags)) return [];
    return tableBodyTags.filter((tableBody) => this.containsSparkMagicTable(tableBody));
  }

  private containsSparkMagicTable(node: HTMLElement) {
    return node.textContent?.includes(YARN_ID) && node.textContent.includes(SPARK_UI);
  }

  private isSparkUIErrorRow(row: Node | null): boolean {
    if (!(row instanceof HTMLTableRowElement)) return false;
    return row.textContent?.includes(i18nStrings.Clusters.presignedURL.error) || false;
  }

  private injectSparkUIErrorIntoNextTableRow(
    tableBody: HTMLTableSectionElement,
    dataRow: HTMLTableRowElement,
    sshTunnelLink: string | null,
    presignedURLError: string | null,
  ): void {
    // If error is null, clear any errors in the next row and return
    const nextRowIsError = this.isSparkUIErrorRow(dataRow.nextSibling);
    if (presignedURLError === null) {
      if (nextRowIsError) {
        dataRow.nextSibling?.remove();
      }
      return;
    }
    // If we've already injected an error as the next row, we'll overwrite it, otherwise make a new row
    let row: HTMLTableRowElement | null;
    if (nextRowIsError) {
      row = dataRow.nextSibling as HTMLTableRowElement;
      removeAllChildNodes(row);
    } else row = injectTableRowAfterDataRow(tableBody, dataRow);
    // Silently fail, EmrPresignedURL component will show its own error
    if (!row) return;

    // Setup cell to hold React component for error message
    const errorCell = row.insertCell();
    const tableWidth = dataRow.childElementCount;
    errorCell.setAttribute('colspan', tableWidth.toString());
    errorCell.style.textAlign = ErrorRowStyles.textAlign;
    errorCell.style.background = ErrorRowStyles.background;

    const errorMessage = <EmrPresignedURLErrorMessage sshTunnelLink={sshTunnelLink} error={presignedURLError} />;

    ReactDOM.render(errorMessage, errorCell);
  }

  private injectPresignedURL(cell: CodeCell, clusterId: string | null, accountId: string | undefined): boolean {
    // Find the table(s), or try again later if they're still loading
    const node = cell.outputArea.node;
    const cellModel = cell.model.sharedModel as any;
    const tableBodyTags = this.getSparkMagicTableBodyNodes(node);
    if (!arrayHasLength(tableBodyTags)) {
      return false;
    }
    if (cellModel.source.includes(CONFIGURE_COMMAND) && tableBodyTags.length < 2) {
      return false;
    }

    for (let i = 0; i < tableBodyTags.length; i++) {
      const tableBody = tableBodyTags[i] as HTMLTableSectionElement;
      const headerRow = tableBody.firstChild as HTMLTableRowElement;

      // Get index of the columns we need
      const sparkUIIndex = getColumnIndexOfTableHeader(headerRow, SPARK_UI);
      const driverLogIndex = getColumnIndexOfTableHeader(headerRow, DRIVER_LOG);
      const applicationIdIndex = getColumnIndexOfTableHeader(headerRow, YARN_ID);

      // Get the th element you want to remove (in this case, index 1)
      const thToRemove = headerRow.getElementsByTagName('th')[driverLogIndex];

      // Remove the th element from the header row
      headerRow.removeChild(thToRemove);

      if (sparkUIIndex === -1 || applicationIdIndex === -1) {
        // TODO: Add logger
        // this.logger.error({
        //   schema: ClientSchemas.ClientError,
        //   message: ClientErrorMessage.EmrPresignedURLInjectionError,
        //   error: new Error(
        //     'Error injecting presigned URL: SparkMagic rendered an invalid table, this is likely an error in SparkMagic',
        //   ),
        // });
        break;
      }

      // For the remaining rows (data rows), inject presigned URL at the index of Spark UI
      for (let j = 1; j < tableBody.childNodes.length; j++) {
        const dataRow = tableBody.childNodes[j] as HTMLTableRowElement;
        const sparkUILinkCell = dataRow.childNodes[sparkUIIndex] as HTMLElement;
        const driverLogLinkCell = dataRow.childNodes[driverLogIndex] as HTMLElement;

        // Remove driverLogLinkCell
        driverLogLinkCell.remove();
        const sshTunnelLink = sparkUILinkCell.getElementsByTagName('a')[0]?.href;
        if (sparkUILinkCell.hasChildNodes()) {
          removeAllChildNodes(sparkUILinkCell);
        }
        // Create and inject the presigned URL component
        const applicationId = dataRow.childNodes[applicationIdIndex].textContent || undefined;
        const presignedURLContainer = document.createElement('div');
        sparkUILinkCell.appendChild(presignedURLContainer);
        const presignedURLComponent = (
          <EmrPresignedURL
            clusterId={clusterId}
            applicationId={applicationId}
            onError={(error) => this.injectSparkUIErrorIntoNextTableRow(tableBody, dataRow, sshTunnelLink, error)}
            accountId={accountId}
          />
        );
        ReactDOM.render(presignedURLComponent, presignedURLContainer);
      }
    }
    return true;
  }

  private injectPresignedURLOnTableRender(cell: CodeCell): void {
    if (this.isTrackedCell(cell)) return;
    this.trackCell(cell);
    const nodeObserver = new MutationObserver((record, observer) => {
      for (const mutation of record) {
        if (mutation.type === 'childList') {
          try {
            const cellModel = cell.model.sharedModel;
            const clusterId = this.getClusterId(cellModel.source);
            const accountId = this.getAccountId(cellModel.source);
            const isComplete = this.injectPresignedURL(cell, clusterId, accountId);

            if (isComplete) {
              this.stopTrackingCell(cell);
              observer.disconnect();
              this.lastConnectedClusterId = clusterId;
              this.lastConnectedAccountId = accountId;
              break;
            }
          } catch (exception) {
            this.stopTrackingCell(cell);
            observer.disconnect();
            //TODO: Add logger
          }
        }
      }
    });
    nodeObserver.observe(cell.outputArea.node, SUBTREE_MUTATION_OPTIONS);
  }
}

export { SparkWidgetPresignedURLInjector };
