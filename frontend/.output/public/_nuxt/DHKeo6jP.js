import{ap as N,aq as M,ar as O,as as B,at as P,P as q,c as _,o as y,a as b,al as C,X as R,C as D,au as h,t as j,u as H,n as G,m as X,p as Y,r as f,q as J,b as i,w as g,s as K,v as c,x as Q,z as W,y as Z,A as tt,B as et,D as nt,E as ot,F as at,G as lt,H as it}from"./DU3s_J-k.js";import{a as v}from"./DW_MHI2K.js";import{M as rt}from"./CeymNAjJ.js";import{_ as st}from"./B4doYjP3.js";var ct=function(n){var t=n.dt;return`
.p-togglebutton {
    display: inline-flex;
    cursor: pointer;
    user-select: none;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
    color: `.concat(t("togglebutton.color"),`;
    background: `).concat(t("togglebutton.background"),`;
    border: 1px solid `).concat(t("togglebutton.border.color"),`;
    padding: `).concat(t("togglebutton.padding"),`;
    font-size: 1rem;
    font-family: inherit;
    font-feature-settings: inherit;
    transition: background `).concat(t("togglebutton.transition.duration"),", color ").concat(t("togglebutton.transition.duration"),", border-color ").concat(t("togglebutton.transition.duration"),`,
        outline-color `).concat(t("togglebutton.transition.duration"),", box-shadow ").concat(t("togglebutton.transition.duration"),`;
    border-radius: `).concat(t("togglebutton.border.radius"),`;
    outline-color: transparent;
    font-weight: `).concat(t("togglebutton.font.weight"),`;
}

.p-togglebutton-content {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: `).concat(t("togglebutton.gap"),`;
}

.p-togglebutton-label,
.p-togglebutton-icon {
    position: relative;
    transition: none;
}

.p-togglebutton::before {
    content: "";
    background: transparent;
    transition: background `).concat(t("togglebutton.transition.duration"),", color ").concat(t("togglebutton.transition.duration"),", border-color ").concat(t("togglebutton.transition.duration"),`,
            outline-color `).concat(t("togglebutton.transition.duration"),", box-shadow ").concat(t("togglebutton.transition.duration"),`;
    position: absolute;
    inset-inline-start: `).concat(t("togglebutton.content.left"),`;
    inset-block-start: `).concat(t("togglebutton.content.top"),`;
    width: calc(100% - calc(2 * `).concat(t("togglebutton.content.left"),`));
    height: calc(100% - calc(2 * `).concat(t("togglebutton.content.top"),`));
    border-radius: `).concat(t("togglebutton.border.radius"),`;
}

.p-togglebutton.p-togglebutton-checked::before {
    background: `).concat(t("togglebutton.content.checked.background"),`;
    box-shadow: `).concat(t("togglebutton.content.checked.shadow"),`;
}

.p-togglebutton:not(:disabled):not(.p-togglebutton-checked):hover {
    background: `).concat(t("togglebutton.hover.background"),`;
    color: `).concat(t("togglebutton.hover.color"),`;
}

.p-togglebutton.p-togglebutton-checked {
    background: `).concat(t("togglebutton.checked.background"),`;
    border-color: `).concat(t("togglebutton.checked.border.color"),`;
    color: `).concat(t("togglebutton.checked.color"),`;
}

.p-togglebutton:focus-visible {
    box-shadow: `).concat(t("togglebutton.focus.ring.shadow"),`;
    outline: `).concat(t("togglebutton.focus.ring.width")," ").concat(t("togglebutton.focus.ring.style")," ").concat(t("togglebutton.focus.ring.color"),`;
    outline-offset: `).concat(t("togglebutton.focus.ring.offset"),`;
}

.p-togglebutton.p-invalid {
    border-color: `).concat(t("togglebutton.invalid.border.color"),`;
}

.p-togglebutton:disabled {
    opacity: 1;
    cursor: default;
    background: `).concat(t("togglebutton.disabled.background"),`;
    border-color: `).concat(t("togglebutton.disabled.border.color"),`;
    color: `).concat(t("togglebutton.disabled.color"),`;
}

.p-togglebutton-icon {
    color: `).concat(t("togglebutton.icon.color"),`;
}

.p-togglebutton:not(:disabled):not(.p-togglebutton-checked):hover .p-togglebutton-icon {
    color: `).concat(t("togglebutton.icon.hover.color"),`;
}

.p-togglebutton.p-togglebutton-checked .p-togglebutton-icon {
    color: `).concat(t("togglebutton.icon.checked.color"),`;
}

.p-togglebutton:disabled .p-togglebutton-icon {
    color: `).concat(t("togglebutton.icon.disabled.color"),`;
}

.p-togglebutton-sm {
    padding: `).concat(t("togglebutton.sm.padding"),`;
    font-size: `).concat(t("togglebutton.sm.font.size"),`;
}

.p-togglebutton-lg {
    padding: `).concat(t("togglebutton.lg.padding"),`;
    font-size: `).concat(t("togglebutton.lg.font.size"),`;
}
`)},dt={root:function(n){var t=n.instance,r=n.props;return["p-togglebutton p-component",{"p-togglebutton-checked":t.active,"p-invalid":t.$invalid,"p-togglebutton-sm p-inputfield-sm":r.size==="small","p-togglebutton-lg p-inputfield-lg":r.size==="large"}]},content:"p-togglebutton-content",icon:"p-togglebutton-icon",label:"p-togglebutton-label"},ut=N.extend({name:"togglebutton",theme:ct,classes:dt}),gt={name:"BaseToggleButton",extends:O,props:{onIcon:String,offIcon:String,onLabel:{type:String,default:"Yes"},offLabel:{type:String,default:"No"},iconPos:{type:String,default:"left"},readonly:{type:Boolean,default:!1},tabindex:{type:Number,default:null},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null},size:{type:String,default:null}},style:ut,provide:function(){return{$pcToggleButton:this,$parentInstance:this}}},S={name:"ToggleButton",extends:gt,inheritAttrs:!1,emits:["change"],methods:{getPTOptions:function(n){var t=n==="root"?this.ptmi:this.ptm;return t(n,{context:{active:this.active,disabled:this.disabled}})},onChange:function(n){!this.disabled&&!this.readonly&&(this.writeValue(!this.d_value,n),this.$emit("change",n))},onBlur:function(n){var t,r;(t=(r=this.formField).onBlur)===null||t===void 0||t.call(r,n)}},computed:{active:function(){return this.d_value===!0},hasLabel:function(){return B(this.onLabel)&&B(this.offLabel)},label:function(){return this.hasLabel?this.d_value?this.onLabel:this.offLabel:" "}},directives:{ripple:M}},bt=["tabindex","disabled","aria-pressed","aria-labelledby","data-p-checked","data-p-disabled"];function pt(e,n,t,r,m,a){var p=P("ripple");return q((y(),_("button",h({type:"button",class:e.cx("root"),tabindex:e.tabindex,disabled:e.disabled,"aria-pressed":e.d_value,onClick:n[0]||(n[0]=function(){return a.onChange&&a.onChange.apply(a,arguments)}),onBlur:n[1]||(n[1]=function(){return a.onBlur&&a.onBlur.apply(a,arguments)})},a.getPTOptions("root"),{"aria-labelledby":e.ariaLabelledby,"data-p-checked":a.active,"data-p-disabled":e.disabled}),[b("span",h({class:e.cx("content")},a.getPTOptions("content")),[C(e.$slots,"default",{},function(){return[C(e.$slots,"icon",{value:e.d_value,class:R(e.cx("icon"))},function(){return[e.onIcon||e.offIcon?(y(),_("span",h({key:0,class:[e.cx("icon"),e.d_value?e.onIcon:e.offIcon]},a.getPTOptions("icon")),null,16)):D("",!0)]}),b("span",h({class:e.cx("label")},a.getPTOptions("label")),j(a.label),17)]})],16)],16,bt)),[[p]])}S.render=pt;const ft={class:"flex flex-wrap gap-2 items-center justify-between"},_t={__name:"users",setup(e){H();const n=G(),t=X();Y();const r=f([]),m=f({global:{value:null,matchMode:"contains"}}),a=f(null),p=f([]),k=f({}),$=()=>{v.get("/api/users").then(o=>{p.value=o.data}).catch(o=>{n.add({severity:"error",summary:"Error while getting requests",detail:o.response.data,life:3e3})}),p.value.forEach(o=>k.value[o.email]=o.is_admin),console.log(k.value)};J(()=>{v.get("/api/users/me").then(o=>{console.log(o.data),a.value=o.data}).catch(),$()});const x=()=>{let o=[];console.log(r),r.value.forEach(l=>{o.push(l.email)}),console.log(o),t.require({message:`Are you sure you want to delete ${o.length} users`,header:"Delete Confirmation",icon:"pi pi-exclemation-triangle",accept:()=>{r.value=null,o.forEach(l=>{v.delete(`/api/users/${l}`).then(()=>{n.add({severity:"success",summary:"Delete Successful",detail:`User ${l} deleted successfully.`,life:3e3}),$()}).catch(d=>{n.add({severity:"error",summary:"Delete Failed",detail:d.response.data,life:3e3})})})}})},T=o=>{const l=new FormData;l.append("is_admin",o.is_admin),v.post(`/api/users/${o.email}/edit`,l,{headers:{"Content-Type":"multipart/form-data"}}).then(d=>{n.add({severity:"success",summary:"User role changed",detail:`Updated user ${o.email} role to: ${o.is_admin?"Admin":"User"}`,life:3e3})}).catch(d=>{n.add({severity:"error",summary:"User role change failed",detail:`Failed to update user role for ${o.email}: ${d}`,life:3e3})})};return(o,l)=>{const d=W,L=Z,I=nt,U=at,V=lt,z=ot,u=tt,A=S,E=Q,F=it;return y(),_("div",null,[i(rt),l[4]||(l[4]=b("h1",{class:"m-4 text-3xl font-bold"},"Users",-1)),i(d),i(E,{value:c(p),scrollable:"",scrollHeight:"500px",filters:c(m),selection:c(r),"onUpdate:selection":l[2]||(l[2]=s=>K(r)?r.value=s:null)},{header:g(()=>[b("div",ft,[b("div",null,[c(a)&&c(a).is_admin?(y(),et(I,{key:0,label:"Delete",icon:"pi pi-trash",severity:"danger",onClick:l[0]||(l[0]=s=>x()),disabled:!c(r)||!c(r).length},null,8,["disabled"])):D("",!0)]),i(z,null,{default:g(()=>[i(U,null,{default:g(()=>l[3]||(l[3]=[b("i",{class:"pi pi-search"},null,-1)])),_:1}),i(V,{modelValue:c(m).global.value,"onUpdate:modelValue":l[1]||(l[1]=s=>c(m).global.value=s),placeholder:"Search..."},null,8,["modelValue"])]),_:1})])]),default:g(()=>[i(L,{position:"bottom-right"}),i(u,{selectionMode:"multiple",headerStyle:"width: 3rem"}),i(u,{field:"email",header:"Email",sortable:""}),i(u,{field:"name",header:"Name"}),i(u,{field:"surname",header:"Surname"}),i(u,{field:"created_at",header:"Created At"},{body:g(s=>[i(st,{datetime:s.data.created_at},null,8,["datetime"])]),_:1}),i(u,{field:"is_admin",header:"Role"},{body:g(s=>[i(A,{modelValue:s.data.is_admin,"onUpdate:modelValue":w=>s.data.is_admin=w,onLabel:"Admin",offLabel:"User",onIcon:"pi pi-wrench",offIcon:"pi pi-user",class:"p-button-sm",disabled:c(a).email==s.data.email||!c(a).is_admin,onChange:w=>T(s.data)},null,8,["modelValue","onUpdate:modelValue","disabled","onChange"])]),_:1})]),_:1},8,["value","filters","selection"]),i(F)])}}};export{_t as default};
