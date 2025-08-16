// Source:  sagemaker-ui-aws-sdk
interface ResourceInfo {
  resourceType: string;
  resourceName: string;
}

class Arn {
  private static ARN_REG_EXP = /^arn:(.*?):(.*?):(.*?):(.*?):(.*)$/;
  private static SPLIT_RESOURCE_INFO_REG_EXP = /^(.*?)[/:](.*)$/;

  public static readonly VERSION_DELIMITER = '/';

  constructor(
    public readonly partition: string = '',
    public readonly service: string = '',
    public readonly region: string = '',
    public readonly accountId: string = '',
    public readonly resourceInfo: string = '',
    public readonly resourceType: string = '',
    public readonly resourceName: string = '',
  ) {}

  public static getResourceInfo(resourceInfoString: string): ResourceInfo {
    const parts = resourceInfoString.match(Arn.SPLIT_RESOURCE_INFO_REG_EXP);
    let resourceType = '';
    let resourceName = '';

    if (parts) {
      if (parts.length === 1) {
        resourceName = parts[1];
      } else {
        resourceType = parts[1];
        resourceName = parts[2];
      }
    }

    return { resourceType, resourceName };
  }

  public static fromArnString(arnString: string): Arn {
    const parts = arnString.match(Arn.ARN_REG_EXP);

    if (!parts) {
      throw new Error(`Invalid ARN format: ${arnString}`);
    }

    const [, partition, service, region, accountId, resourceInfo] = parts;
    const { resourceType = '', resourceName = '' } = resourceInfo ? Arn.getResourceInfo(resourceInfo) : {};

    return new Arn(partition, service, region, accountId, resourceInfo, resourceType, resourceName);
  }

  public static isValid(arnString: string): boolean {
    const parts = arnString.match(Arn.ARN_REG_EXP);

    if (!parts) {
      return false;
    }

    return true;
  }

  public static getArn(
    partition: string,
    service: string,
    region: string,
    accountId: string,
    resourceType: string,
    resourceName: string,
  ): string {
    return `arn:${partition}:${service}:${region}:${accountId}:${resourceType}/${resourceName}`;
  }
}

export { Arn, ResourceInfo };
