// Dump the rubric tables from the real app.js as JSON, so Python never has to
// parse JS. jsc: jsc dump_rubric.js -- <repo_dir> <out.json>
const args = (typeof scriptArgs !== 'undefined') ? scriptArgs
           : (typeof arguments !== 'undefined') ? Array.prototype.slice.call(arguments) : [];
const [REPO, OUT] = args;
function readText(p){ if (typeof require==='function') return require('fs').readFileSync(p,'utf8');
  if (typeof readFile==='function') return readFile(p); throw new Error('no reader'); }
function writeText(p,s){ if (typeof require==='function') return require('fs').writeFileSync(p,s);
  if (typeof writeFile==='function') return writeFile(p,s); throw new Error('no writer'); }
const elements=new Map();
function stubEl(id){ if(!elements.has(id)) elements.set(id,{id,value:'',textContent:'',innerHTML:'',
  hidden:true,disabled:false,classList:{add(){},remove(){},contains(){return false},toggle(){return false}},
  addEventListener(){},appendChild(){},removeChild(){},click(){},focus(){},setAttribute(){},style:{}});
  return elements.get(id); }
globalThis.document={getElementById:stubEl,addEventListener(){},createElement:()=>({style:{},click(){},setAttribute(){},appendChild(){}}),body:{appendChild(){},removeChild(){}}};
globalThis.window={print(){}};
let ls={}; globalThis.localStorage={getItem:k=>(k in ls?ls[k]:null),setItem:(k,v)=>{ls[k]=String(v);},removeItem:k=>{delete ls[k];}};
globalThis.Blob=function(){}; globalThis.URL={createObjectURL:()=>'',revokeObjectURL(){}};
if (typeof setTimeout!=='function') globalThis.setTimeout=()=>0;
(0,eval)(readText(REPO+'/app.js')+'\n;globalThis.APP={DOMAINS,PART_A_MAX,TIERS,STATIC_WU,STATUS_ROWS,PHASE_MULTIPLIERS,DATA_VOLUME_ITEMS,DATA_VOLUME_MAX,DATA_VOLUME_FACTOR_RANGE,RUBRIC_VERSION,TOOL_VERSION,DEFAULT_PHASE};');
const A=globalThis.APP;
writeText(OUT, JSON.stringify({
  rubricVersion:A.RUBRIC_VERSION, toolVersion:A.TOOL_VERSION, partAMax:A.PART_A_MAX,
  defaultPhase:A.DEFAULT_PHASE, staticWU:A.STATIC_WU,
  dataVolumeItems:A.DATA_VOLUME_ITEMS.map(it=>it.id), dataVolumeMax:A.DATA_VOLUME_MAX,
  dataVolumeFactorRange:A.DATA_VOLUME_FACTOR_RANGE,
  tiers:A.TIERS, statusRows:A.STATUS_ROWS, phases:A.PHASE_MULTIPLIERS,
  domains:A.DOMAINS.map(d=>({id:d.id,title:d.title,cap:d.cap??null,max:d.max,itemizedMax:d.itemizedMax,
    items:d.items.map(it=>({id:it.id,label:it.label,max:it.max,note:it.note||'',dataVolume:!!it.dataVolume}))})),
}, null, 2));
print('dumped '+A.DOMAINS.reduce((n,d)=>n+d.items.length,0)+' items, Part A max '+A.PART_A_MAX);
