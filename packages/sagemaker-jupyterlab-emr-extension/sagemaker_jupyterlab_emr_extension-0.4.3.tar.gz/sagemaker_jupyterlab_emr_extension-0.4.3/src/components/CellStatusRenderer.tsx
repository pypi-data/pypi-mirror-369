import React from 'react';

const CellStatusRenderer: React.FunctionComponent<any> = ({ cellData }) => {
  const status = cellData.status?.state;
  const statusRunningWaiting = 'Running/Waiting';

  if (cellData.status?.state === 'RUNNING' || cellData.status?.state === 'WAITING') {
    return (
      <div>
        <svg width="10" height="10">
          <circle cx="5" cy="5" r="5" fill="green" />
        </svg>
        <label htmlFor="myInput"> {statusRunningWaiting}</label>
      </div>
    );
  }

  return (
    <div>
      <label htmlFor="myInput">{status}</label>
    </div>
  );
};

export { CellStatusRenderer };
