'use strict';
// Generated questions are validated by the authenticated API; worksheet decisions live only in this page.
let workspaceRows=[];
let nextQuestionId=1;
let workspaceReady=false;
let workspaceBusy=false;
let worksheetMode=null;
const expandedReviews=new Set();
const expandedRows=new Set();
const stateLabels={draft:'Awaiting review',under_review:'Under review',approved:'Approved',discarded:'Discarded'};
const pendingRows=()=>workspaceRows.filter(d=>d.state==='draft'||d.state==='under_review');
const approvedRows=()=>workspaceRows.filter(d=>d.state==='approved');
const markTotal=rows=>rows.reduce((sum,d)=>sum+d.marks,0);
function clearWorksheetPreview(){
  worksheetMode=null;
  byId('worksheet-preview').replaceChildren();
  byId('worksheet-preview').hidden=true;
  document.body.classList.remove('worksheet-printing');
  byId('worksheet-print').replaceChildren();
}
function updateWorkspaceControls(){
  const pending=pendingRows().length, approved=approvedRows().length;
  const ready=workspaceReady&&!workspaceBusy&&!pending&&approved>0;
  for(const id of ['worksheet-preview-btn','worksheet-export-btn','scheme-export-btn'])byId(id).disabled=!ready;
  byId('worksheet-gate').textContent=!workspaceReady?'Preparing an empty worksheet…':workspaceBusy?'Working on your questions…':pending?`${pending} question${pending===1?'':'s'} still need a decision. Approve or discard every pending question to unlock worksheet export.`:!approved?'Approve at least one question to build a worksheet.':'All questions have been decided. Your worksheet is ready to preview or export.';
}
async function workspaceTask(action){
  if(workspaceBusy)throw Error('Another question operation is in progress.');
  workspaceBusy=true;updateWorkspaceControls();
  try{return await action();}finally{workspaceBusy=false;updateWorkspaceControls();}
}
function addWorkspaceRows(rows){
  if(!Array.isArray(rows)||rows.some(d=>!d||typeof d.question!=='string'||!Number.isInteger(d.marks)||d.marks<1))throw Error('Invalid generated questions.');
  workspaceRows.push(...rows.map(d=>({...d,id:nextQuestionId++,state:'draft'})));
}
async function refreshWorkspace(){
  workspaceReady=true;clearWorksheetPreview();renderWorkspace();
}
function resetWorkspace(){
  workspaceRows=[];nextQuestionId=1;expandedReviews.clear();expandedRows.clear();
  byId('worksheet-title').value='';
  return refreshWorkspace();
}
function statusPill(state){return el('span',stateLabels[state],'queue-status status-'+state);}
function rowSummary(d){
  const head=el('summary',undefined,'queue-summary');
  const text=el('div',undefined,'queue-title');
  text.append(el('strong',`#${d.id} · ${d.label.replace(/ - original practice$/,'')}`),el('small',d.question,'queue-snippet'));
  head.append(text,el('span',`${d.unit} · ${d.marks} mark${d.marks===1?'':'s'}`,'queue-meta'),statusPill(d.state));
  return head;
}
function queueButton(label,action,style){const b=button(label,action);if(style)b.classList.add(style);return b;}
const temporaryTransitions={draft:['under_review','discarded'],under_review:['discarded','draft'],approved:['under_review','discarded'],discarded:['draft']};
async function decision(d,target){
  await workspaceTask(async()=>{
    const row=workspaceRows.find(r=>r.id===d.id);
    if(!row||row.state!==d.state||!temporaryTransitions[row.state]?.includes(target))throw Error('Question changed. Select the current question.');
    workspaceRows=workspaceRows.map(r=>r.id===d.id?{...r,state:target}:r);
    if(target==='under_review')expandedReviews.add(d.id);else expandedReviews.delete(d.id);
    expandedRows.delete(d.id);
    await refreshWorkspace();
    statusText('Question #'+d.id+' · '+stateLabels[target]);
    // Keep the teacher in the current list; review is opened without navigating to it.
  });
}
async function approveQuestion(d){
  await workspaceTask(async()=>{
    const row=workspaceRows.find(r=>r.id===d.id);
    if(!row||row.state!=='under_review'||d.state!==row.state)throw Error('Question must be under review before approval.');
    workspaceRows=workspaceRows.map(r=>r.id===d.id?{...r,state:'approved'}:r);
    expandedReviews.delete(d.id);expandedRows.delete(d.id);
    await refreshWorkspace();statusText('Question #'+d.id+' approved and added to this temporary worksheet.');
  });
}
function reviewContent(d){
  const form=el('div',undefined,'stack review-content');
  form.append(examPreview(d));
  form.append(el('small','Question wording is locked to the validated solution. Regenerate to change it.'));
  const solution=el('ol'),rubric=el('ul');
  for(const step of d.solution)solution.append(el('li',step));
  for(const rule of d.rubric)rubric.append(el('li',rule));
  form.append(el('strong','Worked solution'),solution,el('div',d.answer,'review-answer'),el('strong','Proposed marking scheme · '+d.marks+' marks'),rubric,
    el('p',d.validation),el('small',d.spec+' · '+d.difficulty),el('small',(d.sources||[]).map(reference).join(' / ')));
  if(d.difficulty_features)form.append(el('small','Difficulty rationale: '+d.difficulty_features));
  if(d.model_role)form.append(el('small','Model role: '+d.model_role));
  if(d.family)form.append(el('small',d.evidence_level==='specification-only'?'Specification-only template; no related verified references in this unit.':'References concern the same skill, not a verified match to this original question.'));
  const actions=el('div',undefined,'queue-actions');
  if(d.state==='under_review')actions.append(queueButton('Approve question',()=>approveQuestion(d),'approve-action'),queueButton('Discard',()=>decision(d,'discarded'),'discard-action'));
  if(d.state==='approved')actions.append(queueButton('Return to review',()=>decision(d,'under_review'),'secondary-action'),queueButton('Remove from worksheet',()=>decision(d,'discarded'),'discard-action'));
  form.append(actions);return form;
}
function queueRow(d){
  const outer=el('div',undefined,'queue-row row-'+d.state);outer.id='question-'+d.id;
  const details=el('details',undefined,'queue-details');const expanded=d.state==='under_review'?expandedReviews:expandedRows;
  details.open=expanded.has(d.id);details.ontoggle=()=>{if(!details.isConnected)return;if(details.open)expanded.add(d.id);else expanded.delete(d.id)};
  details.append(rowSummary(d));
  if(d.state==='under_review'||d.state==='approved')details.append(reviewContent(d));
  else details.append(examPreview(d));
  outer.append(details);
  if(d.state==='draft'||d.state==='discarded'){
    const actions=el('div',undefined,'queue-actions queue-quick-actions');
    if(d.state==='draft')actions.append(queueButton('Review',()=>decision(d,'under_review')),queueButton('Discard',()=>decision(d,'discarded'),'discard-action'));
    else actions.append(queueButton('Restore to generated',()=>decision(d,'draft'),'secondary-action'));
    outer.append(actions);
  }
  return outer;
}
function renderWorkspace(){
  const groups=[['draft','studio-results','generated-count','No questions awaiting review. Generate another batch above.'],['under_review','review-queue','review-count','No questions under review. Select Review on any generated question.'],['approved','approved-queue','approved-count','No approved questions yet. Approve questions after checking their solution.'],['discarded','discarded-queue','discarded-count','No discarded questions.']];
  for(const [state,id,countId,empty] of groups){
    const rows=workspaceRows.filter(d=>d.state===state);byId(countId).textContent=String(rows.length);
    byId(id).replaceChildren(...(rows.length?rows.map(queueRow):[el('p',empty,'empty-state')]));
  }
  const approved=approvedRows();byId('approved-marks').textContent=`${markTotal(approved)} marks`;
  byId('pending-count').textContent=String(pendingRows().length);
  updateWorkspaceControls();
}
function makeWorksheet(rows,mode){
  const paper=el('div',undefined,'worksheet-paper');
  const title=byId('worksheet-title').value.trim()||'Foundation Mathematics · Practice worksheet';
  paper.append(el('p','TEACHERS ONLY · ORIGINAL FOUNDATION PRACTICE','worksheet-kicker'),el('h2',title+(mode==='scheme'?' — Mark scheme':'')),el('p',`${rows.length} questions · ${markTotal(rows)} marks · ${[...new Set(rows.map(d=>d.unit))].join(' / ')}`,'worksheet-meta'));
  if(mode==='student')paper.append(el('p','Name: __________________________   Date: ______________','worksheet-name'),el('p','Show your working. Answer all questions.','worksheet-instructions'));
  else paper.append(el('p','Teacher-approved practice. These marking criteria are not an official CCEA mark scheme.','worksheet-instructions'));
  rows.forEach((d,i)=>{
    if(mode==='student'){paper.append(examPreview(d,i+1));return;}
    const block=el('div',undefined,'worksheet-scheme-item'),steps=el('ol'),rubric=el('ul');
    block.append(el('h3',`Question ${i+1} · ${d.marks} marks`),el('p',d.question),el('strong','Answer: '+d.answer));
    for(const step of d.solution)steps.append(el('li',step));for(const rule of d.rubric)rubric.append(el('li',rule));
    block.append(steps,el('strong','Marking criteria'),rubric);paper.append(block);
  });
  return paper;
}
async function prepareWorksheet(mode,print){
  await workspaceTask(async()=>{
    await refreshWorkspace();
    if(pendingRows().length||!approvedRows().length)throw Error('Approve or discard all pending questions before exporting.');
    const rows=approvedRows();worksheetMode=mode;
    if(!print){const target=byId('worksheet-preview');target.replaceChildren(makeWorksheet(rows,mode));target.hidden=false;target.scrollIntoView({block:'start'});return;}
    const target=byId('worksheet-print');target.replaceChildren(makeWorksheet(rows,mode));
    document.body.classList.add('worksheet-printing');
    const cleanup=()=>{document.body.classList.remove('worksheet-printing');target.replaceChildren();};
    window.addEventListener('afterprint',cleanup,{once:true});
    try{window.print();}catch(error){window.removeEventListener('afterprint',cleanup);cleanup();throw error;}
  });
}
function initWorksheet(){
  byId('worksheet-preview-btn').onclick=()=>run(()=>prepareWorksheet('student',false));
  byId('worksheet-export-btn').onclick=()=>run(()=>prepareWorksheet('student',true));
  byId('scheme-export-btn').onclick=()=>run(()=>prepareWorksheet('scheme',true));
  byId('worksheet-title').oninput=()=>{if(worksheetMode&&!byId('worksheet-preview').hidden)byId('worksheet-preview').replaceChildren(makeWorksheet(approvedRows(),worksheetMode));};
  byId('workspace-reload').onclick=()=>run(()=>workspaceTask(async()=>{
    if(workspaceRows.length&&!window.confirm('Clear all questions in this temporary worksheet? This cannot be undone.'))return;
    await resetWorkspace();statusText('Temporary worksheet cleared.');
  }));
  return refreshWorkspace();
}
