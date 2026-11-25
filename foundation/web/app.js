'use strict';
const byId = id => document.getElementById(id);
const statusText = text => { byId('status').textContent = text; };
let skills = [];
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
async function run(action) {
  try { await action(); } catch (error) { statusText(error.message); }
}
function button(label, action) {
  const b = el('button', label);
  b.type = 'button';
  b.onclick = () => run(async () => {
    b.disabled = true;
    try { await action(); } finally { b.disabled = false; }
  });
  return b;
}
async function api(route, args = {}, write = false) {
  if (!location.protocol.startsWith('http')) throw Error('Open the teacher portal through its Foundation server.');
  const url = '/api/foundation/' + route;
  const response = await fetch(write ? url : url + '?' + new URLSearchParams(args), write ? {
    method:'POST', headers:{'Content-Type':'application/json','X-KB-Request':'teacher'},body:JSON.stringify(args)
  } : {});
  if (!(response.headers.get('content-type') || '').includes('application/json')) {
    throw Error('This host is serving the static portal. Connect to the Foundation server to open the database.');
  }
  const data = await response.json();
  if (!response.ok) throw Error(data.error || 'Request failed.');
  return data;
}
function onForm(id, action) {
  const form = byId(id);
  form.onsubmit = event => {
    event.preventDefault();
    run(async () => {
      const control = form.querySelector('button');
      control.disabled = true;
      try { await action(Object.fromEntries(new FormData(form))); } finally { control.disabled = false; }
    });
  };
}
const reference = r => r.year+' '+r.series+' · Q'+r.num+(r.part?'('+r.part+')':'')+
  ' · paper p. '+r.page+' · scheme p. '+(r.scheme_page || 'unresolved');
