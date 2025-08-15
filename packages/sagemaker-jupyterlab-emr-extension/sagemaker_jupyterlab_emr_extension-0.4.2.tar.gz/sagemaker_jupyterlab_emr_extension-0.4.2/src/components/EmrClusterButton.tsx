import React from 'react';
import { ToolbarButtonComponent } from '@jupyterlab/apputils';
import { EmrClusterPluginClassNames } from '../constants/common';
import { i18nStrings } from '../constants/i18n';

type EmrClusterProps = {
  readonly handleClick: () => void;
  readonly tooltip: string;
};

const EmrClusterButton: React.FC<EmrClusterProps> = ({ handleClick, tooltip }) => {
  return (
    <div className={EmrClusterPluginClassNames.EmrClusterContainer}>
      <ToolbarButtonComponent
        className={EmrClusterPluginClassNames.EmrClusterButton}
        tooltip={tooltip}
        label={i18nStrings.Clusters.clusterButtonLabel}
        onClick={handleClick}
        enabled={true}
      />
    </div>
  );
};

export { EmrClusterProps, EmrClusterButton };
