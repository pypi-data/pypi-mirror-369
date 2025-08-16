import { css } from '@emotion/css';
import { CSSProperties } from 'react';
import { EmrClusterPluginClassNames } from '../../constants/common';

const NoResultsContainer = css`
  height: 100%;
  position: relative;
`;

const Caret = css`
  margin-right: 10px;
`;

const CaretDown = css`
  ${Caret}
  svg {
    width: 6px;
  }
`;

const HoveredRow = css`
  background-color: var(--jp-layout-color2);
  label: ${EmrClusterPluginClassNames.HoveredCellClassname};
  cursor: pointer;
`;

const SelectedRowInfo = css`
  background-color: var(--jp-layout-color3);
  -webkit-touch-callout: none; /* iOS Safari */
  -webkit-user-select: none; /* Safari */
  -khtml-user-select: none; /* Konqueror HTML */
  -moz-user-select: none; /* Old versions of Firefox */
  -ms-user-select: none; /* Internet Explorer/Edge */
  user-select: none; /* Non-prefixed version, currently supported by Chrome, Opera and Firefox */
  label: ${EmrClusterPluginClassNames.SelectedCellClassname};
`;

const ExpandedRowInfo = css`
  background-color: var(--jp-layout-color2);
  display: flex;
  padding: var(--jp-cell-padding);
  width: 100%;
  align-items: baseline;
  justify-content: start;
  /* box shadow */
  -moz-box-shadow: inset 0 -15px 15px -15px var(--jp-layout-color3);
  -webkit-box-shadow: inset 0 -15px 15px -15px var(--jp-layout-color3);
  box-shadow: inset 0 -15px 15px -15px var(--jp-layout-color3);
  /* Disable visuals for scroll */
  overflow-x: scroll;
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
  &::-webkit-scrollbar {
    display: none;
  }
`;

const TableHeaderRow: CSSProperties = {
  borderTop: 'var(--jp-border-width) solid var(--jp-border-color1)',
  borderBottom: 'var(--jp-border-width) solid var(--jp-border-color1)',
  borderRight: 'var(--jp-border-width) solid var(--jp-border-color1)',
  display: 'flex',
  boxSizing: 'border-box',
  marginRight: '0px',
  padding: '2.5px',
  fontWeight: 'initial',
  textTransform: 'capitalize',
  color: 'var(--jp-ui-font-color2)',
};

const ExpandedRowContainer: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  height: 'max-content',
};

const ExpandableRow = css`
  display: flex;
`;

const Row: CSSProperties = {
  height: 'max-content',
  display: 'flex',
  overflow: 'auto',
  padding: 'var(--jp-cell-padding)',
};

export {
  Caret,
  CaretDown,
  NoResultsContainer,
  HoveredRow,
  SelectedRowInfo,
  TableHeaderRow,
  ExpandedRowInfo,
  ExpandedRowContainer,
  ExpandableRow,
  Row,
};
