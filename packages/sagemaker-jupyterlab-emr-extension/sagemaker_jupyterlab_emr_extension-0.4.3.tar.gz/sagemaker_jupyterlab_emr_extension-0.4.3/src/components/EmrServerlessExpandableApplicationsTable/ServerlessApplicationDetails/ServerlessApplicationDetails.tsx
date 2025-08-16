import React from 'react';
import { i18nStrings } from '../../../constants/i18n';
import { ServerlessApplication } from '../../../constants/types';

import * as styles from '../../EmrExpandableClustersTable/ClusterDetails/styles';
import * as emrsStyles from './styles';
import {
  displayArchitecture,
  displayMaximumCapacityCpu,
  displayMaximumCapacityDisk,
  displayMaximumCapacityMemory,
  displayReleaseLabel,
  displayWhetherLivyEndpointEnabled,
} from '../../../utils/ServerlessApplicationDetailsUtils';
import { ServerlessApplicationTags } from './ServerlessApplicationTags';

interface Props {
  applicationData: ServerlessApplication | undefined;
}

const expandServerlessApplicationStrings = i18nStrings.EmrServerlessApplications.expandApplication;

const ServerlessApplicationDetails: React.FunctionComponent<Props> = ({ applicationData }) => {
  return (
    applicationData && (
      <>
        <div className={emrsStyles.InformationContainer}>
          <h4>{expandServerlessApplicationStrings.Overview}</h4>
          <div className={styles.Info}>{displayArchitecture(applicationData)}</div>
          <div className={styles.Info}>{displayReleaseLabel(applicationData)}</div>
          <div className={styles.Info}>{displayWhetherLivyEndpointEnabled(applicationData)}</div>
        </div>
        <div className={emrsStyles.InformationContainer}>
          <h4>{expandServerlessApplicationStrings.MaximumCapacity}</h4>
          <div className={styles.Info}>{displayMaximumCapacityCpu(applicationData)}</div>
          <div className={styles.Info}>{displayMaximumCapacityMemory(applicationData)}</div>
          <div className={styles.Info}>{displayMaximumCapacityDisk(applicationData)}</div>
        </div>
        <div className={emrsStyles.InformationContainer}>
          <h4>{expandServerlessApplicationStrings.Tags}</h4>
          <ServerlessApplicationTags applicationData={applicationData} />
        </div>
      </>
    )
  );
};

export { ServerlessApplicationDetails, Props };
