import React from 'react';
import _ from 'lodash';
import { i18nStrings } from '../../../constants/i18n';
import { ServerlessApplication } from '../../../constants/types';

import * as styles from '../../EmrExpandableClustersTable/ClusterDetails/styles';

interface Props {
  applicationData: ServerlessApplication | undefined;
}

const expandServerlessApplicationStrings = i18nStrings.EmrServerlessApplications.expandApplication;

const ServerlessApplicationTags: React.FunctionComponent<Props> = ({ applicationData }) => {
  const tags = applicationData?.tags;

  if (!_.isEmpty(tags)) {
    return (
      <>
        {Object.entries(tags).map(([key, value]) => {
          return (
            <div className={styles.Info} key={key}>
              {key}: {value}
            </div>
          );
        })}
      </>
    );
  }

  return <div>{expandServerlessApplicationStrings.NoTags}</div>;
};

export { ServerlessApplicationTags };
