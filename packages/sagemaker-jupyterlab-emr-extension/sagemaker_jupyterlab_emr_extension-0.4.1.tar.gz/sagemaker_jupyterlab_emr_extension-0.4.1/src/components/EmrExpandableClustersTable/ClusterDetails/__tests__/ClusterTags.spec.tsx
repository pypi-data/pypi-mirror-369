import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect'; // For expect().toBeInTheDocument()
import { ClusterTags } from '../ClusterTags';
import { i18nStrings } from '../../../../constants/i18n';

const expandClusterStrings = i18nStrings.Clusters.expandCluster;

describe('ClusterTags', () => {
  it('renders NoTags message when clusterData is undefined', () => {
    const { getByText } = render(<ClusterTags clusterData={undefined} />);
    expect(getByText(expandClusterStrings.NoTags)).toBeInTheDocument();
  });

  it('renders tags when clusterData has tags', () => {
    const clusterData: any = {
      tags: [
        { key: 'Tag1', value: 'Value1' },
        { key: 'Tag2', value: 'Value2' },
      ],
    };

    const { getByText } = render(<ClusterTags clusterData={clusterData} />);

    expect(getByText('Tag1: Value1')).toBeInTheDocument();
    expect(getByText('Tag2: Value2')).toBeInTheDocument();
  });

  it('renders NoTags message when clusterData has empty tags', () => {
    const clusterData: any = {
      cluster: {
        tags: [],
      },
    };

    const { getByText } = render(<ClusterTags clusterData={clusterData} />);
    expect(getByText(expandClusterStrings.NoTags)).toBeInTheDocument();
  });
});
