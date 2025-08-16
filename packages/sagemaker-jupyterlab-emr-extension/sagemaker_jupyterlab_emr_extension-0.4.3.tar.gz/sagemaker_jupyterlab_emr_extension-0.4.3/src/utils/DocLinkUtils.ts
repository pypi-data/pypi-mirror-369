import { AWSRegions } from '../service/schemaTypes';

const tutorialLink = 'https://www.youtube.com/playlist?list=PLhr1KZpdzukcOr_6j_zmSrvYnLUtgqsZz';

const isChinaRegion = (region?: AWSRegions) => {
  return region === AWSRegions['cn-north-1'] || region === AWSRegions['cn-northwest-1'];
};

const getDocLinkDomain = (region?: AWSRegions) => {
  if (isChinaRegion(region)) {
    return 'https://docs.amazonaws.cn';
  }
  return 'https://docs.aws.amazon.com';
};

const getTourGuideLink = (region?: AWSRegions) => {
  const docLinkDomain = getDocLinkDomain(region);
  return `${docLinkDomain}/sagemaker/latest/dg/gs-studio-end-to-end.html`;
};

const getTutorialVideoLink = (region?: AWSRegions) => {
  if (isChinaRegion(region)) {
    return 'http://aws.amazon.bokecc.com/news/show-3518.html';
  } else {
    return tutorialLink;
  }
};

export { getDocLinkDomain, getTourGuideLink, getTutorialVideoLink, isChinaRegion };
