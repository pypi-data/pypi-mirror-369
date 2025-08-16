import React, { Suspense } from 'react';
import { Dialog } from '@jupyterlab/apputils';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { ListClusterView } from './components/ListClusterView';
import { ShowNotificationHandlerType } from './constants/types';
import { Tabs, Tab } from '@mui/material';
import { ListServerlessApplicationsView } from './components/ListServerlessApplicationsView';
import { ClusterTab } from './styles';
import { cx } from '@emotion/css';
import { i18nStrings } from './constants';

interface ListClusterProps extends React.HTMLAttributes<HTMLElement> {
  readonly onCloseModal: () => void;
  readonly header: JSX.Element;
  readonly app: JupyterFrontEnd;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

export function ClusterTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <div>{children}</div>}
    </div>
  );
}

export function ClusterTabs(props: ListClusterProps) {
  const [value, setValue] = React.useState(0);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <div>
      <div>
        <Tabs value={value} onChange={handleChange}>
          <Tab className={cx(ClusterTab)} label={i18nStrings.EmrServerlessApplications.tabName} />
          <Tab className={cx(ClusterTab)} label={i18nStrings.Clusters.tabName} />
        </Tabs>
      </div>
      <ClusterTabPanel value={value} index={0}>
        <ListServerlessApplicationsView onCloseModal={props.onCloseModal} header={props.header} app={props.app} />
      </ClusterTabPanel>
      <ClusterTabPanel value={value} index={1}>
        <ListClusterView onCloseModal={props.onCloseModal} header={props.header} app={props.app} />
      </ClusterTabPanel>
    </div>
  );
}

// @ts-ignore
class ListClusterWidget implements Dialog.IBodyWidget {
  readonly disposeDialog: any;
  readonly header: JSX.Element;
  readonly app: JupyterFrontEnd;

  constructor(disposeDialog: ShowNotificationHandlerType, header: JSX.Element, app: JupyterFrontEnd) {
    this.disposeDialog = disposeDialog;
    this.header = header;
    this.app = app;
  }

  render() {
    return (
      <Suspense fallback={null}>
        <ClusterTabs onCloseModal={this.disposeDialog} app={this.app} header={this.header}></ClusterTabs>
      </Suspense>
    );
  }
}

const createListClusterWidget = (disposeDialog: () => void, header: JSX.Element, app: JupyterFrontEnd) =>
  new ListClusterWidget(disposeDialog, header, app);

export { createListClusterWidget };
