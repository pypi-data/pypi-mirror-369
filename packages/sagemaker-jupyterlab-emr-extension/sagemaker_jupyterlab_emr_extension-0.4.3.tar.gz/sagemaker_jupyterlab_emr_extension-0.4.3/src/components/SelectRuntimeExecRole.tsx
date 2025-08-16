import React, { useState } from 'react';
import { cx } from '@emotion/css';
import { EmrClusterPluginClassNames } from '../constants/common';
import { Footer } from './Footer';
import { AuthType, ClusterRowType, EmrConnectRoleDataType, ServerlessApplicationRowType } from '../constants/types';
import styles from './styles';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { COMMANDS } from '../utils/CommandUtils';
import { Arn } from '../utils/ArnUtils';
import { i18nStrings } from '../constants';
import { recordEventDetail } from '../utils/CommonUtils';
import { Link, LinkType } from './Link/Link';
import { HTMLSelect } from '@jupyterlab/ui-components';

// TODO: change it to dynamic link depending on user language
const EMR_RUNTIME_ROLE_PREREQUISITE_URL =
  'https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-steps-runtime-roles.html#emr-steps-runtime-roles-configure';

const EMR_SERVERLESS_RUNTIME_ROLE_PREREQUISITE_URL =
  'https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/getting-started.html#gs-runtime-role';

interface SelectRuntimeExecRoleProps {
  readonly onCloseModal: () => void;
  readonly selectedCluster?: ClusterRowType;
  readonly selectedServerlessApplication?: ServerlessApplicationRowType;
  readonly emrConnectRoleData: EmrConnectRoleDataType;
  readonly app: JupyterFrontEnd;
  readonly selectedAssumableRoleArn?: string;
}

const SelectRuntimeExecRole: React.FC<SelectRuntimeExecRoleProps> = ({
  onCloseModal,
  selectedCluster,
  selectedServerlessApplication,
  emrConnectRoleData,
  app,
  selectedAssumableRoleArn,
}) => {
  const containerClasses = `${EmrClusterPluginClassNames.SelectEMRAccessRoleContainer}`;

  const onConnect = () => {
    onCloseModal();
    if (selectedCluster) {
      const params = {
        clusterId: selectedCluster.id,
        language: 'python', // This option is hardcoded by default
        authType: AuthType.Basic_Access, // should only use basic_access in this case
        executionRoleArn: selectedExecutionRoleArn,
      };

      if (selectedAssumableRoleArn) {
        Object.assign(params, { crossAccountArn: selectedAssumableRoleArn });
      }
      app.commands.execute(COMMANDS.emrConnect.id, params);

      recordEventDetail('EMR-Connect-RBAC', 'JupyterLab');
    } else if (selectedServerlessApplication) {
      const params = {
        serverlessApplicationId: selectedServerlessApplication.id,
        executionRoleArn: selectedExecutionRoleArn,
        language: 'python', // This option is hardcoded by default
        assumableRoleArn: selectedAssumableRoleArn,
      };

      app.commands.execute(COMMANDS.emrServerlessConnect.id, params);
    }
  };

  const getFilteredEmrExecutionRoleData = (): string[] => {
    if (selectedCluster) {
      return emrConnectRoleData.EmrExecutionRoleArns.filter(
        (roleArn) => Arn.fromArnString(roleArn).accountId === selectedCluster.clusterAccountId,
      );
    } else if (selectedServerlessApplication) {
      return emrConnectRoleData.EmrExecutionRoleArns.filter(
        (roleArn) =>
          Arn.fromArnString(roleArn).accountId === Arn.fromArnString(selectedServerlessApplication.arn).accountId,
      );
    } else {
      return [];
    }
  };

  const filteredRoleArns = getFilteredEmrExecutionRoleData();
  const initialSelection = filteredRoleArns.length ? filteredRoleArns[0] : undefined;
  const [selectedExecutionRoleArn, setSelectedExecutionRoleArn] = useState<string | undefined>(initialSelection);

  const selectRuntimeExecRoleBody: JSX.Element = filteredRoleArns.length ? (
    <HTMLSelect
      className={cx(styles.SelectRole)}
      options={filteredRoleArns}
      value={selectedExecutionRoleArn}
      title={i18nStrings.RoleSelectionModal.executionRoleTooltip}
      onChange={(e) => {
        setSelectedExecutionRoleArn(e.target.value);
      }}
      data-testid="select-runtime-exec-role"
    />
  ) : (
    <span className="error-msg">{i18nStrings.Clusters.selectRoleErrorMessage.noEmrExecutionRole}</span>
  );

  const prerequisiteLink = (): string => {
    if (selectedCluster) {
      return EMR_RUNTIME_ROLE_PREREQUISITE_URL;
    } else if (selectedServerlessApplication) {
      return EMR_SERVERLESS_RUNTIME_ROLE_PREREQUISITE_URL;
    }
    return '';
  };

  return (
    <div className={cx(containerClasses, styles.ModalBase, styles.AuthModal)}>
      <div className={cx(containerClasses, styles.ModalBody, styles.SelectRole)}>{selectRuntimeExecRoleBody}</div>
      <div className={cx(containerClasses, styles.ModalBody)}>
        <Link href={prerequisiteLink()} type={LinkType.External}>
          {i18nStrings.Clusters.setUpRuntimeExecRole}
        </Link>
      </div>
      <Footer onCloseModal={onCloseModal} onConnect={onConnect} disabled={selectedExecutionRoleArn === undefined} />
    </div>
  );
};

export { SelectRuntimeExecRole, SelectRuntimeExecRoleProps };
