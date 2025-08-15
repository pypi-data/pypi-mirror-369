import React from 'react';
import { Dialog, ISessionContext, ReactWidget } from '@jupyterlab/apputils';
import { cx } from '@emotion/css';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { EmrClusterButton } from './components/EmrClusterButton';
import { handleKeyboardEvent } from './utils/KeyboardEventHandler';
import { ModalHeader } from './components/Modal/ModalHeader';
import { createListClusterWidget } from './ListClusterWidget';
import { i18nStrings } from './constants/i18n';
import { ClusterRowType } from './constants/types';
import { ListClusterHeader } from './components/ListClusterHeader';
import styles from './components/Modal/styles';

export class EmrClusterWidget extends ReactWidget {
  private _selectedCluster: ClusterRowType | null;
  private _appContext: JupyterFrontEnd<JupyterFrontEnd.IShell, 'desktop' | 'mobile'>;
  private _connectedCluster: ClusterRowType | null;
  private _kernelId: string | null;

  constructor(clientSession: ISessionContext, appContext: JupyterFrontEnd) {
    super();
    this._selectedCluster = null;
    this._appContext = appContext;
    this._connectedCluster = null;
    this._kernelId = null;
  }

  get kernelId(): string | null {
    return this._kernelId;
  }

  get selectedCluster(): ClusterRowType | null {
    return this._selectedCluster;
  }

  updateConnectedCluster = (cluster: ClusterRowType) => {
    this._connectedCluster = cluster;
    this.update();
  };

  getToolTip = () => {
    const tooltip = this._connectedCluster
      ? `${i18nStrings.Clusters.widgetConnected} ${this._connectedCluster.name} cluster`
      : i18nStrings.Clusters.defaultTooltip;
    return tooltip;
  };

  clickHandler = async () => {
    // TODO: update type here to Dialog. Had issues with one of typescript rule. Will look into this later.
    let dialog: any = {};
    const disposeDialog = () => dialog && dialog.resolve();

    dialog = new Dialog({
      title: (
        <ModalHeader
          heading={i18nStrings.Clusters.widgetTitle}
          shouldDisplayCloseButton={true}
          onClickCloseButton={disposeDialog}
          className="list-cluster-modal-header"
        />
      ),
      body: createListClusterWidget(disposeDialog, this.listClusterHeader(), this._appContext).render(),
    });

    dialog.handleEvent = (event: Event) => {
      if (event.type === 'keydown') {
        handleKeyboardEvent({
          keyboardEvent: event as KeyboardEvent,
          onEscape: () => dialog.reject(),
        });
      }
    };

    dialog.addClass(cx(styles.ModalBase, styles.Footer, styles.DialogClassname));
    dialog.launch();
  };

  updateKernel(kernelId: string | null) {
    if (this._kernelId === kernelId) return;
    this._kernelId = kernelId;
    if (this.kernelId) {
      this.update();
    }
  }

  listClusterHeader = () => {
    return <ListClusterHeader clusterName={this._connectedCluster?.name} />;
  };

  render() {
    return <EmrClusterButton handleClick={this.clickHandler} tooltip={this.getToolTip()} />;
  }
}

const createEmrClusterWidget = (clientSession: ISessionContext, appContext: JupyterFrontEnd) =>
  new EmrClusterWidget(clientSession, appContext);

export { createEmrClusterWidget };
