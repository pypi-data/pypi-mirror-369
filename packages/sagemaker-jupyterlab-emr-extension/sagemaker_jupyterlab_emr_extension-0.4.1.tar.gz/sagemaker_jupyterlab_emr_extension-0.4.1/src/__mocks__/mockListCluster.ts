const originRowData = [
  {
    name: 'Cluster-1',
    id: '1',
    status: { state: 'STARTING' },
    clusterArn: '101001010123',
  },
  {
    name: 'Cluster-2',
    id: '2',
    status: { state: 'WAITING' },
    clusterArn: '101001010125',
  },
  {
    name: 'Cluster-3',
    id: '3',
    status: { state: 'RUNNING' },
    clusterArn: '101001010127',
  },
  {
    name: 'Cluster-4',
    id: '4',
    status: { state: 'TERMINATED' },
    clusterArn: '101001010129',
  },
];

const getData = () => {
  return originRowData;
};

const getClusterDetails = (id: string | undefined) => {
  const validId = Number(id);
  return originRowData[validId - 1];
};

export { getData, originRowData, getClusterDetails };
