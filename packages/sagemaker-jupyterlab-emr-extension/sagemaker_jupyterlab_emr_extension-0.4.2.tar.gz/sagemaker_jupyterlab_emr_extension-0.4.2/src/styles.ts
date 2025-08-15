import { css } from '@emotion/css';

export const ClusterTab = css`
  &:not(:active) {
    color: var(--jp-ui-font-color2);
  }
`;

export const ErrorBannerContainer = css`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  color: var(--jp-error-color0);
  background-color: var(--jp-error-color3);
`;

export const ErrorBannerMessage = css`
  font-size: 12px;
  font-style: normal;
  font-weight: 500;
  line-height: 150%;
  margin: unset;
  flex-grow: 1;
`;
