import { i18nStrings } from '../constants/i18n';
import { ServerlessApplication } from '../constants';

const expandServerlessApplicationStrings = i18nStrings.EmrServerlessApplications.expandApplication;

export const displayReleaseLabel = (application: ServerlessApplication) => {
  const releaseLabel = application?.releaseLabel;
  if (releaseLabel) {
    return `${expandServerlessApplicationStrings.ReleaseLabel}: ${releaseLabel}`;
  }
  return `${expandServerlessApplicationStrings.ReleaseLabel}: ${expandServerlessApplicationStrings.NotAvailable}`;
};

export const displayArchitecture = (application: ServerlessApplication) => {
  const architecture = application?.architecture;
  if (architecture) {
    return `${expandServerlessApplicationStrings.Architecture}: ${architecture}`;
  }
  return `${expandServerlessApplicationStrings.Architecture}: ${expandServerlessApplicationStrings.NotAvailable}`;
};

export const displayWhetherLivyEndpointEnabled = (application: ServerlessApplication) => {
  const livyEndpointEnabled = application?.livyEndpointEnabled;
  if (livyEndpointEnabled === 'True') {
    return `${expandServerlessApplicationStrings.InteractiveLivyEndpoint}: Enabled`;
  } else if (livyEndpointEnabled === 'False') {
    return `${expandServerlessApplicationStrings.InteractiveLivyEndpoint}: Disabled`;
  }
  return `${expandServerlessApplicationStrings.InteractiveLivyEndpoint}: ${expandServerlessApplicationStrings.NotAvailable}`;
};

export const displayMaximumCapacityCpu = (application: ServerlessApplication) => {
  const maximumCapacityCpu = application?.maximumCapacityCpu;

  if (maximumCapacityCpu) {
    return `${expandServerlessApplicationStrings.Cpu}: ${maximumCapacityCpu}`;
  }
  return `${expandServerlessApplicationStrings.Cpu}: ${expandServerlessApplicationStrings.NotAvailable}`;
};

export const displayMaximumCapacityMemory = (application: ServerlessApplication) => {
  const maximumCapacityMemory = application?.maximumCapacityMemory;

  if (maximumCapacityMemory) {
    return `${expandServerlessApplicationStrings.Memory}: ${maximumCapacityMemory}`;
  }
  return `${expandServerlessApplicationStrings.Memory}: ${expandServerlessApplicationStrings.NotAvailable}`;
};

export const displayMaximumCapacityDisk = (application: ServerlessApplication) => {
  const maximumCapacityDisk = application?.maximumCapacityDisk;

  if (maximumCapacityDisk) {
    return `${expandServerlessApplicationStrings.Disk}: ${maximumCapacityDisk}`;
  }
  return `${expandServerlessApplicationStrings.Disk}: ${expandServerlessApplicationStrings.NotAvailable}`;
};
