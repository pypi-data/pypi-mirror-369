import React from 'react';
import { i18nStrings } from '../constants/i18n';
import { Button } from '@jupyterlab/ui-components/lib/components/button';
import styles from './Modal/styles';

export interface FooterPropsType extends React.HTMLAttributes<HTMLElement> {
  readonly onCloseModal: () => void;
  readonly onConnect: () => void;
  readonly disabled: boolean;
}

export const Footer: React.FC<FooterPropsType> = ({ onCloseModal, onConnect, disabled }) => {
  return (
    <footer data-analytics-type="eventContext" data-analytics="JupyterLab" className={styles.ModalFooter}>
      <Button
        data-analytics-type="eventDetail"
        data-analytics="EMR-Modal-Footer-CancelButton"
        className="jp-Dialog-button jp-mod-reject jp-mod-styled listcluster-cancel-btn"
        type="button"
        onClick={onCloseModal}
      >
        {i18nStrings.DefaultModal.CancelButton}
      </Button>
      <Button
        data-analytics-type="eventDetail"
        data-analytics="EMR-Modal-Footer-ConnectButton"
        className="jp-Dialog-button jp-mod-accept jp-mod-styled listcluster-connect-btn"
        type="button"
        onClick={onConnect}
        disabled={disabled}
      >
        {i18nStrings.Clusters.connectButton}
      </Button>
    </footer>
  );
};
