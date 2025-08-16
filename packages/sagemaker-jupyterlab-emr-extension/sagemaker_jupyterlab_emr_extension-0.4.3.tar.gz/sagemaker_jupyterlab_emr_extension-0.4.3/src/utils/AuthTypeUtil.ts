import { ClusterRowType, ClusterConfiguration } from '../constants/types';

const isKerberosCluster = (cluster: ClusterRowType): boolean => Boolean(cluster.kerberosAttributes?.kdcAdminPassword);

const isLdapCluster = (cluster: ClusterRowType): boolean =>
  Boolean(
    cluster.configurations?.some((c: ClusterConfiguration | undefined) => c?.properties?.livyServerAuthType === 'ldap'),
  );

const isTIPEnabledCluster = (cluster: ClusterRowType): boolean => {
  return Boolean(cluster.securityConfiguration?.authentication === 'IdentityCenter');
};

export { isKerberosCluster, isLdapCluster, isTIPEnabledCluster };
