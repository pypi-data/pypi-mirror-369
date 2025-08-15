import { isKerberosCluster, isLdapCluster } from '../AuthTypeUtil';
import { ClusterRowType } from '../../constants/types';

type GetMockCluster = {
  kdcAdminPassword?: string;
  type?: string;
};

const getMockCluster = ({ kdcAdminPassword, type }: GetMockCluster) =>
  ({
    kerberosAttributes: {
      kdcAdminPassword,
    },
    configurations: [
      {
        properties: { livyServerAuthType: type },
      },
    ],
  } as unknown as ClusterRowType);

describe('AuthType Util', () => {
  it('should return "Kerberos" for a cluster with kerberos admin password', () => {
    expect(isKerberosCluster(getMockCluster({ kdcAdminPassword: '********' }))).toBe(true);
  });

  it('should return "Basic_Access" for a ldap type clusters', () => {
    expect(isLdapCluster(getMockCluster({ type: 'ldap' }))).toBe(true);
  });
});
