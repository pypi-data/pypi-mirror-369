/* eslint-disable no-console */
import React, { useCallback, useState } from 'react';
import { cx } from '@emotion/css';
import { CircularProgress } from '@mui/material';
import {
  getOnClusterAppUIPresignedURL,
  createPersistentAppUI,
  pollUntilPersistentAppUIReady,
  getPersistentAppUIPresignedURL,
  describeCluster,
} from '../service/presignedURL';
import { Cluster, ClusterState } from '../constants/types';
import { i18nStrings } from '../constants/i18n';
import { Link } from '../components/Link/Link';
import styles from './styles';

export const INVALID_STATE_ERROR = 'Invalid Cluster State';
export const MISSING_CLUSTER_ID_ERROR = 'Missing Cluster ID, are you connected to a cluster?';
export const UNSUPPORTED_CLUSTER_ERROR = 'Unsupported cluster version';

const NEW_TAB = '_blank';
const NEW_TAB_OPTIONS = 'noopener,noreferrer';

// Max wait time for polling describePersistentAppUI, 30 seconds, per SLA from EMR
const MAX_DESCRIBE_POLL_WAIT = 30000;
const DESCRIBE_POLL_INTERVAL_MS = 2000;

type EmrPresignedURLErrorHandler = (error: string | null) => void;

type EmrPresignedURLProps = {
  readonly clusterId: string | null;
  readonly accountId: string | undefined;
  readonly applicationId?: string | undefined;
  readonly persistentAppUIType?: string | undefined;
  readonly label?: string | undefined;
  readonly onError: EmrPresignedURLErrorHandler;
};

