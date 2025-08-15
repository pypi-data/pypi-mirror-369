import React from 'react';
import { cx } from '@emotion/css';
import { i18nStrings } from './constants/i18n';
import { Link, LinkType } from './components/Link/Link';
import styles from './components/styles';
import { INVALID_STATE_ERROR, MISSING_CLUSTER_ID_ERROR, UNSUPPORTED_CLUSTER_ERROR } from './components/EmrPresignedURL';

const emrSSHTunnelHelpLinkUrl = 'https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-ssh-tunnel.html';

const SSHTunnelLink = (sshTunnelLink: string | null): React.ReactNode => {
  const linkText = i18nStrings.Clusters.presignedURL.sshTunnelLink;
  return sshTunnelLink ? (
    <Link href={sshTunnelLink} type={LinkType.External} hideExternalIcon={true}>
      {linkText}
    </Link>
  ) : (
    <span className={cx('PresignedURLErrorText', styles.PresignedURLErrorText)}>{linkText}</span>
  );
};

const GuideLink = (): React.ReactNode => {
  return (
    <Link href={emrSSHTunnelHelpLinkUrl} type={LinkType.External}>
      {i18nStrings.Clusters.presignedURL.viewTheGuide}
    </Link>
  );
};

const GenericError = (sshTunnelLink: string | null): React.ReactNode => {
  return (
    <span>
      <span className={cx('PresignedURLErrorText', styles.PresignedURLErrorText)}>
        <b>{i18nStrings.Clusters.presignedURL.error}</b>
        {i18nStrings.Clusters.presignedURL.sparkUIError}
      </span>
      {SSHTunnelLink(sshTunnelLink)}
      <span className={cx('PresignedURLErrorText', styles.PresignedURLErrorText)}>
        {i18nStrings.Clusters.presignedURL.or}
      </span>
      {GuideLink()}
    </span>
  );
};

const InvalidStateError = (): React.ReactNode => {
  return (
    <span className={cx('PresignedURLErrorText', styles.PresignedURLErrorText)}>
      <b>{i18nStrings.Clusters.presignedURL.error}</b>
      {i18nStrings.Clusters.presignedURL.clusterNotReady}
    </span>
  );
};

const MissingClusterIdError = (): React.ReactNode => {
  return (
    <span className={cx('PresignedURLErrorText', styles.PresignedURLErrorText)}>
      <b>{i18nStrings.Clusters.presignedURL.error}</b>
      {i18nStrings.Clusters.presignedURL.clusterNotConnected}
    </span>
  );
};

const UnsupportedClusterError = (sshTunnelLink: string | null): React.ReactNode => {
  return (
    <span className={cx('PresignedURLErrorText', styles.PresignedURLErrorText)}>
      <b>{i18nStrings.Clusters.presignedURL.error}</b>
      {i18nStrings.Clusters.presignedURL.clusterNotCompatible}
      {SSHTunnelLink(sshTunnelLink)}
      {i18nStrings.Clusters.presignedURL.or}
      {GuideLink()}
    </span>
  );
};

type EmrPresignedURLErrorMessageProps = {
  readonly sshTunnelLink: string | null;
  readonly error: string;
};

const EmrPresignedURLErrorMessage: React.FC<EmrPresignedURLErrorMessageProps> = ({ sshTunnelLink, error }) => {
  const renderError = () => {
    switch (error) {
      case INVALID_STATE_ERROR:
        return InvalidStateError();
      case MISSING_CLUSTER_ID_ERROR:
        return MissingClusterIdError();
      case UNSUPPORTED_CLUSTER_ERROR:
        return UnsupportedClusterError(sshTunnelLink);
      default:
        return GenericError(sshTunnelLink);
    }
  };

  return <React.Fragment>{renderError()}</React.Fragment>;
};

export { EmrPresignedURLErrorMessage, EmrPresignedURLErrorMessageProps };
