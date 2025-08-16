import { fetchApiResponse, OPTIONS_TYPE } from '../service/fetchApiWrapper';
import { Arn } from './ArnUtils';
import { FETCH_EMR_ROLES } from '../service/constants';

const getFilteredAssumableRoles = async (clusterAccountId: string | undefined) => {
  const describeUserProfileInput = JSON.stringify({});
  const describeUserProfileOutput = await fetchApiResponse(
    FETCH_EMR_ROLES,
    OPTIONS_TYPE.POST,
    describeUserProfileInput,
  );
  if (describeUserProfileOutput?.EmrAssumableRoleArns?.length > 0) {
    return describeUserProfileOutput.EmrAssumableRoleArns.filter(
      (roleArn: string) => Arn.fromArnString(roleArn).accountId === clusterAccountId,
    );
  }
};

export { getFilteredAssumableRoles };