const EmrPresignedURL: React.FC<EmrPresignedURLProps> = ({
  clusterId,
  accountId,
  applicationId,
  persistentAppUIType,
  label,
  onError,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const handleError = useCallback(
    (error: string) => {
      setError(true);
      onError(error);
    },
    [onError],
  );

  const openPresignedURLInNewTab = useCallback(
    (url: string | undefined): void => {
      if (url) {
        const res = window.open(url, NEW_TAB, NEW_TAB_OPTIONS);
        if (res !== null) {
          // TODO:: Add telemetry
          setError(false);
          onError(null);
        }
      } else {
        // TODO: Add Logger
        throw new Error('Error opening Spark UI: Invalid URL');
      }
    },
    [onError],
  );

  const getActiveClusterPresignedURL = useCallback(
    (clusterId: string, accountId: string | undefined, applicationId: string | undefined) => {
      getOnClusterAppUIPresignedURL(accountId, clusterId, applicationId)
        .then((res) => openPresignedURLInNewTab(res?.presignedURL))
        .catch((error) => handleError(error))
        .finally(() => setLoading(false));
    },
    [handleError, openPresignedURLInNewTab],
  );

  const getInactiveClusterPresignedURL = useCallback(
    (
      cluster: Cluster,
      accountId: string | undefined,
      applicationId: string | undefined,
      persistentAppUIType?: string | undefined,
    ) => {
      createPersistentAppUI(cluster.clusterArn)
        .then((res) =>
          pollUntilPersistentAppUIReady(
            res?.persistentAppUIId,
            MAX_DESCRIBE_POLL_WAIT,
            DESCRIBE_POLL_INTERVAL_MS,
            res?.roleArn,
          ),
        )
        .then((res) =>
          getPersistentAppUIPresignedURL(res?.persistentAppUI.persistentAppUIId, res?.roleArn, persistentAppUIType),
        )
        .then((res) => openPresignedURLInNewTab(res?.presignedURL))
        .catch((error) => handleError(error))
        .finally(() => setLoading(false));
    },
    [handleError, openPresignedURLInNewTab],
  );

  const handleGetPresignedURL = useCallback(
    (
        accountId: string | undefined,
        clusterId: string | null,
        applicationId: string | undefined,
        persistentAppUIType: string | undefined,
      ) =>
      async () => {
        // TODO:: Add Telemetry
        // Grab info about this cluster to control which flow we'll take
        setLoading(true);
        if (!clusterId) {
          setLoading(false);
          handleError(MISSING_CLUSTER_ID_ERROR);
          return;
        }
        const res = await describeCluster(clusterId, accountId).catch((error) => handleError(error));
        if (!res || !res?.cluster) {
          // Error propagated through handleError, just bail here if we have one
          setLoading(false);
          return;
        }

        const cluster = res?.cluster;

        // If we have release label, check it, otherwise let EMR try to figure things out
        if (cluster.releaseLabel) {
          // Check to make sure this cluster supports presigned
          // As of 11/03/21 EMR supports presigned for emr-5.33+ and emr-6.3.0+
          try {
            // index 4 of the string (should) be the start of the number, after emr-
            // before first '.' should always be major, after first '.' should always be minor, regardless of # digits
            const versionStrings = cluster.releaseLabel.substr(4).split('.');
            const majorVersionNum = +versionStrings[0];
            const minorVersionNum = +versionStrings[1];
            if (majorVersionNum < 5) {
              setLoading(false);
              handleError(UNSUPPORTED_CLUSTER_ERROR);
              return;
            }
            if (majorVersionNum === 5 && minorVersionNum < 33) {
              setLoading(false);
              handleError(UNSUPPORTED_CLUSTER_ERROR);
              return;
            } else if (majorVersionNum === 6 && minorVersionNum < 3) {
              setLoading(false);
              handleError(UNSUPPORTED_CLUSTER_ERROR);
              return;
            }
          } catch (error) {
            // Swallow the error and let emr try to get a presigned URL
            // If this happens, the only effect is the detail of the error message in the UI,
            // but there's a chance EMR will succeed so we don't want to entirely fail here
          }
        }

        // Dispatch the appropriate API calls based on cluster state
        switch (cluster.status.state) {
          case ClusterState.Running: {
            // Active cluster flow
            // Add check to see if we know applicationId or not
            if (applicationId) {
              getActiveClusterPresignedURL(clusterId, accountId, applicationId);
            } else {
              getInactiveClusterPresignedURL(cluster, accountId, applicationId, persistentAppUIType);
            }
            break;
          }
          case ClusterState.Waiting: {
            // Active cluster flow
            // Add check to see if we know applicationId or not
            if (applicationId) {
              getActiveClusterPresignedURL(clusterId, accountId, applicationId);
            } else {
              getInactiveClusterPresignedURL(cluster, accountId, applicationId, persistentAppUIType);
            }
            break;
          }
          case ClusterState.Terminated: {
            // Inactive cluster flow
            getInactiveClusterPresignedURL(cluster, accountId, applicationId, persistentAppUIType);
            break;
          }
          default: {
            // Cluster in transition or invalid state
            setLoading(false);
            handleError(INVALID_STATE_ERROR);
            break;
          }
        }
      },
    [getActiveClusterPresignedURL, getInactiveClusterPresignedURL, handleError],
  );

  return (
    <>
      {loading ? (
        <span>
          <CircularProgress size="1rem" />
        </span>
      ) : (
        <Link
          data-analytics-type="eventDetail"
          data-analytics="EMR-Modal-PresignedUrl-Click"
          className={cx('PresignedURL', styles.PresignedURL)}
          onClick={handleGetPresignedURL(accountId, clusterId, applicationId, persistentAppUIType)}
        >
          {error ? (
            <span>
              {label && label}&nbsp;
              <span
                className={cx('PresignedURLErrorText', styles.PresignedURLErrorText)}
                onClick={handleGetPresignedURL(accountId, clusterId, applicationId, persistentAppUIType)}
              >
                ({i18nStrings.Clusters.presignedURL.retry})
              </span>
            </span>
          ) : label ? (
            label
          ) : (
            i18nStrings.Clusters.presignedURL.link
          )}
        </Link>
      )}
    </>
  );
};

export { EmrPresignedURLProps, EmrPresignedURL };
