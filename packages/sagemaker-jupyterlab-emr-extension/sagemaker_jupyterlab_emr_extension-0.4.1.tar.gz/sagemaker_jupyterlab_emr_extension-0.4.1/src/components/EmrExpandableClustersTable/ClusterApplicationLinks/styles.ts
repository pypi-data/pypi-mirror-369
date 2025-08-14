import { css } from '@emotion/css';

const link = css`
  cursor: pointer;
  & {
    color: var(--jp-content-link-color);
    text-decoration: none;
    text-underline-offset: 1.5px;
    text-decoration: underline;

    &:hover:not([disabled]) {
      text-decoration: underline;
    }

    &:focus:not([disabled]) {
      border: var(--jp-border-width) solid var(--jp-brand-color2);
    }

    &:active:not([disabled]) {
      text-decoration: underline;
    }

    &[disabled] {
      color: var(--jp-ui-font-color3);
    }
  }
`;

const linkContainer = css`
  display: flex;
`;

const loadingIcon = css`
  margin-left: 10px;
`;

const Info = css`
  margin-bottom: var(--jp-code-padding);
`;

export { link, linkContainer, loadingIcon, Info };
