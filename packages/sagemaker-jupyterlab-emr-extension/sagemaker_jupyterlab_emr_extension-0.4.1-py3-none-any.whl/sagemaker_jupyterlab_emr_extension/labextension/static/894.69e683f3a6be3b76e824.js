"use strict";(self.webpackChunk_amzn_sagemaker_jupyterlab_emr_extension=self.webpackChunk_amzn_sagemaker_jupyterlab_emr_extension||[]).push([[894],{1894:(e,t,n)=>{n.r(t),n.d(t,{default:()=>Sn});var a=n(4541),r=n(6029),o=n.n(r),s=n(5731),l=n(1837);const i="SelectedCell",c="HoveredCellClassname",d="SelectAuthContainer",u="SelectEMRAccessRoleContainer";var p;!function(e){e.emrConnect="sagemaker-studio:emr-connect",e.emrServerlessConnect="sagemaker-studio:emr-serverless-connect"}(p||(p={}));const m={width:850,height:500};var g;!function(e){e.name="name",e.id="id",e.status="status",e.creationDateTime="creationDateTime",e.arn="clusterArn"}(g||(g={}));const v="AccessDeniedException",h={tabName:"EMR Clusters",widgetTitle:"Connect to cluster",connectCommand:{label:"Connect",caption:"Connect to a cluster"},connectMessage:{errorTitle:"Error connecting to EMR cluster",successTitle:"Successfully connected to EMR cluster",errorDefaultMessage:"Error connecting to EMR cluster",successDefaultMessage:"Connected to EMR Cluster"},selectRoleErrorMessage:{noEmrExecutionRole:"No available EMR execution role found for the cluster. Please provide one in user profile settings.",noEmrAssumableRole:"No available EMR assumable role found for the cluster. Please provide one in user profile settings."},widgetConnected:"The notebook is connected to",defaultTooltip:"Select a cluster to connect to",widgetHeader:"Select a cluster to connect to. A code block will be added to the active cell and run automatically to establish the connection.",connectedWidgetHeader:"cluster. You can submit new jobs to run on the cluster.",connectButton:"Connect",learnMore:"Learn more",noResultsMatchingFilters:"There are no clusters matching the filter.",radioButtonLabels:{basicAccess:"Http basic authentication",RBAC:"Role-based access control",noCredential:"No credential",kerberos:"Kerberos"},fetchEmrRolesError:"Failed to fetch EMR assumable and execution roles",listClusterError:"Fail to list clusters, refresh the modal or try again later",noCluster:"No clusters are available",permissionError:"The IAM role SageMakerStudioClassicExecutionRole does not have permissions needed to list EMR clusters. Update the role with appropriate permissions and try again. Refer to the",selectCluster:"Select a cluster",selectAssumableRoleTitle:"Select an assumable role for cluster",selectRuntimeExecRoleTitle:"Select EMR runtime execution role for cluster",setUpRuntimeExecRole:"Please make sure you have run the prerequisite steps.",selectAuthTitle:"Select credential type for ",clusterButtonLabel:"Cluster",expandCluster:{MasterNodes:"Master nodes",CoreNodes:"Core nodes",NotAvailable:"Not available",NoTags:"No tags",SparkHistoryServer:"Spark History Server",TezUI:"Tez UI",Overview:"Overview",Apps:"Apps",ApplicationUserInterface:"Application user Interface",Tags:"Tags"},presignedURL:{link:"Link",error:"Error: ",retry:"Retry",sparkUIError:"Spark UI Link is not available or time out. Please try ",sshTunnelLink:"SSH tunnel",or:" or ",viewTheGuide:"view the guide",clusterNotReady:"Cluster is not ready. Please try again later.",clusterNotConnected:"No active cluster connection. Please connect to a cluster and try again.",clusterNotCompatible:"EMR version 5.33+ or 6.3.0+ required for direct Spark UI links. Try a compatible cluster, use "}},E="Cancel",f="Select an execution role",C="Select a cross account assumable role",b={name:"Name",id:"ID",status:"Status",creationTime:"Creation Time",createdOn:"Created On",accountId:"Account ID"},y="EMR Serverless Applications",x="No serverless applications are available",w="AccessDeniedException: Please contact your administrator to get permissions to List Applications",R="AccessDeniedException: Please contact your administrator to get permissions to get selected application details",I={Overview:"Overview",NotAvailable:"Not available",NoTags:"No tags",Tags:"Tags",ReleaseLabel:"Release Label",Architecture:"Architecture",InteractiveLivyEndpoint:"Interactive Livy Endpoint",MaximumCapacity:"Maximum Capacity",Cpu:"Cpu",Memory:"Memory",Disk:"Disk"},S=({handleClick:e,tooltip:t})=>o().createElement("div",{className:"EmrClusterContainer"},o().createElement(s.ToolbarButtonComponent,{className:"EmrClusterButton",tooltip:t,label:h.clusterButtonLabel,onClick:e,enabled:!0}));var A;!function(e){e.tab="Tab",e.enter="Enter",e.escape="Escape",e.arrowDown="ArrowDown"}(A||(A={}));var k=n(8278),N=n(7699),T=n(8564);const M={ModalBase:l.css`
  .jp-Dialog-body {
    padding: var(--jp-padding-xl);
    .no-cluster-msg {
      padding: var(--jp-cell-collapser-min-height);
      margin: auto;
    }
  }
`,Header:l.css`
  width: 100%;
  display: contents;
  font-size: 0.5rem;
  h1 {
    margin: 0;
  }
`,HeaderButtons:l.css`
  display: flex;
  float: right;
`,ModalFooter:l.css`
  display: flex;
  justify-content: flex-end;
  background-color: var(--jp-layout-color2);
  padding: 12px 24px 12px 24px;
  button {
    margin: 5px;
  }
`,Footer:l.css`
  .jp-Dialog-footer {
    background-color: var(--jp-layout-color2);
    margin: 0;
  }
`,DismissButton:l.css`
  padding: 0;
  border: none;
  cursor: pointer;
`,DialogClassname:l.css`
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
`},L=({heading:e,headingId:t="modalHeading",className:n,shouldDisplayCloseButton:a=!1,onClickCloseButton:r,actionButtons:s})=>{let i=null,c=null;return a&&(i=o().createElement(k.z,{className:(0,l.cx)(M.DismissButton,"dismiss-button"),role:"button","aria-label":"close",onClick:r,"data-testid":"close-button"},o().createElement(N.closeIcon.react,{tag:"span"}))),s&&(c=s.map((e=>{const{className:t,component:n,onClick:a,label:r}=e;return n?o().createElement("div",{key:`${(0,T.v4)()}`},n):o().createElement(k.z,{className:t,type:"button",role:"button",onClick:a,"aria-label":r,key:`${(0,T.v4)()}`},r)}))),o().createElement("header",{className:(0,l.cx)(M.Header,n)},o().createElement("h1",{id:t},e),o().createElement("div",{className:(0,l.cx)(M.HeaderButtons,"header-btns")},c,i))};var D=n(1105);const P=({onCloseModal:e,onConnect:t,disabled:n})=>o().createElement("footer",{"data-analytics-type":"eventContext","data-analytics":"JupyterLab",className:M.ModalFooter},o().createElement(k.z,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-Footer-CancelButton",className:"jp-Dialog-button jp-mod-reject jp-mod-styled listcluster-cancel-btn",type:"button",onClick:e},E),o().createElement(k.z,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-Footer-ConnectButton",className:"jp-Dialog-button jp-mod-accept jp-mod-styled listcluster-connect-btn",type:"button",onClick:t,disabled:n},h.connectButton));class U{constructor(e="",t="",n="",a="",r="",o="",s=""){this.partition=e,this.service=t,this.region=n,this.accountId=a,this.resourceInfo=r,this.resourceType=o,this.resourceName=s}static getResourceInfo(e){const t=e.match(U.SPLIT_RESOURCE_INFO_REG_EXP);let n="",a="";return t&&(1===t.length?a=t[1]:(n=t[1],a=t[2])),{resourceType:n,resourceName:a}}static fromArnString(e){const t=e.match(U.ARN_REG_EXP);if(!t)throw new Error(`Invalid ARN format: ${e}`);const[,n,a,r,o,s]=t,{resourceType:l="",resourceName:i=""}=s?U.getResourceInfo(s):{};return new U(n,a,r,o,s,l,i)}static isValid(e){return!!e.match(U.ARN_REG_EXP)}static getArn(e,t,n,a,r,o){return`arn:${e}:${t}:${n}:${a}:${r}/${o}`}}U.ARN_REG_EXP=/^arn:(.*?):(.*?):(.*?):(.*?):(.*)$/,U.SPLIT_RESOURCE_INFO_REG_EXP=/^(.*?)[/:](.*)$/,U.VERSION_DELIMITER="/";const j=({cellData:e})=>{var t,n,a;const r=null===(t=e.status)||void 0===t?void 0:t.state;return"RUNNING"===(null===(n=e.status)||void 0===n?void 0:n.state)||"WAITING"===(null===(a=e.status)||void 0===a?void 0:a.state)?o().createElement("div",null,o().createElement("svg",{width:"10",height:"10"},o().createElement("circle",{cx:"5",cy:"5",r:"5",fill:"green"})),o().createElement("label",{htmlFor:"myInput"}," ","Running/Waiting")):o().createElement("div",null,o().createElement("label",{htmlFor:"myInput"},r))};var _,$,O,B,F,z,G;!function(e){e.Bootstrapping="BOOTSTRAPPING",e.Running="RUNNING",e.Starting="STARTING",e.Terminated="TERMINATED",e.TerminatedWithErrors="TERMINATED_WITH_ERRORS",e.Terminating="TERMINATING",e.Undefined="UNDEFINED",e.Waiting="WAITING"}(_||(_={})),function(e){e.AllStepsCompleted="All_Steps_Completed",e.BootstrapFailure="Bootstrap_Failure",e.InstanceFailure="Instance_Failure",e.InstanceFleetTimeout="Instance_Fleet_Timeout",e.InternalError="Internal_Error",e.StepFailure="Step_Failure",e.UserRequest="User_Request",e.ValidationError="Validation_Error"}($||($={})),function(e){e[e.SHS=0]="SHS",e[e.TEZUI=1]="TEZUI",e[e.YTS=2]="YTS"}(O||(O={})),function(e){e.None="None",e.Basic_Access="Basic_Access",e.RBAC="RBAC",e.Kerberos="Kerberos"}(B||(B={})),function(e){e.Success="Success",e.Fail="Fail"}(F||(F={})),function(e){e[e.Content=0]="Content",e[e.External=1]="External",e[e.Notebook=2]="Notebook"}(z||(z={})),function(e){e.Started="STARTED",e.Starting="STARTING",e.Created="CREATED",e.Creating="CREATING",e.Stopped="STOPPED",e.Stopping="STOPPING",e.Terminated="TERMINATED"}(G||(G={}));const H=b;var J=n(2510),V=n(4321);l.css`
  height: 100%;
  position: relative;
`;const K=l.css`
  margin-right: 10px;
`,W=(l.css`
  ${K}
  svg {
    width: 6px;
  }
`,l.css`
  background-color: var(--jp-layout-color2);
  label: ${c};
  cursor: pointer;
`),q=l.css`
  background-color: var(--jp-layout-color3);
  -webkit-touch-callout: none; /* iOS Safari */
  -webkit-user-select: none; /* Safari */
  -khtml-user-select: none; /* Konqueror HTML */
  -moz-user-select: none; /* Old versions of Firefox */
  -ms-user-select: none; /* Internet Explorer/Edge */
  user-select: none; /* Non-prefixed version, currently supported by Chrome, Opera and Firefox */
  label: ${i};
`,X=l.css`
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
`,Y={borderTop:"var(--jp-border-width) solid var(--jp-border-color1)",borderBottom:"var(--jp-border-width) solid var(--jp-border-color1)",borderRight:"var(--jp-border-width) solid var(--jp-border-color1)",display:"flex",boxSizing:"border-box",marginRight:"0px",padding:"2.5px",fontWeight:"initial",textTransform:"capitalize",color:"var(--jp-ui-font-color2)"},Z={display:"flex",flexDirection:"column",height:"max-content"},Q=l.css`
  display: flex;
`,ee={height:"max-content",display:"flex",overflow:"auto",padding:"var(--jp-cell-padding)"},te=({isSelected:e})=>e?o().createElement(N.caretDownIcon.react,{tag:"span"}):o().createElement(N.caretRightIcon.react,{tag:"span"}),ne=({dataList:e,tableConfig:t,selectedId:n,expandedView:a,noResultsView:s,showIcon:i,isLoading:c,columnConfig:d,onRowSelect:u,...p})=>{const m=(0,r.useRef)(null),g=(0,r.useRef)(null),[v,h]=(0,r.useState)(-1),[E,f]=(0,r.useState)(0);(0,r.useEffect)((()=>{var e,t;f((null===(e=null==g?void 0:g.current)||void 0===e?void 0:e.clientHeight)||40),null===(t=m.current)||void 0===t||t.recomputeRowHeights()}),[n,c,t.width,t.height]);const C=({rowData:e,...t})=>e?(0,J.defaultTableCellDataGetter)({rowData:e,...t}):null;return o().createElement(J.Table,{...p,...t,headerStyle:Y,ref:m,headerHeight:40,overscanRowCount:10,rowCount:e.length,rowData:e,noRowsRenderer:()=>s,rowHeight:({index:t})=>e[t].id&&e[t].id===n?E:40,rowRenderer:e=>{const{style:t,key:r,rowData:s,index:i,className:c}=e,d=n===s.id,u=v===i,p=(0,l.cx)(Q,c,{[q]:d,[W]:!d&&u});return d?o().createElement("div",{key:r,ref:g,style:{...t,...Z},onMouseEnter:()=>h(i),onMouseLeave:()=>h(-1),className:p},(0,V.Cx)({...e,style:{width:t.width,...ee}}),o().createElement("div",{className:X},a)):o().createElement("div",{key:r,onMouseEnter:()=>h(i),onMouseLeave:()=>h(-1)},(0,V.Cx)({...e,className:p}))},onRowClick:({rowData:e})=>u(e),rowGetter:({index:t})=>e[t]},d.map((({dataKey:t,label:a,disableSort:r,cellRenderer:s})=>o().createElement(J.Column,{key:t,dataKey:t,label:a,flexGrow:1,width:150,disableSort:r,cellDataGetter:C,cellRenderer:t=>((t,a)=>{const{rowIndex:r,columnIndex:s}=t,l=e[r].id===n,c=0===s;let d=null;return a&&(d=a({row:e[r],rowIndex:r,columnIndex:s,onCellSizeChange:()=>null})),c&&i?o().createElement(o().Fragment,null,o().createElement(te,{isSelected:l})," ",d):d})(t,s)}))))},ae=l.css`
  height: 100%;
  position: relative;
`,re=l.css`
  margin-right: 10px;
`,oe=(l.css`
  ${re}
  svg {
    width: 6px;
  }
`,l.css`
  text-align: center;
  margin: 0;
  position: absolute;
  top: 50%;
  left: 50%;
  margin-right: -50%;
  transform: translate(-50%, -50%);
`),se=(l.css`
  background-color: var(--jp-layout-color2);
  label: ${c};
  cursor: pointer;
`,l.css`
  background-color: var(--jp-layout-color3);
  -webkit-touch-callout: none; /* iOS Safari */
  -webkit-user-select: none; /* Safari */
  -khtml-user-select: none; /* Konqueror HTML */
  -moz-user-select: none; /* Old versions of Firefox */
  -ms-user-select: none; /* Internet Explorer/Edge */
  user-select: none; /* Non-prefixed version, currently supported by Chrome, Opera and Firefox */
  label: ${i};
`,l.css`
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
`,l.css`
  padding: 24px 24px 12px 24px;
`),le=l.css`
  .ReactVirtualized__Table__headerRow {
    display: flex;
    align-items: center;
  }
  .ReactVirtualized__Table__row {
    display: flex;
    font-size: 12px;
    align-items: center;
  }
`,ie=l.css`
  width: 100%;
  display: flex;
  flex-direction: row;
`,ce=l.css`
  flex-direction: column;
  margin: 0 32px 8px 8px;
  flex: 1 0 auto;
  width: 33%;
`,de=l.css`
  width: 20%;
`,ue=l.css`
  margin-bottom: var(--jp-code-padding);
`,pe=h.expandCluster,me=({clusterData:e})=>{const t=null==e?void 0:e.tags;return(null==t?void 0:t.length)?o().createElement(o().Fragment,null,t.map((e=>o().createElement("div",{className:ue,key:null==e?void 0:e.key},null==e?void 0:e.key,": ",null==e?void 0:e.value)))):o().createElement("div",null,pe.NoTags)},ge=h.expandCluster;var ve=n(3587),he=n(7174);const Ee="/aws/sagemaker/api/emr/describe-cluster",fe="/aws/sagemaker/api/emr/describe-security-configuration",Ce="/aws/sagemaker/api/emr/get-on-cluster-app-ui-presigned-url",be="/aws/sagemaker/api/emr/create-persistent-app-ui",ye="/aws/sagemaker/api/emr/describe-persistent-app-ui",xe="/aws/sagemaker/api/emr/get-persistent-app-ui-presigned-url",we="/aws/sagemaker/api/emr/list-instance-groups",Re="/aws/sagemaker/api/sagemaker/fetch-emr-roles",Ie="/aws/sagemaker/api/emr-serverless/get-application",Se=[200,201];var Ae;!function(e){e.POST="POST",e.GET="GET",e.PUT="PUT"}(Ae||(Ae={}));const ke=async(e,t,n)=>{const a=ve.ServerConnection.makeSettings(),r=he.URLExt.join(a.baseUrl,e);try{const e=await ve.ServerConnection.makeRequest(r,{method:t,body:n},a);if(!Se.includes(e.status)&&r.includes("list-clusters"))throw 400===e.status?new Error("permission error"):new Error("Unable to fetch data");return e.json()}catch(e){return{error:e}}},Ne=async e=>{var t;const n=JSON.stringify({}),a=await ke(Re,Ae.POST,n);if((null===(t=null==a?void 0:a.EmrAssumableRoleArns)||void 0===t?void 0:t.length)>0)return a.EmrAssumableRoleArns.filter((t=>U.fromArnString(t).accountId===e))},Te="ApplicationMaster",Me=async(e,t)=>{if(void 0===e)throw new Error("Error describing persistent app UI: Invalid persistent app UI ID");if(t){const n={PersistentAppUIId:e,RoleArn:t},a=JSON.stringify(n);return await ke(ye,Ae.POST,a)}const n={PersistentAppUIId:e},a=JSON.stringify(n);return await ke(ye,Ae.POST,a)},Le=async e=>await new Promise((t=>setTimeout(t,e))),De=async(e,t)=>{const n={ClusterId:e},a=await Ne(t);if((null==a?void 0:a.length)>0)for(const t of a){const n=JSON.stringify({ClusterId:e,RoleArn:t}),a=await ke(Ee,Ae.POST,n);if(void 0!==(null==a?void 0:a.cluster))return a}const r=JSON.stringify(n);return await ke(Ee,Ae.POST,r)},Pe=async(e,t)=>{const n={applicationId:e},a=await Ne(t);if((null==a?void 0:a.length)>0)for(const t of a){const n=JSON.stringify({applicationId:e,RoleArn:t}),a=await ke(Ie,Ae.POST,n);if(void 0!==(null==a?void 0:a.application))return a}const r=JSON.stringify(n);return await ke(Ie,Ae.POST,r)},Ue="smsjp--icon-link-external",je={link:l.css`
  a& {
    color: var(--jp-content-link-color);
    line-height: var(--jp-custom-ui-text-line-height);
    text-decoration: none;
    text-underline-offset: 1.5px;

    span.${Ue} {
      display: inline;
      svg {
        width: var(--jp-ui-font-size1);
        height: var(--jp-ui-font-size1);
        margin-left: var(--jp-ui-font-size1;
        transform: scale(calc(var(--jp-custom-ui-text-line-height) / 24));
      }
      path {
        fill: var(--jp-ui-font-color1);
      }
    }

    &.sm--content-link {
      text-decoration: underline;
    }

    &:hover:not([disabled]) {
      text-decoration: underline;
    }

    &:focus:not([disabled]),
    &:active:not([disabled]) {
      color: var(--jp-brand-color2);
      .${Ue} path {
        fill: var(--jp-ui-font-color1);
      }
    }

    &:focus:not([disabled]) {
      border: var(--jp-border-width) solid var(--jp-brand-color2);
    }

    &:active:not([disabled]) {
      text-decoration: underline;
    }

    &[disabled] {
      color: var(--jp-ui-font-color3);
      .${Ue} path {
        fill: var(--jp-ui-font-color1);
      }
    }
  }
`,externalIconClass:Ue};var _e;!function(e){e[e.Content=0]="Content",e[e.External=1]="External",e[e.Notebook=2]="Notebook"}(_e||(_e={}));const $e=({children:e,className:t,disabled:n=!1,href:a,onClick:r,type:s=_e.Content,hideExternalIcon:i=!1,...c})=>{const d=s===_e.External,u={className:(0,l.cx)(je.link,t,{"sm-emr-content":s===_e.Content}),href:a,onClick:n?void 0:r,target:d?"_blank":void 0,rel:d?"noopener noreferrer":void 0,...c},p=d&&!i?o().createElement("span",{className:je.externalIconClass},o().createElement(N.launcherIcon.react,{tag:"span"})):null;return o().createElement("a",{role:"link",...u},e,p)},Oe=l.css`
  h2 {
    font-size: var(--jp-ui-font-size1);
    margin-top: 0;
  }
`,Be=l.css`
  .DataGrid-ContextMenu > div {
    overflow: hidden;
  }
  margin: 12px;
`,Fe=l.css`
  padding-bottom: var(--jp-add-tag-extra-width);
`,ze=l.css`
  background-color: var(--jp-layout-color2);
  display: flex;
  justify-content: flex-end;
  button {
    margin: 5px;
  }
`,Ge=l.css`
  text-align: center;
  vertical-align: middle;
`,He=l.css`
  .jp-select-wrapper select {
    border: 1px solid;
  }
`,Je={ModalBase:Oe,ModalBody:Be,ModalFooter:ze,ListTable:l.css`
  overflow: hidden;
`,NoHorizontalPadding:l.css`
  padding-left: 0;
  padding-right: 0;
`,RadioGroup:l.css`
  display: flex;
  justify-content: flex-start;
  li {
    margin-right: 20px;
  }
`,ModalHeader:Fe,ModalMessage:Ge,AuthModal:l.css`
  min-height: none;
`,ListClusterModal:l.css`
  /* so the modal height remains the same visually during and after loading (this number can be changed) */
  min-height: 600px;
`,ConnectCluster:l.css`
  white-space: nowrap;
`,ClusterDescription:l.css`
  display: inline;
`,PresignedURL:l.css`
  line-height: normal;
`,ClusterListModalCrossAccountError:l.css`
  display: flex;
  flex-direction: column;
  padding: 0 0 10px 0;
`,GridWrapper:l.css`
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
`,EmrExecutionRoleContainer:l.css`
  margin-top: 25px;
  width: 90%;
`,Dropdown:l.css`
  margin-top: var(--jp-cell-padding);
`,PresignedURLErrorText:l.css`
  color: var(--jp-error-color1);
`,DialogClassname:l.css`
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
`,Footer:l.css`
  .jp-Dialog-footer {
    background-color: var(--jp-layout-color2);
    margin: 0;
  }
`,SelectRole:He},Ve="Invalid Cluster State",Ke="Missing Cluster ID, are you connected to a cluster?",We="Unsupported cluster version",qe=({clusterId:e,accountId:t,applicationId:n,persistentAppUIType:a,label:s,onError:i})=>{const[c,d]=(0,r.useState)(!1),[u,p]=(0,r.useState)(!1),m=(0,r.useCallback)((e=>{p(!0),i(e)}),[i]),g=(0,r.useCallback)((e=>{if(!e)throw new Error("Error opening Spark UI: Invalid URL");null!==window.open(e,"_blank","noopener,noreferrer")&&(p(!1),i(null))}),[i]),v=(0,r.useCallback)(((e,t,n)=>{(async(e,t,n)=>{const a=await Ne(e);if((null==a?void 0:a.length)>0)for(const e of a){const a={ClusterId:t,OnClusterAppUIType:Te,ApplicationId:n,RoleArn:e},r=JSON.stringify(a),o=await ke(Ce,Ae.POST,r);if(void 0!==(null==o?void 0:o.presignedURL))return o}const r={ClusterId:t,OnClusterAppUIType:Te,ApplicationId:n},o=JSON.stringify(r);return await ke(Ce,Ae.POST,o)})(t,e,n).then((e=>g(null==e?void 0:e.presignedURL))).catch((e=>m(e))).finally((()=>d(!1)))}),[m,g]),E=(0,r.useCallback)(((e,t,n,a)=>{(async e=>{if(void 0===e)throw new Error("Error describing persistent app UI: Invalid persistent app UI ID");const t=U.fromArnString(e).accountId,n=await Ne(t);if((null==n?void 0:n.length)>0)for(const t of n){const n={TargetResourceArn:e,RoleArn:t},a=JSON.stringify(n),r=await ke(be,Ae.POST,a);if(void 0!==(null==r?void 0:r.persistentAppUIId))return r}const a={TargetResourceArn:e},r=JSON.stringify(a);return await ke(be,Ae.POST,r)})(e.clusterArn).then((e=>(async(e,t,n,a)=>{var r;const o=Date.now();let s,l=0;for(;l<=3e4;){const t=await Me(e,a),n=null===(r=null==t?void 0:t.persistentAppUI)||void 0===r?void 0:r.persistentAppUIStatus;if(n&&"ATTACHED"===n){s=t;break}await Le(2e3),l=Date.now()-o}if(null==s)throw new Error("Error waiting for persistent app UI ready: Max attempts reached");return s})(null==e?void 0:e.persistentAppUIId,0,0,null==e?void 0:e.roleArn))).then((e=>(async(e,t,n,a)=>{if(void 0===e)throw new Error("Error getting persistent app UI presigned URL: Invalid persistent app UI ID");if(t){const a={PersistentAppUIId:e,PersistentAppUIType:n,RoleArn:t},r=JSON.stringify(a);return await ke(xe,Ae.POST,r)}const r={PersistentAppUIId:e,PersistentAppUIType:n},o=JSON.stringify(r);return await ke(xe,Ae.POST,o)})(null==e?void 0:e.persistentAppUI.persistentAppUIId,null==e?void 0:e.roleArn,a))).then((e=>g(null==e?void 0:e.presignedURL))).catch((e=>m(e))).finally((()=>d(!1)))}),[m,g]),f=(0,r.useCallback)(((e,t,n,a)=>async()=>{if(d(!0),!t)return d(!1),void m(Ke);const r=await De(t,e).catch((e=>m(e)));if(!r||!(null==r?void 0:r.cluster))return void d(!1);const o=null==r?void 0:r.cluster;if(o.releaseLabel)try{const e=o.releaseLabel.substr(4).split("."),t=+e[0],n=+e[1];if(t<5)return d(!1),void m(We);if(5===t&&n<33)return d(!1),void m(We);if(6===t&&n<3)return d(!1),void m(We)}catch(e){}switch(o.status.state){case _.Running:case _.Waiting:n?v(t,e,n):E(o,e,n,a);break;case _.Terminated:E(o,e,n,a);break;default:d(!1),m(Ve)}}),[v,E,m]);return o().createElement(o().Fragment,null,c?o().createElement("span",null,o().createElement(D.CircularProgress,{size:"1rem"})):o().createElement($e,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-PresignedUrl-Click",className:(0,l.cx)("PresignedURL",Je.PresignedURL),onClick:f(t,e,n,a)},u?o().createElement("span",null,s&&s," ",o().createElement("span",{className:(0,l.cx)("PresignedURLErrorText",Je.PresignedURLErrorText),onClick:f(t,e,n,a)},"(",h.presignedURL.retry,")")):s||h.presignedURL.link))},Xe=l.css`
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
`,Ye=l.css`
  display: flex;
`,Ze=(l.css`
  margin-left: 10px;
`,l.css`
  margin-bottom: var(--jp-code-padding);
`),Qe=h.expandCluster,et=({clusterId:e,accountId:t,setIsError:n})=>{const[a]=(0,r.useState)(!1);return o().createElement("div",{className:Ye},o().createElement("div",{className:(0,l.cx)("HistoryLink",Xe)},o().createElement(qe,{clusterId:e,onError:e=>e,accountId:t,persistentAppUIType:"SHS",label:Qe.SparkHistoryServer})),o().createElement(N.launcherIcon.react,{tag:"span"}),a&&o().createElement("span",null,o().createElement(D.CircularProgress,{size:"1rem"})))},tt=h.expandCluster,nt=({clusterId:e,accountId:t,setIsError:n})=>{const[a]=o().useState(!1);return o().createElement("div",{className:Ye},o().createElement("div",{className:Xe},o().createElement(qe,{clusterId:e,onError:e=>e,accountId:t,persistentAppUIType:"TEZ",label:tt.TezUI})),o().createElement(N.launcherIcon.react,{tag:"span"}),a&&o().createElement("span",null,o().createElement(D.CircularProgress,{size:"1rem"})))},at=h.expandCluster,rt=e=>{const{accountId:t,selectedClusterId:n}=e,[a,s]=(0,r.useState)(!1);return a?o().createElement("div",null,at.NotAvailable):o().createElement(o().Fragment,null,o().createElement("div",{className:Ze},o().createElement(et,{clusterId:n,accountId:t,setIsError:s})),o().createElement("div",{className:Ze},o().createElement(nt,{clusterId:n,accountId:t,setIsError:s})))},ot=h.expandCluster,st=({clusterArn:e,accountId:t,selectedClusterId:n,clusterData:a})=>{const s=a,[i,c]=(0,r.useState)();return(0,r.useEffect)((()=>{(async e=>{var n,a;const r=JSON.stringify({ClusterId:e}),o=await ke(we,Ae.POST,r);if((null===(n=o.instanceGroups)||void 0===n?void 0:n.length)>0&&(null===(a=o.instanceGroups[0].id)||void 0===a?void 0:a.length)>0)c(o);else{const n=await Ne(t);if((null==n?void 0:n.length)>0)for(const t of n){const n=JSON.stringify({ClusterId:e,RoleArn:t}),a=await ke(we,Ae.POST,n);a.instanceGroups.length>0&&a.instanceGroups[0].id&&c(a)}}})(n)}),[n]),o().createElement("div",{"data-analytics-type":"eventContext","data-analytics":"JupyterLab",className:ie},o().createElement("div",{className:ce},o().createElement("h4",null,ot.Overview),o().createElement("div",{className:ue},(e=>{var t;const n=null===(t=null==e?void 0:e.instanceGroups)||void 0===t?void 0:t.find((e=>"MASTER"===(null==e?void 0:e.instanceGroupType)));if(n){const e=n.runningInstanceCount,t=n.instanceType;return`${ge.MasterNodes}: ${e}, ${t}`}return`${ge.MasterNodes}: ${ge.NotAvailable}`})(i)),o().createElement("div",{className:ue},(e=>{var t;const n=null===(t=null==e?void 0:e.instanceGroups)||void 0===t?void 0:t.find((e=>"CORE"===(null==e?void 0:e.instanceGroupType)));if(n){const e=n.runningInstanceCount,t=n.instanceType;return`${ge.CoreNodes}: ${e}, ${t}`}return`${ge.CoreNodes}: ${ge.NotAvailable}`})(i)),o().createElement("div",{className:ue},ot.Apps,": ",(e=>{const t=null==e?void 0:e.applications;return(null==t?void 0:t.length)?t.map(((e,n)=>{const a=n===t.length-1?".":", ";return`${null==e?void 0:e.name} ${null==e?void 0:e.version}${a}`})):`${ge.NotAvailable}`})(s))),o().createElement("div",{className:(0,l.cx)(ce,de)},o().createElement("h4",null,ot.ApplicationUserInterface),o().createElement(rt,{selectedClusterId:n,accountId:t,clusterArn:e})),o().createElement("div",{className:ce},o().createElement("h4",null,ot.Tags),o().createElement(me,{clusterData:a})))},lt=h,it=o().createElement("div",{className:ae},o().createElement("p",{className:oe},lt.noResultsMatchingFilters)),ct=({clustersList:e,tableConfig:t,clusterManagementListConfig:n,selectedClusterId:a,clusterArn:r,accountId:s,onRowSelect:l,clusterDetails:i,...c})=>{const d=!i&&!1,u=i;return o().createElement(ne,{...c,tableConfig:t,showIcon:!0,dataList:e,selectedId:a,columnConfig:n,isLoading:d,noResultsView:it,onRowSelect:l,expandedView:d?o().createElement("span",null,o().createElement(D.CircularProgress,{size:"1rem"})):o().createElement(st,{selectedClusterId:a,accountId:s||"",clusterArn:r,clusterData:u,instanceGroupData:void 0})})};n(7960);const dt=e=>"string"==typeof e&&e.length>0,ut=e=>Array.isArray(e)&&e.length>0,pt=(e,t)=>{window&&window.panorama&&window.panorama("trackCustomEvent",{eventType:"eventDetail",eventDetail:e,eventContext:t,timestamp:Date.now()})},mt=(e,t,n)=>{t.execute(e,n)},gt=e=>t=>n=>{mt(e,t,n)},vt=Object.fromEntries(Object.entries(p).map((e=>{const t=e[0],n=e[1];return[t,(a=n,{id:a,createRegistryWrapper:gt(a),execute:(e,t)=>mt(a,e,t)})];var a}))),ht=({onCloseModal:e,selectedCluster:t,selectedServerlessApplication:n,emrConnectRoleData:a,app:s,selectedAssumableRoleArn:i})=>{const c=`${u}`,d=t?a.EmrExecutionRoleArns.filter((e=>U.fromArnString(e).accountId===t.clusterAccountId)):n?a.EmrExecutionRoleArns.filter((e=>U.fromArnString(e).accountId===U.fromArnString(n.arn).accountId)):[],p=d.length?d[0]:void 0,[m,g]=(0,r.useState)(p),v=d.length?o().createElement(N.HTMLSelect,{className:(0,l.cx)(Je.SelectRole),options:d,value:m,title:f,onChange:e=>{g(e.target.value)},"data-testid":"select-runtime-exec-role"}):o().createElement("span",{className:"error-msg"},h.selectRoleErrorMessage.noEmrExecutionRole);return o().createElement("div",{className:(0,l.cx)(c,Je.ModalBase,Je.AuthModal)},o().createElement("div",{className:(0,l.cx)(c,Je.ModalBody,Je.SelectRole)},v),o().createElement("div",{className:(0,l.cx)(c,Je.ModalBody)},o().createElement($e,{href:t?"https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-steps-runtime-roles.html#emr-steps-runtime-roles-configure":n?"https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/getting-started.html#gs-runtime-role":"",type:_e.External},h.setUpRuntimeExecRole)),o().createElement(P,{onCloseModal:e,onConnect:()=>{if(e(),t){const e={clusterId:t.id,language:"python",authType:B.Basic_Access,executionRoleArn:m};i&&Object.assign(e,{crossAccountArn:i}),s.commands.execute(vt.emrConnect.id,e),pt("EMR-Connect-RBAC","JupyterLab")}else if(n){const e={serverlessApplicationId:n.id,executionRoleArn:m,language:"python",assumableRoleArn:i};s.commands.execute(vt.emrServerlessConnect.id,e)}},disabled:void 0===m}))},Et=({onCloseModal:e,selectedCluster:t,emrConnectRoleData:n,app:a,selectedAssumableRoleArn:s})=>{const i=`${d}`,c=`${d}`,[u,p]=(0,r.useState)(B.Basic_Access);return o().createElement("div",{className:(0,l.cx)(i,Je.ModalBase,Je.AuthModal)},o().createElement("div",{className:(0,l.cx)(c,Je.ModalBody)},o().createElement(D.FormControl,null,o().createElement(D.RadioGroup,{"aria-labelledby":"demo-radio-buttons-group-label",defaultValue:B.Basic_Access,value:u,onChange:e=>{p(e.target.value)},name:"radio-buttons-group","data-testid":"radio-button-group",row:!0},o().createElement(D.FormControlLabel,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-SelectAuth-BasicAccess-Click",value:B.Basic_Access,control:o().createElement(D.Radio,null),label:h.radioButtonLabels.basicAccess}),o().createElement(D.FormControlLabel,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-SelectAuth-RBAC-Click",value:B.RBAC,control:o().createElement(D.Radio,null),label:h.radioButtonLabels.RBAC}),o().createElement(D.FormControlLabel,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-SelectAuth-Kerberos-Click",value:B.Kerberos,control:o().createElement(D.Radio,null),label:h.radioButtonLabels.kerberos}),o().createElement(D.FormControlLabel,{"data-analytics-type":"eventDetail","data-analytics":"EMR-Modal-SelectAuth-None-Click",value:B.None,control:o().createElement(D.Radio,null),label:h.radioButtonLabels.noCredential})))),o().createElement(P,{onCloseModal:e,onConnect:()=>{if(u===B.RBAC)e(),xt(n,a,s,t);else{e();const n={clusterId:t.id,authType:u,language:"python"};s&&Object.assign(n,{crossAccountArn:s}),a.commands.execute(vt.emrConnect.id,n),pt("EMR-Connect-Non-RBAC","JupyterLab")}},disabled:!1}))},ft=e=>{var t;return Boolean(null===(t=e.configurations)||void 0===t?void 0:t.some((e=>{var t;return"ldap"===(null===(t=null==e?void 0:e.properties)||void 0===t?void 0:t.livyServerAuthType)})))},Ct=({onCloseModal:e,selectedCluster:t,selectedServerlessApplication:n,emrConnectRoleData:a,app:s})=>{const i=`${u}`,c=t?a.EmrAssumableRoleArns.filter((e=>U.fromArnString(e).accountId===t.clusterAccountId)):n?a.EmrAssumableRoleArns.filter((e=>U.fromArnString(e).accountId===U.fromArnString(n.arn).accountId)):[],d=c.length?c[0]:void 0,[p,m]=(0,r.useState)(d),g=c.length?o().createElement(N.HTMLSelect,{title:C,options:c,value:p,onChange:e=>{m(e.target.value)},"data-testid":"select-assumable-role"}):o().createElement("span",{className:"error-msg"},h.selectRoleErrorMessage.noEmrAssumableRole);return o().createElement("div",{className:(0,l.cx)(i,Je.ModalBase,Je.AuthModal)},o().createElement("div",{className:(0,l.cx)(i,Je.ModalBody,Je.SelectRole)},g),o().createElement(P,{onCloseModal:e,onConnect:()=>{if(e(),t){if(ft(t))return void wt(s,t,p);yt(t,a,s,p),pt("EMR-Select-Assumable-Role","JupyterLab")}else n&&xt(a,s,p,void 0,n)},disabled:void 0===p}))},bt=(e,t,n,a)=>{let r={};const i=()=>r&&r.resolve();r=new s.Dialog({title:o().createElement(L,{heading:`${h.selectAssumableRoleTitle}`,shouldDisplayCloseButton:!0,onClickCloseButton:i}),body:o().createElement(Ct,{onCloseModal:i,selectedCluster:n,selectedServerlessApplication:a,emrConnectRoleData:e,app:t})}),r.addClass((0,l.cx)(M.ModalBase,M.Footer,M.DialogClassname)),r.launch()},yt=(e,t,n,a)=>{let r={};const i=()=>r&&r.resolve();r=new s.Dialog({title:o().createElement(L,{heading:`${h.selectAuthTitle}"${e.name}"`,shouldDisplayCloseButton:!0,onClickCloseButton:i}),body:o().createElement(Et,{onCloseModal:i,selectedCluster:e,emrConnectRoleData:t,app:n,selectedAssumableRoleArn:a})}),r.addClass((0,l.cx)(M.ModalBase,M.Footer,M.DialogClassname)),r.launch()},xt=(e,t,n,a,r)=>{let i={};const c=()=>i&&i.resolve();i=new s.Dialog({title:o().createElement(L,{heading:`${h.selectRuntimeExecRoleTitle}`,shouldDisplayCloseButton:!0,onClickCloseButton:c}),body:o().createElement(ht,{onCloseModal:c,selectedCluster:a,selectedServerlessApplication:r,emrConnectRoleData:e,app:t,selectedAssumableRoleArn:n})}),i.addClass((0,l.cx)(M.ModalBase,M.Footer,M.DialogClassname)),i.launch()},wt=(e,t,n="")=>{const a=B.Basic_Access,r={clusterId:t.id,authType:a,language:"python"};n&&Object.assign(r,{crossAccountArn:n}),e.commands.execute(vt.emrConnect.id,r),pt("EMR-Connect-Special-Cluster","JupyterLab")},Rt=e=>{const{onCloseModal:t,header:n,app:a}=e,[s,i]=(0,r.useState)([]),[c,d]=(0,r.useState)(!1),[u,p]=(0,r.useState)(""),[v,E]=(0,r.useState)(void 0),[f,C]=(0,r.useState)(),[b,y]=(0,r.useState)(""),[x,w]=(0,r.useState)(!0),R=[{dataKey:g.name,label:H.name,disableSort:!0,cellRenderer:({row:e})=>null==e?void 0:e.name},{dataKey:g.id,label:H.id,disableSort:!0,cellRenderer:({row:e})=>null==e?void 0:e.id},{dataKey:g.status,label:H.status,disableSort:!0,cellRenderer:({row:e})=>o().createElement(j,{cellData:e})},{dataKey:g.creationDateTime,label:H.creationTime,disableSort:!0,cellRenderer:({row:e})=>{var t;return null===(t=null==e?void 0:e.status)||void 0===t?void 0:t.timeline.creationDateTime.split("+")[0].split(".")[0]}},{dataKey:g.arn,label:H.accountId,disableSort:!0,cellRenderer:({row:e})=>{if(null==e?void 0:e.clusterArn)return U.fromArnString(e.clusterArn).accountId}}],I=async(e="",t)=>{try{do{const n=JSON.stringify({ClusterStates:["RUNNING","WAITING"],...e&&{Marker:e},RoleArn:t}),a=await ke("/aws/sagemaker/api/emr/list-clusters",Ae.POST,n);a&&a.clusters&&i((e=>[...new Map([...e,...a.clusters].map((e=>[e.id,e]))).values()])),e=null==a?void 0:a.Marker}while(dt(e))}catch(e){p(e.message)}};(0,r.useEffect)((()=>{(async()=>{var e;try{d(!0);const t=JSON.stringify({}),n=await ke(Re,Ae.POST,t);if((null===(e=null==n?void 0:n.EmrAssumableRoleArns)||void 0===e?void 0:e.length)>0)for(const e of n.EmrAssumableRoleArns)await I("",e);await I(),d(!1)}catch(e){d(!1),p(e.message)}})()}),[]);(0,r.useEffect)((()=>{f&&E((async e=>{var t;const n=S.find((t=>t.id===e));let a="";const r=null==n?void 0:n.clusterArn;r&&U.isValid(r)&&(a=U.fromArnString(r).accountId);const o=await De(e,a);if(null==o?void 0:o.cluster.id){const e="string"==typeof(null==o?void 0:o.cluster.securityConfiguration)?null==o?void 0:o.cluster.securityConfiguration:null===(t=null==o?void 0:o.cluster.securityConfiguration)||void 0===t?void 0:t.name;if(e){const t={securityConfigurationName:e,authentication:""};try{const n=await(async(e,t,n)=>{const a=JSON.stringify({ClusterId:e,SecurityConfigurationName:t}),r=await Ne(n);if((null==r?void 0:r.length)>0)for(const n of r){const a=JSON.stringify({ClusterId:e,RoleArn:n,SecurityConfigurationName:t}),r=await ke(fe,Ae.POST,a);if(r&&r.securityConfigurationName)return r}return await ke(fe,Ae.POST,a)})(null==o?void 0:o.cluster.id,e,a);o.cluster.securityConfiguration=n||t}catch(e){o.cluster.securityConfiguration=t}}E(o.cluster)}})(f))}),[f]);const S=(0,r.useMemo)((()=>null==s?void 0:s.sort(((e,t)=>{const n=e.name,a=t.name;return null==n?void 0:n.localeCompare(a)}))),[s]),A=(0,r.useCallback)((e=>{const t=S.find((t=>t.id===e));let n="";const a=null==t?void 0:t.clusterArn;return a&&U.isValid(a)&&(n=U.fromArnString(a).accountId),n}),[S]),k=(0,r.useCallback)((e=>{const t=S.find((t=>t.id===e)),n=null==t?void 0:t.clusterArn;return n&&U.isValid(n)?n:""}),[S]),N=(0,r.useCallback)((e=>{const t=null==e?void 0:e.id;t&&t===f?(C(t),y(""),w(!0)):(C(t),y(A(t)),w(!1),pt("EMR-Modal-ClusterRow","JupyterLab"))}),[f,A]);return o().createElement(o().Fragment,null,o().createElement("div",{"data-testid":"list-cluster-view"},u&&o().createElement("span",{className:"no-cluster-msg"},(e=>{const t=o().createElement("a",{href:"https://docs.aws.amazon.com/sagemaker/latest/dg/studio-notebooks-configure-discoverability-emr-cluster.html"},"documentation");return e.includes("permission error")?o().createElement("span",{className:"error-msg"},h.permissionError," ",t):o().createElement("span",{className:"error-msg"},e)})(u)),c?o().createElement("span",null,o().createElement(D.CircularProgress,{size:"1rem"})):ut(s)?o().createElement("div",{className:(0,l.cx)(se,"modal-body-container")},n,o().createElement(o().Fragment,null,o().createElement("div",{className:(0,l.cx)(le,"grid-wrapper")},o().createElement(ct,{clustersList:S,selectedClusterId:null!=f?f:"",clusterArn:k(null!=f?f:""),accountId:A(null!=f?f:""),tableConfig:m,clusterManagementListConfig:R,onRowSelect:N,clusterDetails:v})))):o().createElement("div",{className:"no-cluster-msg"},h.noCluster),o().createElement(P,{onCloseModal:t,onConnect:async()=>{try{const n=await ke(Re,Ae.POST,void 0);if("MISSING_AWS_ACCOUNT_ID"===n.CallerAccountId)throw new Error("Failed to get caller account Id");if(!v)throw new Error("Error in getting cluster details");if(!b)throw new Error("Error in getting cluster account Id");const r=v;if(r.clusterAccountId=b,Boolean("IdentityCenter"===(null===(e=r.securityConfiguration)||void 0===e?void 0:e.authentication)))return t(),void xt(n,a,void 0,r,void 0);if(r.clusterAccountId===n.CallerAccountId){if(t(),ft(r))return void wt(a,r);yt(r,n,a)}else t(),bt(n,a,r);pt("EMR-Select-Cluster","JupyterLab")}catch(e){p(e.message)}var e},disabled:x})))},It=b,St=({status:e})=>e===G.Started||e===G.Stopped||e===G.Created?o().createElement("div",null,o().createElement("svg",{width:"10",height:"10"},o().createElement("circle",{cx:"5",cy:"5",r:"5",fill:"green"})),o().createElement("label",{htmlFor:"myInput"}," ",e)):o().createElement("div",null,o().createElement("label",{htmlFor:"myInput"},e)),At=l.css`
  flex-direction: column;
  margin: 0 0 8px 8px;
  flex: 1 0 auto;
  width: 33%;
`,kt=I;var Nt=n(4439),Tt=n.n(Nt);const Mt=I,Lt=({applicationData:e})=>{const t=null==e?void 0:e.tags;return Tt().isEmpty(t)?o().createElement("div",null,Mt.NoTags):o().createElement(o().Fragment,null,Object.entries(t).map((([e,t])=>o().createElement("div",{className:ue,key:e},e,": ",t))))},Dt=I,Pt=({applicationData:e})=>e&&o().createElement(o().Fragment,null,o().createElement("div",{className:At},o().createElement("h4",null,Dt.Overview),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.architecture;return t?`${kt.Architecture}: ${t}`:`${kt.Architecture}: ${kt.NotAvailable}`})(e)),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.releaseLabel;return t?`${kt.ReleaseLabel}: ${t}`:`${kt.ReleaseLabel}: ${kt.NotAvailable}`})(e)),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.livyEndpointEnabled;return"True"===t?`${kt.InteractiveLivyEndpoint}: Enabled`:"False"===t?`${kt.InteractiveLivyEndpoint}: Disabled`:`${kt.InteractiveLivyEndpoint}: ${kt.NotAvailable}`})(e))),o().createElement("div",{className:At},o().createElement("h4",null,Dt.MaximumCapacity),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.maximumCapacityCpu;return t?`${kt.Cpu}: ${t}`:`${kt.Cpu}: ${kt.NotAvailable}`})(e)),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.maximumCapacityMemory;return t?`${kt.Memory}: ${t}`:`${kt.Memory}: ${kt.NotAvailable}`})(e)),o().createElement("div",{className:ue},(e=>{const t=null==e?void 0:e.maximumCapacityDisk;return t?`${kt.Disk}: ${t}`:`${kt.Disk}: ${kt.NotAvailable}`})(e))),o().createElement("div",{className:At},o().createElement("h4",null,Dt.Tags),o().createElement(Lt,{applicationData:e}))),Ut=h,jt=o().createElement("div",{className:ae},o().createElement("p",{className:oe},Ut.noResultsMatchingFilters)),_t=({applicationsList:e,tableConfig:t,applicationManagementListConfig:n,selectedApplicationId:a,applicationArn:r,accountId:s,onRowSelect:l,applicationDetails:i,applicationDetailsLoading:c,...d})=>o().createElement(ne,{...d,tableConfig:t,showIcon:!0,dataList:e,selectedId:a,columnConfig:n,isLoading:c,noResultsView:jt,onRowSelect:l,expandedView:c?o().createElement("span",null,o().createElement(D.CircularProgress,{size:"1rem"})):o().createElement(Pt,{applicationData:i})}),$t=l.css`
  &:not(:active) {
    color: var(--jp-ui-font-color2);
  }
`,Ot=l.css`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  color: var(--jp-error-color0);
  background-color: var(--jp-error-color3);
`,Bt=l.css`
  font-size: 12px;
  font-style: normal;
  font-weight: 500;
  line-height: 150%;
  margin: unset;
  flex-grow: 1;
`,Ft=e=>{const[t,n]=(0,r.useState)(!1),{error:a}=e;return(0,r.useEffect)((()=>{n(!1)}),[a]),a&&!t?o().createElement("div",{className:Ot},o().createElement("p",{className:Bt},a),o().createElement(D.IconButton,{sx:{padding:"4px",color:"inherit"},onClick:()=>{n(!0)}},o().createElement(N.closeIcon.react,{elementPosition:"center",tag:"span"}))):null},zt=e=>{const{onCloseModal:t,header:n,app:a}=e,[s,i]=(0,r.useState)([]),[c,d]=(0,r.useState)(!1),[u,p]=(0,r.useState)(""),[h,E]=(0,r.useState)(void 0),[f,C]=(0,r.useState)(!1),[b,y]=(0,r.useState)(),[I,S]=(0,r.useState)(""),[A,k]=(0,r.useState)(!0),N=[{dataKey:g.name,label:It.name,disableSort:!0,cellRenderer:({row:e})=>null==e?void 0:e.name},{dataKey:g.id,label:It.id,disableSort:!0,cellRenderer:({row:e})=>null==e?void 0:e.id},{dataKey:g.status,label:It.status,disableSort:!0,cellRenderer:({row:e})=>o().createElement(St,{status:e.status})},{dataKey:g.creationDateTime,label:It.creationTime,disableSort:!0,cellRenderer:({row:e})=>{var t;return null===(t=null==e?void 0:e.createdAt)||void 0===t?void 0:t.split("+")[0].split(".")[0]}},{dataKey:g.arn,label:It.accountId,disableSort:!0,cellRenderer:({row:e})=>{if(null==e?void 0:e.arn)return U.fromArnString(e.arn).accountId}}],T=async(e="",t)=>{do{const n=JSON.stringify({states:[G.Started,G.Created,G.Stopped],...e&&{nextToken:e},roleArn:t}),a=await ke("/aws/sagemaker/api/emr-serverless/list-applications",Ae.POST,n);a&&a.applications&&i((e=>[...new Map([...e,...a.applications].map((e=>[e.id,e]))).values()])),e=null==a?void 0:a.nextToken,a.code||a.errorMessage?(d(!1),a.code===v?p(w):p(`${a.code}: ${a.errorMessage}`)):p("")}while(dt(e))};(0,r.useEffect)((()=>{(async(e="")=>{var t;try{d(!0);const e=JSON.stringify({}),n=await ke(Re,Ae.POST,e);if(await T(),(null===(t=null==n?void 0:n.EmrAssumableRoleArns)||void 0===t?void 0:t.length)>0)for(const e of n.EmrAssumableRoleArns)await T("",e);d(!1)}catch(e){d(!1),p(e.message)}})()}),[]);const M=(0,r.useMemo)((()=>null==s?void 0:s.sort(((e,t)=>{const n=e.name,a=t.name;return null==n?void 0:n.localeCompare(a)}))),[s]);(0,r.useEffect)((()=>{b&&E((async e=>{C(!0),k(!0);const t=s.find((t=>t.id===e));let n="";const a=null==t?void 0:t.arn;a&&U.isValid(a)&&(n=U.fromArnString(a).accountId);const r=await Pe(e,n);E(r.application),r.code||r.errorMessage?(C(!1),r.code===v?p(R):p(`${r.code}: ${r.errorMessage}`)):p(""),C(!1),k(!1)})(b))}),[b]);const L=(0,r.useCallback)((e=>{const t=M.find((t=>t.id===e));let n="";const a=null==t?void 0:t.arn;return a&&U.isValid(a)&&(n=U.fromArnString(a).accountId),n}),[M]),j=(0,r.useCallback)((e=>{const t=M.find((t=>t.id===e)),n=null==t?void 0:t.arn;return n&&U.isValid(n)?n:""}),[M]),_=(0,r.useCallback)((e=>{const t=null==e?void 0:e.id;t&&t===b?(y(t),S(""),k(!0)):(y(t),S(L(t)),k(!1))}),[b,L]);return o().createElement(o().Fragment,null,o().createElement("div",{"data-testid":"list-serverless-applications-view"},u&&o().createElement(Ft,{error:u}),c?o().createElement("span",null,o().createElement(D.CircularProgress,{size:"1rem"})):ut(s)?o().createElement("div",{className:(0,l.cx)(se,"modal-body-container")},n,o().createElement(o().Fragment,null,o().createElement("div",{className:(0,l.cx)(le,"grid-wrapper")},o().createElement(_t,{applicationsList:M,selectedApplicationId:null!=b?b:"",applicationArn:j(null!=b?b:""),accountId:L(null!=b?b:""),tableConfig:m,applicationManagementListConfig:N,onRowSelect:_,applicationDetails:h,applicationDetailsLoading:f})))):o().createElement("div",{className:"no-cluster-msg"},x),o().createElement(P,{onCloseModal:t,onConnect:async()=>{try{const e=await ke(Re,Ae.POST);if("MISSING_AWS_ACCOUNT_ID"===e.CallerAccountId)throw new Error("Failed to get caller account Id");if(!h)throw new Error("Error in getting serverless application details");if(!I)throw new Error("Error in getting serverless application account Id");I!==e.CallerAccountId?(t(),bt(e,a,void 0,h)):(t(),xt(e,a,void 0,void 0,h))}catch(e){p(e.message)}},disabled:A})))};function Gt(e){const{children:t,value:n,index:a,...r}=e;return o().createElement("div",{role:"tabpanel",hidden:n!==a,...r},n===a&&o().createElement("div",null,t))}function Ht(e){const[t,n]=o().useState(0);return o().createElement("div",null,o().createElement("div",null,o().createElement(D.Tabs,{value:t,onChange:(e,t)=>{n(t)}},o().createElement(D.Tab,{className:(0,l.cx)($t),label:y}),o().createElement(D.Tab,{className:(0,l.cx)($t),label:h.tabName}))),o().createElement(Gt,{value:t,index:0},o().createElement(zt,{onCloseModal:e.onCloseModal,header:e.header,app:e.app})),o().createElement(Gt,{value:t,index:1},o().createElement(Rt,{onCloseModal:e.onCloseModal,header:e.header,app:e.app})))}class Jt{constructor(e,t,n){this.disposeDialog=e,this.header=t,this.app=n}render(){return o().createElement(r.Suspense,{fallback:null},o().createElement(Ht,{onCloseModal:this.disposeDialog,app:this.app,header:this.header}))}}const Vt=(e,t,n)=>new Jt(e,t,n);var Kt;!function(e){e["us-east-1"]="us-east-1",e["us-east-2"]="us-east-2",e["us-west-1"]="us-west-1",e["us-west-2"]="us-west-2",e["us-gov-west-1"]="us-gov-west-1",e["us-gov-east-1"]="us-gov-east-1",e["us-iso-east-1"]="us-iso-east-1",e["us-isob-east-1"]="us-isob-east-1",e["ca-central-1"]="ca-central-1",e["eu-west-1"]="eu-west-1",e["eu-west-2"]="eu-west-2",e["eu-west-3"]="eu-west-3",e["eu-central-1"]="eu-central-1",e["eu-north-1"]="eu-north-1",e["eu-south-1"]="eu-south-1",e["ap-east-1"]="ap-east-1",e["ap-south-1"]="ap-south-1",e["ap-southeast-1"]="ap-southeast-1",e["ap-southeast-2"]="ap-southeast-2",e["ap-southeast-3"]="ap-southeast-3",e["ap-northeast-3"]="ap-northeast-3",e["ap-northeast-1"]="ap-northeast-1",e["ap-northeast-2"]="ap-northeast-2",e["sa-east-1"]="sa-east-1",e["af-south-1"]="af-south-1",e["cn-north-1"]="cn-north-1",e["cn-northwest-1"]="cn-northwest-1",e["me-south-1"]="me-south-1"}(Kt||(Kt={}));const Wt=e=>(e=>e===Kt["cn-north-1"]||e===Kt["cn-northwest-1"])(e)?"https://docs.amazonaws.cn":"https://docs.aws.amazon.com",qt=({clusterName:e})=>{const t=Wt(Kt["us-west-2"]);return o().createElement("div",{className:(0,l.cx)(Je.ModalHeader,"list-cluster-modal-header")},(()=>{let t;if(e){const n=o().createElement("span",{className:Je.ConnectCluster},e),a=`${h.widgetConnected} `,r=` ${h.connectedWidgetHeader} `;t=o().createElement("div",{className:(0,l.cx)(Je.ClusterDescription,"list-cluster-description")},a,n,r)}else t=`${h.widgetHeader} `;return t})(),o().createElement($e,{href:`${t}/sagemaker/latest/dg/studio-notebooks-emr-cluster.html`,type:_e.External},h.learnMore))};class Xt extends s.ReactWidget{constructor(e,t){super(),this.updateConnectedCluster=e=>{this._connectedCluster=e,this.update()},this.getToolTip=()=>this._connectedCluster?`${h.widgetConnected} ${this._connectedCluster.name} cluster`:h.defaultTooltip,this.clickHandler=async()=>{let e={};const t=()=>e&&e.resolve();e=new s.Dialog({title:o().createElement(L,{heading:h.widgetTitle,shouldDisplayCloseButton:!0,onClickCloseButton:t,className:"list-cluster-modal-header"}),body:Vt(t,this.listClusterHeader(),this._appContext).render()}),e.handleEvent=t=>{"keydown"===t.type&&(({keyboardEvent:e,onEscape:t,onShiftTab:n,onShiftEnter:a,onTab:r,onEnter:o})=>{const{key:s,shiftKey:l}=e;l?s===A.tab&&n?n():s===A.enter&&a&&a():s===A.tab&&r?r():s===A.enter&&o?o():s===A.escape&&t&&t()})({keyboardEvent:t,onEscape:()=>e.reject()})},e.addClass((0,l.cx)(M.ModalBase,M.Footer,M.DialogClassname)),e.launch()},this.listClusterHeader=()=>{var e;return o().createElement(qt,{clusterName:null===(e=this._connectedCluster)||void 0===e?void 0:e.name})},this._selectedCluster=null,this._appContext=t,this._connectedCluster=null,this._kernelId=null}get kernelId(){return this._kernelId}get selectedCluster(){return this._selectedCluster}updateKernel(e){this._kernelId!==e&&(this._kernelId=e,this.kernelId&&this.update())}render(){return o().createElement(S,{handleClick:this.clickHandler,tooltip:this.getToolTip()})}}const Yt=e=>null!=e,Zt=async(e,t,n=!0)=>new Promise((async(r,o)=>{if(t){const s=t.content,l=s.model,i=t.context.sessionContext,{metadata:c}=l.sharedModel.toJSON(),d={cell_type:"code",metadata:c,source:e},u=s.activeCell,p=u?s.activeCellIndex:0;if(l.sharedModel.insertCell(p,d),s.activeCellIndex=p,n)try{await a.NotebookActions.run(s,i)}catch(e){o(e)}const m=[];for(const e of u.outputArea.node.children)m.push(e.innerHTML);r({html:m,cell:u})}o("No notebook panel")})),Qt=e=>{const t=e.shell.widgets("main");let n=t.next().value;for(;n;){if(n.hasClass("jp-NotebookPanel")&&n.isVisible)return n;n=t.next().value}return null};var en=n(7704),tn=n.n(en);const nn=e=>{const t=h.presignedURL.sshTunnelLink;return e?o().createElement($e,{href:e,type:_e.External,hideExternalIcon:!0},t):o().createElement("span",{className:(0,l.cx)("PresignedURLErrorText",Je.PresignedURLErrorText)},t)},an=()=>o().createElement($e,{href:"https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-ssh-tunnel.html",type:_e.External},h.presignedURL.viewTheGuide),rn=({sshTunnelLink:e,error:t})=>o().createElement(o().Fragment,null,(()=>{switch(t){case Ve:return o().createElement("span",{className:(0,l.cx)("PresignedURLErrorText",Je.PresignedURLErrorText)},o().createElement("b",null,h.presignedURL.error),h.presignedURL.clusterNotReady);case Ke:return o().createElement("span",{className:(0,l.cx)("PresignedURLErrorText",Je.PresignedURLErrorText)},o().createElement("b",null,h.presignedURL.error),h.presignedURL.clusterNotConnected);case We:return(e=>o().createElement("span",{className:(0,l.cx)("PresignedURLErrorText",Je.PresignedURLErrorText)},o().createElement("b",null,h.presignedURL.error),h.presignedURL.clusterNotCompatible,nn(e),h.presignedURL.or,an()))(e);default:return(e=>o().createElement("span",null,o().createElement("span",{className:(0,l.cx)("PresignedURLErrorText",Je.PresignedURLErrorText)},o().createElement("b",null,h.presignedURL.error),h.presignedURL.sparkUIError),nn(e),o().createElement("span",{className:(0,l.cx)("PresignedURLErrorText",Je.PresignedURLErrorText)},h.presignedURL.or),an()))(e)}})()),on=(e,t)=>{var n;for(let a=0;a<e.childNodes.length;a++)if(null===(n=e.childNodes[a].textContent)||void 0===n?void 0:n.includes(t))return a;return-1},sn=e=>{try{let t=e.lastElementChild;for(;t;)e.removeChild(t),t=e.lastElementChild}catch(e){}},ln="YARN Application ID",cn="Spark UI",dn="--cluster-id",un="--assumable-role-arn",pn="%info",mn="%configure",gn={childList:!0,subtree:!0};class vn{constructor(e){this.trackedPanels=new Set,this.trackedCells=new Set,this.notebookTracker=e,this.triggers=[hn,pn,mn],this.kernelChanged=!1,this.lastConnectedClusterId=null,this.lastConnectedAccountId=void 0}run(){this.notebookTracker.currentChanged.connect(((e,t)=>{t&&(this.isTrackedPanel(t)||(t.context.sessionContext.kernelChanged.connect(((e,t)=>{this.kernelChanged=!0})),t.context.sessionContext.iopubMessage.connect(((e,n)=>{!this.isTrackedPanel(t)||this.kernelChanged?(n?(this.trackPanel(t),this.handleExistingSparkWidgetsOnPanelLoad(t)):this.stopTrackingPanel(t),this.kernelChanged=!1):this.isTrackedPanel(t)&&this.checkMessageForEmrConnectAndInject(n,t)}))))}))}isTrackedCell(e){return this.trackedCells.has(e)}trackCell(e){this.trackedCells.add(e)}stopTrackingCell(e){this.trackedCells.delete(e)}isTrackedPanel(e){return this.trackedPanels.has(e)}trackPanel(e){this.trackedPanels.add(e)}stopTrackingPanel(e){this.trackedPanels.delete(e)}handleExistingSparkWidgetsOnPanelLoad(e){e.revealed.then((()=>{const t=new RegExp(this.triggers.join("|"));((e,t)=>{var n;const a=null===(n=null==e?void 0:e.content)||void 0===n?void 0:n.widgets;return null==a?void 0:a.filter((e=>{const n=e.model.sharedModel;return t.test(n.source)}))})(e,t).forEach((e=>{if(this.containsSparkMagicTable(e.outputArea.node)){const t=e.model.sharedModel,n=this.getClusterId(t.source),a=this.getAccountId(t.source);this.injectPresignedURL(e,n,a)}else this.injectPresignedURLOnTableRender(e)}))}))}checkMessageForEmrConnectAndInject(e,t){if("execute_input"!==e.header.msg_type)return;const n=e.content.code;var a;this.codeContainsTrigger(n)&&(a=n,t.content.widgets.filter((e=>e.model.sharedModel.source.includes(a)))).forEach((e=>{this.injectPresignedURLOnTableRender(e)}))}codeContainsTrigger(e){const t=this.triggers.filter((t=>e.includes(t)));return ut(t)}getParameterFromEmrConnectCommand(e,t){const n=e.split(" "),a=n.indexOf(t);if(!(-1===a||a+1>n.length-1))return n[a+1]}getClusterId(e){return e&&e.includes(dn)?this.getParameterFromEmrConnectCommand(e,dn)||null:this.lastConnectedClusterId}getAccountId(e){if(!e)return this.lastConnectedAccountId;if(e.includes(pn))return this.lastConnectedAccountId;if(e.includes(un)){const t=this.getParameterFromEmrConnectCommand(e,un);return void 0!==t?U.fromArnString(t).accountId:void 0}}getSparkMagicTableBodyNodes(e){const t=Array.from(e.getElementsByTagName("tbody"));return ut(t)?t.filter((e=>this.containsSparkMagicTable(e))):[]}containsSparkMagicTable(e){var t;return(null===(t=e.textContent)||void 0===t?void 0:t.includes(ln))&&e.textContent.includes(cn)}isSparkUIErrorRow(e){var t;return e instanceof HTMLTableRowElement&&(null===(t=e.textContent)||void 0===t?void 0:t.includes(h.presignedURL.error))||!1}injectSparkUIErrorIntoNextTableRow(e,t,n,a){var r;const s=this.isSparkUIErrorRow(t.nextSibling);if(null===a)return void(s&&(null===(r=t.nextSibling)||void 0===r||r.remove()));let l;if(s?(l=t.nextSibling,sn(l)):l=((e,t)=>{let n=1,a=!1;for(let r=1;r<e.childNodes.length;r++)if(e.childNodes[r].isSameNode(t)){n=r,a=!0;break}if(!a)return null;const r=n+1<e.childNodes.length?n+1:-1;return e.insertRow(r)})(e,t),!l)return;const i=l.insertCell(),c=t.childElementCount;i.setAttribute("colspan",c.toString()),i.style.textAlign="left",i.style.background="#212121";const d=o().createElement(rn,{sshTunnelLink:n,error:a});tn().render(d,i)}injectPresignedURL(e,t,n){var a;const r=e.outputArea.node,s=e.model.sharedModel,l=this.getSparkMagicTableBodyNodes(r);if(!ut(l))return!1;if(s.source.includes(mn)&&l.length<2)return!1;for(let e=0;e<l.length;e++){const r=l[e],s=r.firstChild,i=on(s,cn),c=on(s,"Driver log"),d=on(s,ln),u=s.getElementsByTagName("th")[c];if(s.removeChild(u),-1===i||-1===d)break;for(let e=1;e<r.childNodes.length;e++){const s=r.childNodes[e],l=s.childNodes[i];s.childNodes[c].remove();const u=null===(a=l.getElementsByTagName("a")[0])||void 0===a?void 0:a.href;l.hasChildNodes()&&sn(l);const p=s.childNodes[d].textContent||void 0,m=document.createElement("div");l.appendChild(m);const g=o().createElement(qe,{clusterId:t,applicationId:p,onError:e=>this.injectSparkUIErrorIntoNextTableRow(r,s,u,e),accountId:n});tn().render(g,m)}}return!0}injectPresignedURLOnTableRender(e){this.isTrackedCell(e)||(this.trackCell(e),new MutationObserver(((t,n)=>{for(const a of t)if("childList"===a.type)try{const t=e.model.sharedModel,a=this.getClusterId(t.source),r=this.getAccountId(t.source);if(this.injectPresignedURL(e,a,r)){this.stopTrackingCell(e),n.disconnect(),this.lastConnectedClusterId=a,this.lastConnectedAccountId=r;break}}catch(t){this.stopTrackingCell(e),n.disconnect()}})).observe(e.outputArea.node,gn))}}const hn="%sm_analytics emr connect",En=h,fn={id:"@sagemaker-studio:EmrCluster",autoStart:!0,optional:[a.INotebookTracker],activate:async(e,t)=>{null==t||new vn(t).run(),e.docRegistry.addWidgetExtension("Notebook",new Cn(e)),e.commands.addCommand(vt.emrConnect.id,{label:e=>En.connectCommand.label,isEnabled:()=>!0,isVisible:()=>!0,caption:()=>En.connectCommand.caption,execute:async t=>{try{const{clusterId:n,authType:a,language:r,crossAccountArn:o,executionRoleArn:s,notebookPanelToInjectCommandInto:l}=t,i="%load_ext sagemaker_studio_analytics_extension.magics",c=Yt(r)?`--language ${r}`:"",d=Yt(o)?`--assumable-role-arn ${o}`:"",u=Yt(s)?`--emr-execution-role-arn ${s}`:"",p=`${i}\n${hn} --verify-certificate False --cluster-id ${n} --auth-type ${a} ${c} ${d} ${u}`,m=l||Qt(e);await Zt(p,m)}catch(e){throw e.message,e}}}),e.commands.addCommand(vt.emrServerlessConnect.id,{label:e=>En.connectCommand.label,isEnabled:()=>!0,isVisible:()=>!0,caption:()=>En.connectCommand.caption,execute:async t=>{try{const{serverlessApplicationId:n,language:a,assumableRoleArn:r,executionRoleArn:o,notebookPanelToInjectCommandInto:s}=t,l="%load_ext sagemaker_studio_analytics_extension.magics",i=Yt(a)?` --language ${a}`:"",c=`${l}\n%sm_analytics emr-serverless connect --application-id ${n}${i}${Yt(r)?` --assumable-role-arn ${r}`:""}${Yt(o)?` --emr-execution-role-arn ${o}`:""}`,d=s||Qt(e);await Zt(c,d)}catch(e){throw e.message,e}}})}};class Cn{constructor(e){this.appContext=e}createNew(e,t){const n=(a=e.sessionContext,r=this.appContext,new Xt(a,r));var a,r;return e.context.sessionContext.kernelChanged.connect((e=>{var t;const a=null===(t=e.session)||void 0===t?void 0:t.kernel;e.iopubMessage.connect(((e,t)=>{((e,t,n,a)=>{if(n)try{if(e.content.text){const{isConnSuccess:t,clusterId:r}=(e=>{let t,n=!1;if(e.content.text){const a=JSON.parse(e.content.text);if("sagemaker-analytics"!==a.namespace)return{};t=a.cluster_id,n=a.success}return{isConnSuccess:n,clusterId:t}})(e);t&&n.id===r&&a(n)}}catch(e){return}})(t,0,n.selectedCluster,n.updateConnectedCluster)})),a&&a.spec.then((e=>{e&&e.metadata&&n.updateKernel(a.id)})),n.updateKernel(null)})),e.toolbar.insertBefore("kernelName","emrCluster",n),n}}var bn=n(8019);const yn={errorTitle:"Unable to connect to EMR cluster/EMR serverless application",defaultErrorMessage:"Something went wrong when connecting to the EMR cluster/EMR serverless application.",invalidRequestErrorMessage:"A request to attach the EMR cluster/EMR serverless application to the notebook is invalid.",invalidClusterErrorMessage:"EMR cluster ID is invalid."},xn={invalidApplicationErrorMessage:"EMR Serverless Application ID is invalid."};let wn=!1;const Rn=async e=>(0,s.showErrorMessage)(yn.errorTitle,{message:e}),In=async e=>{const t=await e.commands.execute("notebook:create-new");await new Promise((e=>{t.sessionContext.kernelChanged.connect(((t,n)=>{e(n)}))})),await(2e3,new Promise((e=>setTimeout(e,2e3))))},Sn=[fn,{id:"@sagemaker-studio:DeepLinking",requires:[bn.IRouter],autoStart:!0,activate:async(e,t)=>{const{commands:n}=e,a="emrCluster:open-notebook-for-deeplinking";n.addCommand(a,{execute:()=>(async(e,t)=>{if(!wn)try{const{search:n}=e.current;if(!n)return void await Rn(yn.invalidRequestErrorMessage);t.restored.then((async()=>{const{clusterId:e,applicationId:a,accountId:r}=he.URLExt.queryStringToObject(n);if(!e&&!a)return void await Rn(yn.invalidRequestErrorMessage);const o=await ke(Re,Ae.POST,void 0);o&&!(null==o?void 0:o.error)?e?await(async(e,t,n,a)=>{const r=await De(e,n);if(!r||!(null==r?void 0:r.cluster))return void await Rn(yn.invalidClusterErrorMessage);const o=r.cluster;await In(t),n?(o.clusterAccountId=n,bt(a,t,o)):(o.clusterAccountId=a.CallerAccountId,yt(o,a,t))})(e,t,r,o):a&&await(async(e,t,n,a)=>{const r=await Pe(e,n);if(!r||!(null==r?void 0:r.application))return void await Rn(xn.invalidApplicationErrorMessage);const o=r.application;await In(t),n?bt(a,t,void 0,o):xt(a,t,void 0,void 0,o)})(a,t,r,o):await Rn(h.fetchEmrRolesError)}))}catch(e){return void await Rn(yn.defaultErrorMessage)}finally{wn=!0}})(t,e)}),t.register({command:a,pattern:new RegExp("[?]command=attach-emr-to-notebook"),rank:10})}}]}}]);