import React from 'react';
import { cx } from '@emotion/css';
import { AuthType, ClusterRowType, EmrConnectRoleDataType, ServerlessApplicationRowType } from '../constants/types';
import styles from '../components/Modal/styles';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { i18nStrings } from '../constants';
import { ModalHeader } from '../components/Modal/ModalHeader';
import { SelectRuntimeExecRole } from '../components/SelectRuntimeExecRole';
import { Dialog } from '@jupyterlab/apputils';
import { SelectAuthType } from '../components/SelectAuthType';
import { SelectAssumableRole } from '../components/SelectAssumableRole';
import { COMMANDS } from './CommandUtils';
import { recordEventDetail } from './CommonUtils';

const openSelectAssumableRole = (
  emrConnectRoleData: EmrConnectRoleDataType,
  app: JupyterFrontEnd,
  selectedCluster?: ClusterRowType,
  selectedServerlessApplication?: ServerlessApplicationRowType,
) => {
  let dialog: any = {};
  const disposeDialog = () => dialog && dialog.resolve();
  dialog = new Dialog({
    title: (
      <ModalHeader
        heading={`${i18nStrings.Clusters.selectAssumableRoleTitle}`}
        shouldDisplayCloseButton={true}
        onClickCloseButton={disposeDialog}
      />
    ),
    body: (
      <SelectAssumableRole
        onCloseModal={disposeDialog}
        selectedCluster={selectedCluster}
        selectedServerlessApplication={selectedServerlessApplication}
        emrConnectRoleData={emrConnectRoleData}
        app={app}
      />
    ),
  });
  dialog.addClass(cx(styles.ModalBase, styles.Footer, styles.DialogClassname));
  dialog.launch();
};

const openSelectAuthType = (
  selectedCluster: ClusterRowType,
  emrConnectRoleData: EmrConnectRoleDataType,
  app: JupyterFrontEnd,
  selectedAssumableRoleArn?: string,
) => {
  let dialog: any = {};
  const disposeDialog = () => dialog && dialog.resolve();
  dialog = new Dialog({
    title: (
      <ModalHeader
        heading={`${i18nStrings.Clusters.selectAuthTitle}"${selectedCluster.name}"`}
        shouldDisplayCloseButton={true}
        onClickCloseButton={disposeDialog}
      />
    ),
    body: (
      <SelectAuthType
        onCloseModal={disposeDialog}
        selectedCluster={selectedCluster}
        emrConnectRoleData={emrConnectRoleData}
        app={app}
        selectedAssumableRoleArn={selectedAssumableRoleArn}
      />
    ),
  });

  dialog.addClass(cx(styles.ModalBase, styles.Footer, styles.DialogClassname));
  dialog.launch();
};

const openSelectRuntimeExecRole = (
  emrConnectRoleData: EmrConnectRoleDataType,
  app: JupyterFrontEnd,
  selectedAssumableRoleArn?: string,
  selectedCluster?: ClusterRowType,
  selectedServerlessApplication?: ServerlessApplicationRowType,
) => {
  let dialog: any = {};
  const disposeDialog = () => dialog && dialog.resolve();
  dialog = new Dialog({
    title: (
      <ModalHeader
        heading={`${i18nStrings.Clusters.selectRuntimeExecRoleTitle}`}
        shouldDisplayCloseButton={true}
        onClickCloseButton={disposeDialog}
      />
    ),
    body: (
      <SelectRuntimeExecRole
        onCloseModal={disposeDialog}
        selectedCluster={selectedCluster}
        selectedServerlessApplication={selectedServerlessApplication}
        emrConnectRoleData={emrConnectRoleData}
        app={app}
        selectedAssumableRoleArn={selectedAssumableRoleArn}
      />
    ),
  });

  dialog.addClass(cx(styles.ModalBase, styles.Footer, styles.DialogClassname));
  dialog.launch();
};

const handleSpecialClusterConnect = (
  app: JupyterFrontEnd,
  cluster: ClusterRowType,
  selectedAssumableRoleArn: string = '',
) => {
  // cluster is LDAP cluster
  const authMode = AuthType.Basic_Access;

  const params = {
    clusterId: cluster.id,
    authType: authMode,
    language: 'python',
  };

  if (selectedAssumableRoleArn) {
    Object.assign(params, { crossAccountArn: selectedAssumableRoleArn });
  }
  app.commands.execute(COMMANDS.emrConnect.id, params);

  recordEventDetail('EMR-Connect-Special-Cluster', 'JupyterLab');
};
export { openSelectAssumableRole, openSelectAuthType, openSelectRuntimeExecRole, handleSpecialClusterConnect };
