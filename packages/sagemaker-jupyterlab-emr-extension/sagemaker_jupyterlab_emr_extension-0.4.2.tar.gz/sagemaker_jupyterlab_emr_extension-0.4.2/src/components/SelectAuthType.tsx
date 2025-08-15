import React, { useState, ChangeEvent } from 'react';
import { cx } from '@emotion/css';
import { FormControl, FormControlLabel, Radio, RadioGroup } from '@mui/material';
import { EmrClusterPluginClassNames } from '../constants/common';
import { Footer } from './Footer';
import { ClusterRowType, AuthType, EmrConnectRoleDataType } from '../constants/types';
import styles from './styles';
import { i18nStrings } from '../constants/i18n';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { COMMANDS } from '../utils/CommandUtils';
import { recordEventDetail } from '../utils/CommonUtils';
import { openSelectRuntimeExecRole } from '../utils/ConnectClusterUtils';

interface SelectAuthTypeProps extends React.HTMLAttributes<HTMLElement> {
  readonly onCloseModal: () => void;
  readonly selectedCluster: ClusterRowType;
  readonly emrConnectRoleData: EmrConnectRoleDataType;
  readonly app: JupyterFrontEnd;
  readonly selectedAssumableRoleArn?: string;
}

const SelectAuthType: React.FC<SelectAuthTypeProps> = ({
  onCloseModal,
  selectedCluster,
  emrConnectRoleData,
  app,
  selectedAssumableRoleArn,
}) => {
  const containerClasses = `${EmrClusterPluginClassNames.SelectAuthContainer}`;
  const modalBodyContainer = `${EmrClusterPluginClassNames.SelectAuthContainer}`;

  const [authType, setAuthType] = useState<string>(AuthType.Basic_Access);

  const onConnect = () => {
    if (authType === AuthType.RBAC) {
      onCloseModal();
      openSelectRuntimeExecRole(emrConnectRoleData, app, selectedAssumableRoleArn, selectedCluster);
    } else {
      onCloseModal();
      const params = {
        clusterId: selectedCluster.id,
        authType: authType,
        language: 'python', // This option is hardcoded by default
      };

      if (selectedAssumableRoleArn) {
        Object.assign(params, { crossAccountArn: selectedAssumableRoleArn });
      }
      app.commands.execute(COMMANDS.emrConnect.id, params);

      recordEventDetail('EMR-Connect-Non-RBAC', 'JupyterLab');
    }
  };

  return (
    <div className={cx(containerClasses, styles.ModalBase, styles.AuthModal)}>
      <div className={cx(modalBodyContainer, styles.ModalBody)}>
        <FormControl>
          <RadioGroup
            aria-labelledby="demo-radio-buttons-group-label"
            defaultValue={AuthType.Basic_Access}
            value={authType}
            onChange={(e: ChangeEvent<HTMLInputElement>) => {
              setAuthType(e.target.value);
            }}
            name="radio-buttons-group"
            data-testid="radio-button-group"
            row
          >
            <FormControlLabel
              data-analytics-type="eventDetail"
              data-analytics="EMR-Modal-SelectAuth-BasicAccess-Click"
              value={AuthType.Basic_Access}
              control={<Radio />}
              label={i18nStrings.Clusters.radioButtonLabels.basicAccess}
            />
            <FormControlLabel
              data-analytics-type="eventDetail"
              data-analytics="EMR-Modal-SelectAuth-RBAC-Click"
              value={AuthType.RBAC}
              control={<Radio />}
              label={i18nStrings.Clusters.radioButtonLabels.RBAC}
            />
            <FormControlLabel
              data-analytics-type="eventDetail"
              data-analytics="EMR-Modal-SelectAuth-Kerberos-Click"
              value={AuthType.Kerberos}
              control={<Radio />}
              label={i18nStrings.Clusters.radioButtonLabels.kerberos}
            />
            <FormControlLabel
              data-analytics-type="eventDetail"
              data-analytics="EMR-Modal-SelectAuth-None-Click"
              value={AuthType.None}
              control={<Radio />}
              label={i18nStrings.Clusters.radioButtonLabels.noCredential}
            />
          </RadioGroup>
        </FormControl>
      </div>
      <Footer onCloseModal={onCloseModal} onConnect={onConnect} disabled={false} />
    </div>
  );
};

export { SelectAuthTypeProps, SelectAuthType };
