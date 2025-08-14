"use strict";(globalThis.webpackChunksuperset=globalThis.webpackChunksuperset||[]).push([[3807],{3807:(e,t,n)=>{n.r(t),n.d(t,{DashboardPage:()=>he,DashboardPageIdContext:()=>le,default:()=>pe});var a=n(2445),s=n(96540),i=n(17437),r=n(61574),o=n(16844),l=n(95579),d=n(61225),c=n(10381),u=n(5261),h=n(52879),p=n(71478),f=n(52123),b=n(34975),v=n(5007),g=n(92008),m=n(68921),y=n(62221),S=n(27023),w=n(32132),E=n(72173),x=n(39093),C=n(82960),I=n(5556),D=n.n(I),F=n(44344),_=n(38708),$=n(49588);function O(e){return Object.values(e).reduce(((e,t)=>(t&&t.type===$.oT&&t.meta&&t.meta.chartId&&e.push(t.meta.chartId),e)),[])}var k=n(4881),M=n(35700),T=n(35839),j=n(37725);const U=[$.oT,$.xY,$.rG];function z(e){return!Object.values(e).some((({type:e})=>e&&U.includes(e)))}var R=n(47986);const A={actions:D().shape({addSliceToDashboard:D().func.isRequired,removeSliceFromDashboard:D().func.isRequired,triggerQuery:D().func.isRequired,logEvent:D().func.isRequired,clearDataMaskState:D().func.isRequired}).isRequired,dashboardId:D().number.isRequired,editMode:D().bool,isPublished:D().bool,hasUnsavedChanges:D().bool,slices:D().objectOf(k.VE).isRequired,activeFilters:D().object.isRequired,chartConfiguration:D().object,datasources:D().object.isRequired,ownDataCharts:D().object.isRequired,layout:D().object.isRequired,impressionId:D().string.isRequired,timeout:D().number,userId:D().string,children:D().node};class P extends s.PureComponent{static onBeforeUnload(e){e?window.addEventListener("beforeunload",P.unload):window.removeEventListener("beforeunload",P.unload)}static unload(){const e=(0,l.t)("You have unsaved changes.");return window.event.returnValue=e,e}constructor(e){var t,n;super(e),this.appliedFilters=null!=(t=e.activeFilters)?t:{},this.appliedOwnDataCharts=null!=(n=e.ownDataCharts)?n:{},this.onVisibilityChange=this.onVisibilityChange.bind(this)}componentDidMount(){const e=(0,_.Ay)(),{editMode:t,isPublished:n,layout:a}=this.props,s={is_soft_navigation:M.Vy.timeOriginOffset>0,is_edit_mode:t,mount_duration:M.Vy.getTimestamp(),is_empty:z(a),is_published:n,bootstrap_data_length:e.length},i=(0,j.A)();i&&(s.target_id=i),this.props.actions.logEvent(M.es,s),"hidden"===document.visibilityState&&(this.visibilityEventData={start_offset:M.Vy.getTimestamp(),ts:(new Date).getTime()}),window.addEventListener("visibilitychange",this.onVisibilityChange),this.applyCharts()}componentDidUpdate(){this.applyCharts()}UNSAFE_componentWillReceiveProps(e){const t=O(this.props.layout),n=O(e.layout);this.props.dashboardId===e.dashboardId&&(t.length<n.length?n.filter((e=>-1===t.indexOf(e))).forEach((t=>{return this.props.actions.addSliceToDashboard(t,(n=e.layout,a=t,Object.values(n).find((e=>e&&e.type===$.oT&&e.meta&&e.meta.chartId===a))));var n,a})):t.length>n.length&&t.filter((e=>-1===n.indexOf(e))).forEach((e=>this.props.actions.removeSliceFromDashboard(e))))}applyCharts(){const{activeFilters:e,ownDataCharts:t,chartConfiguration:n,hasUnsavedChanges:a,editMode:s}=this.props,{appliedFilters:i,appliedOwnDataCharts:r}=this;n&&(s||(0,T.r$)(r,t,{ignoreUndefined:!0})&&(0,T.r$)(i,e,{ignoreUndefined:!0})||this.applyFilters(),a?P.onBeforeUnload(!0):P.onBeforeUnload(!1))}componentWillUnmount(){window.removeEventListener("visibilitychange",this.onVisibilityChange),this.props.actions.clearDataMaskState()}onVisibilityChange(){if("hidden"===document.visibilityState)this.visibilityEventData={start_offset:M.Vy.getTimestamp(),ts:(new Date).getTime()};else if("visible"===document.visibilityState){const e=this.visibilityEventData.start_offset;this.props.actions.logEvent(M.Xj,{...this.visibilityEventData,duration:M.Vy.getTimestamp()-e})}}applyFilters(){const{appliedFilters:e}=this,{activeFilters:t,ownDataCharts:n,slices:a}=this.props,s=Object.keys(t),i=Object.keys(e),r=new Set(s.concat(i)),o=((e,t)=>{const n=Object.keys(e),a=Object.keys(t),s=(i=n,r=a,[...i.filter((e=>!r.includes(e))),...r.filter((e=>!i.includes(e)))]).filter((n=>e[n]||t[n]));var i,r;return new Set([...n,...a]).forEach((n=>{(0,T.r$)(e[n],t[n])||s.push(n)})),[...new Set(s)]})(n,this.appliedOwnDataCharts);[...r].forEach((n=>{if(!s.includes(n)&&i.includes(n))o.push(...(0,R.z)(n,e[n],a));else if(i.includes(n)){if((0,T.r$)(e[n].values,t[n].values,{ignoreUndefined:!0})||o.push(...(0,R.z)(n,t[n],a)),!(0,T.r$)(e[n].scope,t[n].scope)){const a=(t[n].scope||[]).concat(e[n].scope||[]);o.push(...a)}}else o.push(...(0,R.z)(n,t[n],a))})),this.refreshCharts([...new Set(o)]),this.appliedFilters=t,this.appliedOwnDataCharts=n}refreshCharts(e){e.forEach((e=>{this.props.actions.triggerQuery(!0,e)}))}render(){return this.context.loading?(0,a.Y)(h.R,{}):this.props.children}}P.contextType=F.bf,P.propTypes=A,P.defaultProps={timeout:60,userId:""};const q=P;var L=n(2514),V=n(7735),Y=n(95004);const H=(0,d.Ng)((function(e){var t,n;const{datasources:a,sliceEntities:s,dashboardInfo:i,dashboardState:r,dashboardLayout:o,impressionId:l}=e;return{timeout:null==(t=i.common)||null==(t=t.conf)?void 0:t.SUPERSET_WEBSERVER_TIMEOUT,userId:i.userId,dashboardId:i.id,editMode:r.editMode,isPublished:r.isPublished,hasUnsavedChanges:r.hasUnsavedChanges,datasources:a,chartConfiguration:null==(n=i.metadata)?void 0:n.chart_configuration,slices:s.slices,layout:o.present,impressionId:l}}),(function(e){return{actions:(0,C.zH)({setDatasources:b.nC,clearDataMaskState:Y.V9,addSliceToDashboard:E.ft,removeSliceFromDashboard:E.Hg,triggerQuery:L.triggerQuery,logEvent:V.logEvent},e)}}))(q);var N=n(1208);function W({children:e,themeId:t}){const n=(0,N.w)(),[i,r]=(0,s.useState)(null);return(0,s.useEffect)((()=>{t?(async()=>{try{const e=await n.createDashboardThemeProvider(String(t));r(e)}catch(e){console.error("Failed to load dashboard theme:",e),r(null)}})():r(null)}),[t,n]),t&&i?(0,a.Y)(i.SupersetThemeProvider,{children:e}):(0,a.Y)(a.FK,{children:e})}var B=n(43561);const X=e=>i.AH`
  body {
    h1 {
      font-weight: ${e.fontWeightStrong};
      line-height: 1.4;
      font-size: ${e.fontSizeXXL}px;
      letter-spacing: -0.2px;
      margin-top: ${3*e.sizeUnit}px;
      margin-bottom: ${3*e.sizeUnit}px;
    }

    h2 {
      font-weight: ${e.fontWeightStrong};
      line-height: 1.4;
      font-size: ${e.fontSizeXL}px;
      margin-top: ${3*e.sizeUnit}px;
      margin-bottom: ${2*e.sizeUnit}px;
    }

    h3,
    h4,
    h5,
    h6 {
      font-weight: ${e.fontWeightStrong};
      line-height: 1.4;
      font-size: ${e.fontSizeLG}px;
      letter-spacing: 0.2px;
      margin-top: ${2*e.sizeUnit}px;
      margin-bottom: ${e.sizeUnit}px;
    }
  }
`,K=e=>i.AH`
  .header-title a {
    margin: ${e.sizeUnit/2}px;
    padding: ${e.sizeUnit/2}px;
  }
  .header-controls {
    &,
    &:hover {
      margin-top: ${e.sizeUnit}px;
    }
  }
`,Q=e=>i.AH`
  .ant-dropdown-menu.chart-context-menu {
    min-width: ${43*e.sizeUnit}px;
  }
  .ant-dropdown-menu-submenu.chart-context-submenu {
    max-width: ${60*e.sizeUnit}px;
    min-width: ${40*e.sizeUnit}px;
  }
`,G=e=>i.AH`
  a,
  .ant-tabs-tabpane,
  .ant-tabs-tab-btn,
  .superset-button,
  .superset-button.ant-dropdown-trigger,
  .header-controls span {
    &:focus-visible {
      box-shadow: 0 0 0 2px ${e.colorPrimaryText};
      border-radius: ${e.borderRadius}px;
      outline: none;
      text-decoration: none;
    }
    &:not(
      .superset-button,
      .ant-menu-item,
      a,
      .fave-unfave-icon,
      .ant-tabs-tabpane,
      .header-controls span
    ) {
      &:focus-visible {
        padding: ${e.sizeUnit/2}px;
      }
    }
  }
`;var J=n(71086),Z=n.n(J),ee=n(44383),te=n.n(ee),ne=n(55556);const ae={},se=()=>{const e=(0,y.Gq)(y.Hh.DashboardExploreContext,{});return Z()(e,(e=>!e.isRedundant))},ie=(e,t)=>{const n=se();(0,y.SO)(y.Hh.DashboardExploreContext,{...n,[e]:{...t,dashboardPageId:e}})},re=(0,c.Mz)([e=>e.dashboardInfo.metadata,e=>e.dashboardInfo.id,e=>{var t;return null==(t=e.dashboardState)?void 0:t.colorScheme},e=>{var t;return null==(t=e.nativeFilters)?void 0:t.filters},e=>e.dataMask,e=>{var t;return(null==(t=e.dashboardState)?void 0:t.sliceIds)||[]}],((e,t,n,a,s,i)=>{const r=Object.keys(a).reduce(((e,t)=>(e[t]=te()(a[t],["chartsInScope"]),e)),{}),o=(0,g.R)({chartConfiguration:(null==e?void 0:e.chart_configuration)||ae,nativeFilters:a,dataMask:s,allSliceIds:i});return{labelsColor:(null==e?void 0:e.label_colors)||ae,labelsColorMap:(null==e?void 0:e.map_label_colors)||ae,sharedLabelsColors:(0,ne.ik)(null==e?void 0:e.shared_label_colors),colorScheme:n,chartConfiguration:(null==e?void 0:e.chart_configuration)||ae,nativeFilters:r,dataMask:s,dashboardId:t,filterBoxFilters:(0,m.ug)(),activeFilters:o}})),oe=({dashboardPageId:e})=>{const t=(0,d.d4)(re);return(0,s.useEffect)((()=>(ie(e,t),()=>{ie(e,{...t,isRedundant:!0})})),[t,e]),null},le=(0,s.createContext)(""),de=(0,s.lazy)((()=>Promise.all([n.e(9467),n.e(2120),n.e(8503),n.e(683),n.e(2219),n.e(2656),n.e(8513),n.e(240),n.e(5463),n.e(7688),n.e(9074),n.e(5755),n.e(7252),n.e(8873),n.e(960),n.e(5026)]).then(n.bind(n,29617)))),ce=(0,c.Mz)((e=>e.dataMask),(e=>(0,g.W)(e,"ownState"))),ue=(0,c.Mz)([e=>{var t;return null==(t=e.dashboardInfo.metadata)?void 0:t.chart_configuration},e=>e.nativeFilters.filters,e=>e.dataMask,e=>e.dashboardState.sliceIds],((e,t,n,a)=>({...(0,m.ug)(),...(0,g.R)({chartConfiguration:e,nativeFilters:t,dataMask:n,allSliceIds:a})}))),he=({idOrSlug:e})=>{var t;const n=(0,o.DP)(),c=(0,d.wA)(),g=(0,r.W6)(),m=(0,s.useMemo)((()=>(0,B.Ak)()),[]),C=(0,d.d4)((({dashboardInfo:e})=>e&&Object.keys(e).length>0)),I=(0,d.d4)((e=>e.dashboardInfo.theme)),{addDangerToast:D}=(0,u.Yf)(),{result:F,error:_}=(0,p.MZ)(e),{result:$,error:O}=(0,p.DT)(e),{result:k,error:M,status:T}=(0,p.RO)(e),j=(0,s.useRef)(!1),U=_||O,z=Boolean(F&&$),{dashboard_title:R,id:A=0}=F||{},P=(0,d.d4)((e=>e.dashboardState.css))||(null==F?void 0:F.css);(0,s.useEffect)((()=>{const e=()=>{const e=se();(0,y.SO)(y.Hh.DashboardExploreContext,{...e,[m]:{...e[m],isRedundant:!0}})};return window.addEventListener("beforeunload",e),()=>{window.removeEventListener("beforeunload",e)}}),[m]),(0,s.useEffect)((()=>{c((0,E.wh)(T))}),[c,T]),(0,s.useEffect)((()=>{A&&async function(){const e=(0,w.P3)(S.vX.permalinkKey),t=(0,w.P3)(S.vX.nativeFiltersKey),n=(0,w.P3)(S.vX.nativeFilters);let a,s=t||{};if(e){const t=await(0,x.J)(e);t&&({dataMask:s,activeTabs:a}=t.state)}else t&&(s=await(0,x.I8)(A,t));n&&(s=n),z&&(j.current||(j.current=!0),c((0,f.M)({history:g,dashboard:F,charts:$,activeTabs:a,dataMask:s})))}()}),[z]),(0,s.useEffect)((()=>(R&&(document.title=R),()=>{document.title="Superset"})),[R]),(0,s.useEffect)((()=>"string"==typeof P?(0,v.A)(P):()=>{}),[P]),(0,s.useEffect)((()=>{M?D((0,l.t)("Error loading chart datasources. Filters may not work correctly.")):c((0,b.nC)(k))}),[D,k,M,c]);const q=(0,d.d4)(ce),L=(0,d.d4)(ue);if(U)throw U;const V=(0,s.useMemo)((()=>[i.AH`
  .filter-card-tooltip {
    &.ant-tooltip-placement-bottom {
      padding-top: 0;
      & .ant-tooltip-arrow {
        top: -13px;
      }
    }
  }
`,X(n),Q(n),G(n),K(n)]),[n]);if(U)throw U;const Y=(0,s.useMemo)((()=>(0,a.Y)(de,{})),[]);return(0,a.FD)(a.FK,{children:[(0,a.Y)(i.mL,{styles:V}),z&&C?(0,a.FD)(a.FK,{children:[(0,a.Y)(oe,{dashboardPageId:m}),(0,a.Y)(le.Provider,{value:m,children:(0,a.Y)(W,{themeId:void 0!==I?null==I?void 0:I.id:null==F||null==(t=F.theme)?void 0:t.id,children:(0,a.Y)(H,{activeFilters:L,ownDataCharts:q,children:Y})})})]}):(0,a.Y)(h.R,{})]})},pe=he},5007:(e,t,n)=>{function a(e){const t="CssEditor-css",n=document.head||document.getElementsByTagName("head")[0],a=document.querySelector(`.${t}`)||function(e){const t=document.createElement("style");return t.className=e,t.type="text/css",t}(t);return"styleSheet"in a?a.styleSheet.cssText=e:a.innerHTML=e,n.appendChild(a),function(){a.remove()}}n.d(t,{A:()=>a})},39093:(e,t,n)=>{n.d(t,{Au:()=>o,I8:()=>l,J:()=>d,l6:()=>r});var a=n(35742),s=n(5362);const i=(e,t,n)=>{let a=`/api/v1/dashboard/${e}/filter_state`;return t&&(a=a.concat(`/${t}`)),n&&(a=a.concat(`?tab_id=${n}`)),a},r=(e,t,n,r)=>a.A.put({endpoint:i(e,n,r),jsonPayload:{value:t}}).then((e=>e.json.message)).catch((e=>(s.A.error(e),null))),o=(e,t,n)=>a.A.post({endpoint:i(e,void 0,n),jsonPayload:{value:t}}).then((e=>e.json.key)).catch((e=>(s.A.error(e),null))),l=(e,t)=>a.A.get({endpoint:i(e,t)}).then((({json:e})=>JSON.parse(e.value))).catch((e=>(s.A.error(e),null))),d=e=>a.A.get({endpoint:`/api/v1/dashboard/permalink/${e}`}).then((({json:e})=>e)).catch((e=>(s.A.error(e),null)))},47986:(e,t,n)=>{n.d(t,{z:()=>i});var a=n(73992);function s(e,t){return e.length===Object.keys(t).length}function i(e,t,n){var i;let r=[];const o=Object.keys(n).includes(e)&&(0,a.Ub)(t),l=Array.isArray(t.scope)?t.scope:null!=(i=t.chartsInScope)?i:[];o&&(r=function(e,t,n){if(!t[e])return[];const a=[...n.filter((t=>String(t)!==e)),Number(e)],i=new Set(n);return Object.values(t).reduce(((n,r)=>r.slice_id===Number(e)?n:s(a,t)?(n.push(r.slice_id),n):(i.has(r.slice_id)&&n.push(r.slice_id),n)),[])}(e,n,l));const d=t;return(!o||(0,a.ve)(d)||(0,a.qQ)(d))&&(r=function(e,t){if(s(t,e))return Object.keys(e).map(Number);const n=new Set(t);return Object.values(e).reduce(((e,t)=>(n.has(t.slice_id)&&e.push(t.slice_id),e)),[])}(n,l)),r}},92008:(e,t,n)=>{n.d(t,{R:()=>s,W:()=>a});const a=(e,t)=>e[t]?{[t]:e[t]}:{},s=({chartConfiguration:e,nativeFilters:t,dataMask:n,allSliceIds:a})=>{const s={},i=Object.values(n).some((({id:e})=>{var n;const a=null==t||null==(n=t[e])||null==(n=n.scope)?void 0:n.selectedLayers;return a&&a.length>0}));let r=[],o=[];return i&&Object.values(n).forEach((({id:e})=>{var n,a;const s=null==t||null==(n=t[e])||null==(n=n.scope)?void 0:n.selectedLayers,i=(null==t||null==(a=t[e])||null==(a=a.scope)?void 0:a.excluded)||[];s&&s.length>0&&(r=s,o=i)})),Object.values(n).forEach((({id:n,extraFormData:l={}})=>{var d,c,u,h,p,f,b,v,g;let m=null!=(d=null!=(c=null!=(u=null==t||null==(h=t[n])?void 0:h.chartsInScope)?u:null==e||null==(p=e[parseInt(n,10)])||null==(p=p.crossFilters)?void 0:p.chartsInScope)?c:a)?d:[];const y=null==t||null==(f=t[n])?void 0:f.filterType,S=null==t||null==(b=t[n])?void 0:b.targets;let w,E=null==t||null==(v=t[n])||null==(v=v.scope)?void 0:v.selectedLayers,x=(null==t||null==(g=t[n])||null==(g=g.scope)?void 0:g.excluded)||[];if(!i||E&&0!==E.length||(E=r,x=o),E&&E.length>0){const e=(e=>{const t={},n=new Set;return e.forEach((e=>{const a=e.match(/^chart-(\d+)-layer-(\d+)$/);if(a){const e=parseInt(a[1],10),s=parseInt(a[2],10);Number.isNaN(e)||(t[e]||(t[e]=[]),t[e].push(s),n.add(e))}})),{layerMap:t,chartIds:n}})(E);w=e.layerMap;const t=new Set(e.chartIds);m.forEach((e=>{x.includes(e)||E.some((t=>t.startsWith(`chart-${e}-layer-`)))||t.add(e)})),m=Array.from(t)}else m=m.filter((e=>!x.includes(e)));s[n]={scope:m,targets:S||[],values:l,filterType:y,...w&&{layerScope:w}}})),s}}}]);