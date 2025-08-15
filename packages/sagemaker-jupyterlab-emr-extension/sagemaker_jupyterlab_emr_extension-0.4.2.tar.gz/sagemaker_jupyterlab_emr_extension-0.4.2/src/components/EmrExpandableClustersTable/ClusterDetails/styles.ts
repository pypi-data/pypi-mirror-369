import { css } from '@emotion/css';

const InfoMainContainer = css`
  width: 100%;
  display: flex;
  flex-direction: row;
`;

const InformationContainer = css`
  flex-direction: column;
  margin: 0 32px 8px 8px;
  flex: 1 0 auto;
  width: 33%;
`;

const LinksContainer = css`
  width: 20%;
`;

const Info = css`
  margin-bottom: var(--jp-code-padding);
`;

export { InfoMainContainer, InformationContainer, LinksContainer, Info };
