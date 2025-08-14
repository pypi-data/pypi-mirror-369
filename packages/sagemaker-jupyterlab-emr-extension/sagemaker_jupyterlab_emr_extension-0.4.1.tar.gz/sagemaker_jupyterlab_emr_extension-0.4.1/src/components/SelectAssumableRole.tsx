import React, { useState } from 'react';
import { cx } from '@emotion/css';
import { EmrClusterPluginClassNames } from '../constants/common';
import { Footer } from './Footer';
import { ClusterRowType, EmrConnectRoleDataType, ServerlessApplicationRowType } from '../constants/types';
import styles from './styles';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { Arn } from '../utils/ArnUtils';
import { i18nStrings } from '../constants';
import {
  handleSpecialClusterConnect,
  openSelectAuthType,
  openSelectRuntimeExecRole,
} from '../utils/ConnectClusterUtils';
import { recordEventDetail } from '../utils/CommonUtils';
import { HTMLSelect } from '@jupyterlab/ui-components';
import { isLdapCluster } from '../utils/AuthTypeUtil';

interface SelectAssumableRoleProps extends React.HTMLAttributes<HTMLElement> {
  readonly onCloseModal: () => void;
  readonly emrConnectRoleData: EmrConnectRoleDataType;
  readonly app: JupyterFrontEnd;
  readonly selectedCluster?: ClusterRowType;
  readonly selectedServerlessApplication?: ServerlessApplicationRowType;
}

const SelectAssumableRole: React.FC<SelectAssumableRoleProps> = ({
  onCloseModal,
  selectedCluster,
  selectedServerlessApplication,
  emrConnectRoleData,
  app,
}) => {
  const containerClasses = `${EmrClusterPluginClassNames.SelectEMRAccessRoleContainer}`;

  const onConnect = () => {
    onCloseModal();
    if (selectedCluster) {
      // if Kerberos or LDAP cluster, no need to select auth type
      if (isLdapCluster(selectedCluster)) {
        handleSpecialClusterConnect(app, selectedCluster, selectedAssumableRoleArn);
        return;
      }

      openSelectAuthType(selectedCluster, emrConnectRoleData, app, selectedAssumableRoleArn);
      recordEventDetail('EMR-Select-Assumable-Role', 'JupyterLab');
    } else if (selectedServerlessApplication) {
      openSelectRuntimeExecRole(
        emrConnectRoleData,
        app,
        selectedAssumableRoleArn,
        undefined,
        selectedServerlessApplication,
      );
    }
  };

  const getFilteredEmrAssumableRoleData = (): string[] => {
    if (selectedCluster) {
      return emrConnectRoleData.EmrAssumableRoleArns.filter(
        (roleArn) => Arn.fromArnString(roleArn).accountId === selectedCluster.clusterAccountId,
      );
    } else if (selectedServerlessApplication) {
      return emrConnectRoleData.EmrAssumableRoleArns.filter(
        (roleArn) =>
          Arn.fromArnString(roleArn).accountId === Arn.fromArnString(selectedServerlessApplication.arn).accountId,
      );
    } else {
      return [];
    }
  };

  const filteredRoleArns = getFilteredEmrAssumableRoleData();
  const initialSelection = filteredRoleArns.length ? filteredRoleArns[0] : undefined;
  const [selectedAssumableRoleArn, setSelectedAssumableRoleArn] = useState<string | undefined>(initialSelection);

  const selectAssumableRoleBody: JSX.Element = filteredRoleArns.length ? (
    <HTMLSelect
      title={i18nStrings.RoleSelectionModal.assumableRoleTooltip}
      options={filteredRoleArns}
      value={selectedAssumableRoleArn}
      onChange={(e) => {
        setSelectedAssumableRoleArn(e.target.value);
      }}
      data-testid="select-assumable-role"
    />
  ) : (
    <span className="error-msg">{i18nStrings.Clusters.selectRoleErrorMessage.noEmrAssumableRole}</span>
  );

  return (
    <div className={cx(containerClasses, styles.ModalBase, styles.AuthModal)}>
      <div className={cx(containerClasses, styles.ModalBody, styles.SelectRole)}>{selectAssumableRoleBody}</div>
      <Footer onCloseModal={onCloseModal} onConnect={onConnect} disabled={selectedAssumableRoleArn === undefined} />
    </div>
  );
};

export { SelectAssumableRole, SelectAssumableRoleProps };
