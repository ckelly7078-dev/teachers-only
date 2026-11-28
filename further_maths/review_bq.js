'use strict';
const byId = id => document.getElementById(id);
const mode = byId('mode'), filter = byId('filter'), item = byId('item');
let ids = [], current = null, serial = 0, proofReady = false;
const reviewButton=byId('review').querySelector('button');
const proofZoom=byId('proof-zoom'), proofFrame=byId('proof-frame');
function setZoom(expanded){proofFrame.classList.toggle('expanded',expanded);proofZoom.setAttribute('aria-pressed',String(expanded));proofZoom.textContent=expanded?'Fit proof to screen':'Enlarge proof';if(!expanded)proofFrame.scrollLeft=0;}
proofZoom.addEventListener('click',()=>{if(proofReady)setZoom(proofZoom.getAttribute('aria-pressed')!=='true');});
function invalidate(){current=null;proofReady=false;reviewButton.disabled=true;proofZoom.disabled=true;setZoom(false);byId('proof').removeAttribute('src');byId('preview').hidden=true;}
function status(s){byId('status').textContent=s;}
function error(e){status(e.message);}
async function api(path,params={},body){
 const url='api/'+path+(body?'':'?'+new URLSearchParams(params));
 const response=await fetch(url,body?{method:'POST',headers:{'Content-Type':'application/json','X-AS1-Request':'teacher'},body:JSON.stringify(body)}:{});
 const data=await response.json();if(!response.ok)throw Error(data.error||'Request failed');return data;
}
function fill(){const q=filter.value.toLowerCase(),old=item.value;item.replaceChildren(...ids.filter(x=>x.toLowerCase().includes(q)).map(x=>new Option(x,x)));if([...item.options].some(x=>x.value===old))item.value=old;status(item.options.length+' matching variants');}
async function list(){const seq=++serial;invalidate();ids=[];item.replaceChildren();const data=await api('list',{mode:mode.value});if(seq!==serial)return;ids=data.ids;fill();}
mode.addEventListener('change',()=>{resetProgress();list().catch(error);});filter.addEventListener('input',()=>{
 const previous=item.value;
 fill();
 if(item.value!==previous)cancelPreview();
});
function cancelPreview(){++serial;invalidate();status(item.value?'Open the selected variant.':'No matching variants.');}
item.addEventListener('change',cancelPreview);
const progressLoad=byId('progress-load'), progressNext=byId('progress-next');
let progressSerial=0, progress=null;
function showPreviousChecks(){const row=current&&progress&&progress.mode===current.mode&&progress.items.find(r=>r.id===current.item.id);byId('previous-checks').textContent=row?'Previously recorded by you: '+Object.entries(row.checks).map(([k,v])=>k+': '+v.replaceAll('_',' ')).join(' | ')+'. Choose only checks performed now.':'Refresh my progress to see your previous observations.';}
function resetProgress(){++progressSerial;progress=null;progressLoad.disabled=false;progressNext.disabled=true;byId('progress-status').textContent='Refresh to see your saved review progress.';}
async function loadProgress(){
 const seq=++progressSerial, selectedMode=mode.value;
 progress=null;progressLoad.disabled=true;progressNext.disabled=true;
 const summary=byId('progress-status');summary.textContent='Loading your saved review progress.';
 try{
  const data=await api('progress',{mode:selectedMode});
  if(seq!==progressSerial||mode.value!==selectedMode)return;
  progress=data;
  showPreviousChecks();
  const c=data.counts;
  summary.textContent=c.outstanding+' outstanding | '+c.needs_revision+' need revision | '+c.all_checks_observed_pass+' all checks observed as pass. No examination approval.'+(data.stale_observations_in_mode?' '+data.stale_observations_in_mode+' stale observations excluded.':'')+(data.recording_available?'':' Observation recording is not configured.');
  progressNext.disabled=!data.recording_available||!data.items.some(r=>r.state!=='all_checks_observed_pass');
 }catch(e){if(seq===progressSerial)summary.textContent=e.message;}
 finally{if(seq===progressSerial)progressLoad.disabled=false;}
}
progressLoad.addEventListener('click',loadProgress);
progressNext.addEventListener('click',()=>{
 if(!progress||progress.mode!==mode.value)return;
 const pending=progress.items.filter(r=>r.state!=='all_checks_observed_pass'&&ids.includes(r.id));
 const next=pending.find(r=>r.id!==item.value)||pending[0];
 if(!next)return;
 filter.value='';fill();item.value=next.id;cancelPreview();
 status('Selected '+next.id+'. Open preview to review.');
});

const checks=['visual','mathematics','marking','scope','difficulty'];
for(const c of checks){const label=document.createElement('label');label.textContent=c+' review';label.htmlFor='check-'+c;const select=document.createElement('select');select.id=label.htmlFor;for(const [v,t] of [['not_reviewed','Not reviewed'],['pass','Pass'],['revise','Needs revision']])select.add(new Option(t,v));byId('checks').append(label,select);}
function para(text){const p=document.createElement('p');p.textContent=text;return p;}
byId('browse').addEventListener('submit',async e=>{e.preventDefault();const seq=++serial;try{invalidate();status('Loading preview');const query={id:item.value,mode:mode.value};const d=await api('item',query);if(seq!==serial)return;current=d;const p=d.item.payload;byId('version').textContent=d.item.id+' | '+d.item.revision+' | '+d.item.marks+' provisional marks';byId('proof').src='api/page?'+new URLSearchParams(query);byId('raw').replaceChildren(para('Question: '+p.question_latex),para('Answer: '+p.final_answer_latex),...p.worked_solution_latex.map((x,i)=>para((i+1)+'. '+x)));byId('rubric').replaceChildren(...p.rubric.map(r=>{const n=document.createElement('li');n.textContent=r.type+' '+r.marks+': '+r.criterion;return n;}));byId('review').reset();showPreviousChecks();reviewButton.disabled=true;byId('review-status').textContent='';byId('preview').hidden=false;status('Loading rendered proof. Not examination approved.');}catch(e){error(e);}});
byId('proof').addEventListener('load',()=>{if(current&&byId('proof').naturalWidth){proofReady=true;reviewButton.disabled=false;proofZoom.disabled=false;status('Preview loaded. Not examination approved.');}});
byId('proof').addEventListener('error',()=>{proofReady=false;reviewButton.disabled=true;proofZoom.disabled=true;setZoom(false);if(current)status('Proof rendering failed. Do not certify this preview.');});
byId('review').addEventListener('submit',async e=>{e.preventDefault();const d=current;if(!d||!proofReady)return;const b=e.currentTarget.querySelector('button');b.disabled=true;try{const data={id:d.item.id,mode:d.mode,fingerprint:d.fingerprint,proof_sha256:d.proof_sha256,checks:Object.fromEntries(checks.map(c=>[c,byId('check-'+c).value])),note:byId('note').value};const r=await api('review',{},data);if(current===d)byId('review-status').textContent='Observation '+r.observation_id+' saved. No examination approval.';if(progress&&progress.mode===mode.value)loadProgress();}catch(e){if(current===d)byId('review-status').textContent=e.message;}finally{if(current===d)b.disabled=!proofReady;}});
list().catch(error);
