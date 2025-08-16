import { css } from '@emotion/css';

const ModalBase = css`
  h2 {
    font-size: var(--jp-ui-font-size1);
    margin-top: 0;
  }
`;

const ModalBody = css`
  .DataGrid-ContextMenu > div {
    overflow: hidden;
  }
  margin: 12px;
`;

const ModalHeader = css`
  padding-bottom: var(--jp-add-tag-extra-width);
`;

const ModalFooter = css`
  background-color: var(--jp-layout-color2);
  display: flex;
  justify-content: flex-end;
  button {
    margin: 5px;
  }
`;

const ModalMessage = css`
  text-align: center;
  vertical-align: middle;
`;

const SelectRole = css`
  .jp-select-wrapper select {
    border: 1px solid;
  }
`;

const ListTable = css`
  overflow: hidden;
`;

const NoHorizontalPadding = css`
  padding-left: 0;
  padding-right: 0;
`;

const RadioGroup = css`
  display: flex;
  justify-content: flex-start;
  li {
    margin-right: 20px;
  }
`;

const AuthModal = css`
  min-height: none;
`;

const ListClusterModal = css`
  /* so the modal height remains the same visually during and after loading (this number can be changed) */
  min-height: 600px;
`;

const ConnectCluster = css`
  white-space: nowrap;
`;

const ClusterDescription = css`
  display: inline;
`;

const PresignedURL = css`
  line-height: normal;
`;

const ClusterListModalCrossAccountError = css`
  display: flex;
  flex-direction: column;
  padding: 0 0 10px 0;
`;

const GridWrapper = css`
  box-sizing: border-box;
  width: 100%;
  height: 100%;

  & .ReactVirtualized__Grid {
    /* important is required because react virtualized puts overflow style inline */
    overflow-x: hidden !important;
  }

  & .ReactVirtualized__Table__headerRow {
    display: flex;
  }

  & .ReactVirtualized__Table__row {
    display: flex;
    font-size: 12px;
    align-items: center;
  }
`;

const EmrExecutionRoleContainer = css`
  margin-top: 25px;
  width: 90%;
`;

const Dropdown = css`
  margin-top: var(--jp-cell-padding);
`;

const PresignedURLErrorText = css`
  color: var(--jp-error-color1);
`;

const DialogClassname = css`
  .jp-Dialog-content {
    width: 900px;
    max-width: none;
    max-height: none;
    padding: 0;
  }
  .jp-Dialog-header {
    padding: 24px 24px 12px 24px;
    background-color: var(--jp-layout-color2);
  }
  /* Hide jp footer so we can add custom footer with button controls. */
  .jp-Dialog-footer {
    display: none;
  }
`;

const Footer = css`
  .jp-Dialog-footer {
    background-color: var(--jp-layout-color2);
    margin: 0;
  }
`;

export default {
  ModalBase,
  ModalBody,
  ModalFooter,
  ListTable,
  NoHorizontalPadding,
  RadioGroup,
  ModalHeader,
  ModalMessage,
  AuthModal,
  ListClusterModal,
  ConnectCluster,
  ClusterDescription,
  PresignedURL,
  ClusterListModalCrossAccountError,
  GridWrapper,
  EmrExecutionRoleContainer,
  Dropdown,
  PresignedURLErrorText,
  DialogClassname,
  Footer,
  SelectRole,
};