async function summary() {
  const data = await api('summary');
  skills = data.skills;
  byId('model').disabled = !data.model;
  byId('studio-ai-option').disabled = !data.studio_ai_configured;
  byId('prompt-submit').disabled = !data.studio_ai_configured;
  byId('prompt-feedback').textContent=data.studio_ai_configured?'AI question design available.':'AI not configured; use the manual question builder.';
  if(!data.studio_ai_configured) byId('manual-options').open=true;
  if(!data.studio_ai_configured) byId('studio-mode').value='local';
  byId('studio-ai-status').textContent=data.studio_ai_configured ? 'AI-assisted selection configured. Each AI batch calls the model once; local mode uses no API.' : 'AI-assisted selection not configured. Local generation remains available.';
  byId('units').replaceChildren(...data.units.map(u => {
    const card = el('div', undefined, 'unit');
    card.append(el('h3',u.unit),el('p',u.verified ? 'Partial retrieval available' : 'Inventory only'),
      el('p',u.papers+' papers · '+u.paired+' confirmed pairs'),el('p',u.pair_review+' pairs to review · '+u.missing+' missing files'),
      el('p',u.questions+' anchors · '+u.verified+' verified · '+u.review+' to review'),
      el('small',u.classified+' classifications incl. suggestions · '+u.covered_skills+' / '+u.skills+' skill groups verified'),
      el('small',u.reports+' reports · '+(u.examiner_anchors || 0)+' question references · '+(u.examiner_notes || 0)+' teaching notes'),el('small',(u.examiner_tagged || 0)+' report questions with provisional topic evidence · '+u.failures+' extraction failures'),el('small','Last extraction: '+(u.last_extraction || 'Pending')));
    return card;
  }));
}
function showRules(node,rules) {
  for (const [i,route] of rules.entries()) {
    const list = el('ul');
    for (const c of route) list.append(el('li',c.code+' · '+c.evidence));
    if (rules.length>1) node.append(el('strong','Method '+(i+1)));
    node.append(list);
  }
}
function showRecord(r) {
  const card = el('article');
  card.append(el('h3',r.label || 'Classification pending'),el('small',reference(r)),
    el('p',r.annotation || 'Candidate page reference awaiting inspection.'));
  if (r.answer) card.append(el('p',r.answer));
  if (r.rules) showRules(card,JSON.parse(r.rules));
  if (r.spec_page) card.append(el('small','Inferred classification · specification §3.1 p. '+r.spec_page));
  card.append(button('Inspect record',()=>inspect(r.id)));
  return card;
}
onForm('search',async args => {
  const data = await api('search',args);
  byId('results').replaceChildren(...data.map(showRecord));
  statusText(data.length ? data.length+' verified matches shown.' : 'No verified matches for this search.');
});
function showExaminer(r) {
  const card=el('article');
  card.append(el('h3',r.year+' '+r.series+' · '+r.unit+' · '+r.component+' · Q'+r.num),el('small','Chief Examiner report '+r.filename+' · PDF pp. '+r.start_page+'–'+r.end_page));
  for (const n of r.notes) card.append(el('strong',n.topic),el('p',n.note),el('small',n.review_status));
  if (r.skills.length) card.append(el('small','Provisional whole-question topic links: '+r.skills.map(s=>s.label+' (spec. p. '+s.spec_page+')').join('; ')));
  if (!r.notes.length) card.append(el('p','Topic evidence only. The examiner observation has not yet been summarised.'));
  card.append(el('small','Examiner commentary; not an official marking rule.'));
  return card;
}
onForm('examiner-search',async args=>{
  const data=await api('examiner',args);
  byId('examiner-results').replaceChildren(...data.map(showExaminer));
  statusText(data.length?data.length+' examiner references shown.':'No linked examiner evidence for this search.');
});
async function papers(unit,cursor={}) {
  const data = await api('papers',{unit,...cursor});
  const wrap = byId('papers');
  wrap.replaceChildren();
  byId('records').replaceChildren(); byId('editor').replaceChildren();
  for (const p of data.slice(0,50)) {
    const card = el('article');
    card.append(el('strong',p.year+' '+p.series+' · '+p.component+' · '+p.status),el('small',p.reason));
    if (p.paper) card.append(button('View question anchors',()=>records(unit,p.paper)));
    wrap.append(card);
  }
  if (data.length>50) {
    const {year,series,component} = data[49];
    wrap.append(button('Next papers',()=>papers(unit,{year,series,component})));
  }
  statusText('Paper inventory loaded.');
}
onForm('browse',({unit})=>papers(unit));
async function records(unit,paper,after=0) {
  const data = await api('records',{unit,paper,after});
  byId('editor').replaceChildren();
  const wrap = byId('records');
  wrap.replaceChildren(el('h3','Question anchors'));
  for (const r of data.slice(0,20)) {
    wrap.append(button('Q'+r.num+' '+r.part+' · '+r.status,()=>inspect(r.id)));
  }
  if (data.length>20) wrap.append(button('Next anchors',()=>records(unit,paper,data[19].id)));
  statusText(data.length?'Select a source record.':'No question records extracted from this paper.');
}
function field(form,title,type,value) {
  const label = el('label',title);
  const input = el(type);
  input.value = value ?? '';
  label.append(input); form.append(label); return input;
}
async function inspect(id) {
  const r = await api('record',{id});
  const target = byId('editor');
  target.replaceChildren(el('h3',reference(r)));
  if (r.extraction_note) target.append(el('p',r.extraction_note));
  if (r.examiner_evidence?.length) {
    target.append(el('h4','Related whole-question examiner evidence'),...r.examiner_evidence.map(showExaminer));
  }
  const form = el('form',undefined,'stack');
  target.append(form);
  const topic = field(form,'Curriculum skill','select','');
  for (const s of skills.filter(s=>s.unit===r.unit)) topic.add(new Option(s.label,s.id));
  topic.value = r.skill || '';
  const fields = {};
  for (const [key,label] of Object.entries({page:'First paper page',end_page:'Last paper page',scheme_page:'Mark scheme page',marks:'Available marks'})) {
    const input = field(form,label,'input',r[key]); input.type='number'; input.min='1'; input.required=true; fields[key]=input;
  }
  const note = field(form,'Teaching note in your own words','textarea',r.annotation);
  const answer = field(form,'Answer and reasoning','textarea',r.answer);
  const routes = field(form,'Marking routes (JSON, one criterion list per method)','textarea',
    r.rules || JSON.stringify([[{code:'A1',evidence:''}]]));
  const state = field(form,'Verification','select','');
  state.add(new Option('Requires review','review')); state.add(new Option('Checked against paper and scheme','verified')); state.value=r.status;
  const submit = el('button','Save source review'); form.append(submit);
  form.onsubmit = event => {
    event.preventDefault();
    run(async () => {
      submit.disabled=true;
      try {
        const numbers = Object.fromEntries(Object.entries(fields).map(([k,v])=>[k,Number(v.value)]));
        await api('review',{...numbers,id:r.id,version:r.version,skill:topic.value,annotation:note.value,answer:answer.value,
          rules:JSON.parse(routes.value),status:state.value,depends_on:r.depends_on},true);
        byId('results').replaceChildren(); byId('records').replaceChildren();
        await summary(); await inspect(id); statusText('Source review saved.');
      } finally { submit.disabled=false; }
    });
  };
  target.scrollIntoView({block:'start'});
}
let studioFamilies=[];
function showStudioEvidence() {
  const item=studioFamilies.find(x=>x.family===byId('studio-family').value);
  byId('studio-evidence').textContent=item ? item.skill_label+' · specification p. '+item.spec_page+
    (item.sources.length?' · '+item.sources.length+' related-skill source-checked references':' · specification only; no source-checked references in this unit') : 'No enabled family for this unit.';
}
async function studioCatalog(){
  const unit=byId('studio-unit').value, selector=byId('studio-family');
  const submit=byId('studio').querySelector('button');
  submit.disabled=true; selector.replaceChildren(); studioFamilies=[]; showStudioEvidence();
  const rows=await api('studio-catalog',{unit});
  if(byId('studio-unit').value!==unit) return;
  studioFamilies=rows;
  for(const item of rows) selector.add(new Option(item.label,item.family));
  showStudioEvidence(); submit.disabled=!rows.length;
}
byId('studio-unit').onchange=()=>run(studioCatalog);
byId('studio-family').onchange=showStudioEvidence;
function examParts(d){
  const chunks=d.question.split(/(?:^|\s)\(([a-z])\)\s+/);
  if(chunks.length>=3 && chunks.length%2===1){
    const parts=[];
    for(let i=1;i<chunks.length;i+=2){
      const part=chunks[i], marks=d.rubric.filter(r=>r.startsWith('('+part+')')).length;
      if(part!==String.fromCharCode(97+parts.length)||!marks||!chunks[i+1].trim()) return null;
      parts.push({part,text:chunks[i+1].trim(),marks});
    }
    if(parts.reduce((n,p)=>n+p.marks,0)===d.marks) return {context:chunks[0].trim(),parts};
  }
  return null;
}
function examPreview(d,number){
  const preview=el('div',undefined,'exam-preview');
  const heading=el('div',undefined,'exam-heading');
  heading.append(el('strong',number?'Question '+number:'Question preview'),el('span','['+d.marks+' marks]'));
  preview.append(heading);
  const split=examParts(d);
  const context=split?.context;
  if(context)preview.append(el('p',context,'exam-context'));
  const diagram=renderStudioDiagram(d.diagram);
  if(diagram)preview.append(diagram);
  const parts=split?split.parts:[{part:'',text:d.question,marks:d.marks}];
  for(const p of parts){
    const block=el('div',undefined,'exam-part'), task=el('div',undefined,'exam-task');
    task.append(el('span',(p.part?'('+p.part+') ':'')+p.text),el('span','['+p.marks+(p.marks===1?' mark]':' marks]')));
    block.append(task);
    for(let i=0;i<Math.min(3,p.marks);i++){
      const line=el('div',undefined,'exam-line'); line.setAttribute('aria-hidden','true');block.append(line);
    }
    preview.append(block);
  }
  preview.append(el('div','Total: '+d.marks+' marks','exam-total'));
  return preview;
}
function showStudioBatch(rows){
  const wrap=byId('studio-results');wrap.replaceChildren();
  rows.forEach((d,i)=>{
    const card=el('article');
    card.append(el('h3',d.label),el('small',d.unit+' · '+d.difficulty),
      examPreview(d,i+1),
      el('small',d.evidence_level==='specification-only'?'Specification only':'Related-skill source-checked references'),
      el('small',d.model_role|| (d.mode==='model'?'AI-assisted · validated template':'Local generation')),
      button('Review solution and mark scheme',()=>{showDraft(d);byId('draft').scrollIntoView({block:'start'});}));
    wrap.append(card);
  });
  statusText(rows.length+' validated drafts saved for teacher review · '+rows.reduce((n,r)=>n+r.marks,0)+' marks total.');
}
byId('prompt-example').onclick=()=>{
  byId('prompt-unit').value='M1';
  byId('teacher-prompt').value='Create three 4-mark shopping discount questions about the reduction, sale price and money left in a budget. Include worked solutions and mark schemes.';
  byId('teacher-prompt').focus();
};
onForm('prompt-studio',async args=>{
  const feedback=byId('prompt-feedback');
  feedback.textContent='Designing and checking your questions…';
  statusText('AI is designing mathematical parameters…');
  try{
    const rows=await api('studio-prompt',args,true);
    showStudioBatch(rows);
    feedback.textContent=rows[0]?.generation_notice || (rows.length+' validated drafts generated. Check that the questions meet your request before approving them.');
  }catch(error){
    feedback.textContent=error.message;
    throw error;
  }
});
onForm('studio',async args=>{
  statusText(args.mode==='model'?'Selecting validated questions with AI…':'Generating validated questions…');
  const rows=await api('studio',{...args,count:Number(args.count)},true);
  showStudioBatch(rows);
});
onForm('generate',async args=>{
  const d=await api('practice',args,true);
  showDraft(d);
  statusText('Draft ready for teacher review.');
});
function showDraft(d) {
  const wrap=byId('draft'), form=el('div',undefined,'stack');
  wrap.replaceChildren(el('h3',d.label),el('small',d.unit+' · '+d.state),form);
  const prompt=d.family?{value:d.question,readOnly:true}:field(form,'Practice question','textarea',d.question);
  if(d.family){form.append(examPreview(d),el('small','Question wording is locked to the validated solution; regenerate for a different question.'));}
  else {const diagram=renderStudioDiagram(d.diagram);if(diagram) form.append(diagram);}
  const solution=el('ol'), rubric=el('ul');
  for(const step of d.solution) solution.append(el('li',step));
  for(const rule of d.rubric) rubric.append(el('li',rule));
  form.append(el('strong','Worked solution'),solution,el('div',d.answer,'review-answer'),el('strong','Proposed marking scheme · '+d.marks+' marks'),rubric,
    el('p',d.validation),el('small',d.spec+' · '+d.difficulty),el('small',d.sources.map(reference).join(' / ')));
  if(d.model_role) form.append(el('small','Model role: '+d.model_role));
  if(d.family) form.append(el('small',d.evidence_level==='specification-only'?'Specification-only template; no related verified references in this unit.':'References concern the same skill, not a verified match to this original question.'),el('small','Proposed marking scheme; teacher approval required.'));
  if (d.state==='approved') {
    prompt.readOnly=true; form.append(el('strong','Approved by teacher')); return;
  }
  form.append(button('Confirm solution and approve question',async()=>{
    await api('approve',{id:d.id,question:prompt.value},true);
    prompt.readOnly=true; form.lastChild.replaceWith(el('strong','Approved by teacher')); statusText('Approved practice saved.');
  }));
}
async function history(before) {
  const rows = await api('drafts',before ? {before} : {});
  const wrap = byId('drafts');
  wrap.replaceChildren(el('h3','My saved practice'));
  for (const d of rows.slice(0,10)) wrap.append(button(d.id+' · '+d.skill+' · '+d.state,()=>showDraft(d)));
  if (rows.length>10) wrap.append(button('Older practice',()=>history(rows[9].id)));
  if (!rows.length) wrap.append(el('p','No saved practice yet.'));
}
byId('history').onclick=()=>run(()=>history());
run(async()=>{ await summary(); await studioCatalog(); statusText('Foundation inventory loaded.'); });
