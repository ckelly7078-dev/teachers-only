'use strict';
// Structured selectors read the existing per-unit generator catalogue.
const builderUnits=['M1','M2','M5','M6'];
const builderCatalogs=new Map();
const builderTopics=new Map();
let builderVersion=0, builderLoading=true, builderBusy=false, builderAI=false, builderConfigured=false, builderError='';
const selectedBuilderUnits=()=>[...byId('builder-unit-options').querySelectorAll('input:checked')].map(x=>x.value);
const topicKey=(unit,family)=>unit+':'+family;
function builderSelection(){
  return {units:selectedBuilderUnits(),topics:[...builderTopics.values()],count:Number(byId('builder-count').value),
    difficulty:byId('builder-difficulty').value,mode:byId('builder-mode').value,
    info:byId('builder-mode').value!=='local'?byId('builder-info').value.trim():''};
}
function builderProblem(s){
  if(builderLoading)return 'Loading available topics…';
  if(builderError)return builderError;
  if(!s.units.length)return 'Select at least one assessment unit.';
  if(!s.topics.length)return 'Select the topics you want to practise.';
  if(s.units.some(u=>!s.topics.some(t=>t.unit===u)))return 'Choose at least one topic in each selected unit.';
  if(!Number.isInteger(s.count)||s.count<s.topics.length||s.count>10)return 'Choose 1–10 questions, at least one per selected topic.';
  if(s.mode==='model'&&!builderAI)return 'AI is unavailable. Select local generation.';
  return '';
}
// Native disclosure/radio menus use page typography even when Firefox's
// operating-system select popup is rendered with a much smaller font.
const builderSingleMenus=new Map();
function installBuilderSingleMenu(id){
  const select=byId(id), original=select.parentElement;
  const title=original.firstChild.textContent.trim();
  const field=el('div',undefined,'builder-field builder-single-field');
  const heading=el('span',title,'builder-label');
  heading.id=id+'-label';
  const details=el('details',undefined,'builder-dropdown builder-single-menu');
  const summary=el('summary');summary.id=id+'-summary';
  summary.setAttribute('aria-labelledby',heading.id+' '+summary.id);
  const options=el('div',undefined,'builder-options');
  options.setAttribute('role','radiogroup');options.setAttribute('aria-labelledby',heading.id);
  const controls=[];
  for(const option of select.options){
    const label=el('label',undefined,'builder-choice');
    const radio=el('input');radio.type='radio';radio.name=id+'-choice';radio.value=option.value;
    radio.onchange=()=>{
      if(!radio.checked)return;
      select.value=radio.value;
      updateBuilderControls();
      details.open=false;
      summary.focus();
    };
    label.append(radio,el('span',option.textContent));options.append(label);
    controls.push({radio,option});
  }
  details.append(summary,options);field.append(heading,details);
  original.replaceWith(field);select.hidden=true;select.tabIndex=-1;select.setAttribute('aria-hidden','true');field.append(select);
  details.addEventListener('keydown',e=>{if(e.key==='Escape'){details.open=false;summary.focus();}});
  builderSingleMenus.set(id,{select,details,summary,controls});
}
function syncBuilderSingleMenus(){
  for(const {select,summary,controls} of builderSingleMenus.values()){
    summary.textContent=select.selectedOptions[0]?.textContent||'Choose an option';
    for(const {radio,option} of controls){
      radio.checked=option.selected;radio.disabled=select.disabled||option.disabled;
    }
  }
}
function updateBuilderControls(){
  const s=builderSelection(), error=builderProblem(s);
  byId('builder-unit-summary').textContent=s.units.length?s.units.join(', '):'Choose units';
  byId('builder-topic-summary').textContent=s.topics.length?s.topics.length+' topic'+(s.topics.length===1?'':'s')+' selected':'Choose topics';
  byId('builder-count').min=String(Math.max(1,s.topics.length));
  byId('builder-info').disabled=builderBusy||s.mode==='local';
  byId('builder-ai-option').disabled=!builderAI;
  byId('builder-info-help').textContent=s.mode==='hybrid'?'Hybrid: AI guidance applies only to questions with diagrams. Text-only questions use no API. Diagram artwork is drawn by the maths engine. Do not include pupil data.':s.mode==='model'?'Optional: guide emphasis, numerical choices and available wording variants. Unsupported features may not be possible. Do not include pupil data.':'Optional guidance is only used in AI mode. Local generation costs nothing.';
  byId('builder-gate').textContent=error||`${s.count} questions · ${s.units.length} unit${s.units.length===1?'':'s'} · ${s.topics.length} selected topic${s.topics.length===1?'':'s'}. Each selected topic will be represented.`;
  byId('builder-submit').disabled=builderBusy||!!error;
  for(const id of ['builder-count','builder-difficulty','builder-mode'])byId(id).disabled=builderBusy;
  for(const control of byId('builder-unit-options').querySelectorAll('input'))control.disabled=builderBusy;
  for(const control of byId('builder-topic-options').querySelectorAll('input'))control.disabled=builderBusy||(!control.checked&&s.topics.length>=10);
  byId('builder-retry').hidden=!builderError;
  byId('builder-retry').disabled=builderBusy;
  syncBuilderSingleMenus();
}
function configureBuilderAI(available){
  builderAI=!!available;
  if(!builderConfigured){byId('builder-mode').value=builderAI?'hybrid':'local';builderConfigured=true;}
  if(!builderAI&&byId('builder-mode').value==='model')byId('builder-mode').value='local';
  updateBuilderControls();
}
function renderBuilderTopics(units){
  const panel=byId('builder-topic-options');panel.replaceChildren();
  if(!units.length){panel.append(el('p','Choose assessment units first.','builder-hint'));return;}
  for(const unit of units){
    const rows=builderCatalogs.get(unit)||[];
    const group=el('fieldset',undefined,'builder-topic-group');group.append(el('legend',unit));
    if(!rows.length)group.append(el('p','No validated generator topics available for this unit.','builder-hint'));
    for(const topic of rows){
      const key=topicKey(unit,topic.family), label=el('label',undefined,'builder-choice');
      const check=el('input');check.type='checkbox';check.value=key;check.checked=builderTopics.has(key);
      check.onchange=()=>{
        if(check.checked){if(builderTopics.size>=10){check.checked=false;return;}builderTopics.set(key,{unit,family:topic.family});}
        else builderTopics.delete(key);
        const count=byId('builder-count');if(Number(count.value)<builderTopics.size)count.value=String(builderTopics.size);
        updateBuilderControls();
      };
      const text=el('span');text.append(el('strong',topic.label),el('small',topic.skill_label+' · spec p. '+topic.spec_page));
      label.append(check,text);group.append(label);
    }
    panel.append(group);
  }
}
async function loadBuilderTopics(){
  const version=++builderVersion, units=selectedBuilderUnits();
  for(const [key,t] of builderTopics)if(!units.includes(t.unit))builderTopics.delete(key);
  builderLoading=true;builderError='';byId('builder-topic-options').replaceChildren(el('p','Loading supported topics…','builder-hint'));updateBuilderControls();
  try{
    await Promise.all(units.map(async unit=>{
      if(!builderCatalogs.has(unit)){
        const rows=await api('studio-catalog',{unit});
        if(!Array.isArray(rows)||rows.some(r=>typeof r.family!=='string'||typeof r.label!=='string'))throw Error('Invalid topic catalogue.');
        builderCatalogs.set(unit,rows);
      }
    }));
    if(version!==builderVersion)return;
    renderBuilderTopics(units);
  }catch(error){
    if(version!==builderVersion)return;
    builderError='Could not load topics. Use Reload topics to try again.';
    byId('builder-topic-options').replaceChildren(el('p',builderError,'builder-hint'));
  }finally{
    if(version===builderVersion){builderLoading=false;updateBuilderControls();}
  }
}
async function initBuilder(){
  installBuilderSingleMenu('builder-difficulty');
  installBuilderSingleMenu('builder-mode');
  syncBuilderSingleMenus();
  for(const c of byId('builder-unit-options').querySelectorAll('input'))c.onchange=()=>run(loadBuilderTopics);
  byId('builder-mode').onchange=updateBuilderControls;
  byId('builder-count').oninput=updateBuilderControls;
  byId('builder-retry').onclick=()=>run(loadBuilderTopics);
  byId('assessment-builder').onsubmit=event=>{
    event.preventDefault();
    run(async()=>{
      const settings=builderSelection(), problem=builderProblem(settings);
      if(problem||builderBusy)throw Error(problem||'Generation already in progress.');
      builderBusy=true;updateBuilderControls();
      const feedback=byId('builder-feedback');feedback.textContent=settings.mode==='hybrid'?'Generating text questions locally and using AI only for diagram topics…':settings.mode==='model'?'AI is designing and checking your selected topics…':'Generating and checking your selected topics…';
      try{
        await workspaceTask(async()=>{
          const diagram_history=[...new Set(workspaceRows.map(r=>r.diagram_key).filter(Boolean))];
          const shape_history=[...new Set(workspaceRows.map(r=>r.diagram_shape).filter(Boolean))].slice(-150);
          const rows=await api('studio-mixed',{...settings,diagram_history,shape_history},true);
          await showStudioBatch(rows);
          feedback.textContent=rows.length+' validated questions added to this worksheet.'+(rows[0]?.generation_notice?' '+rows[0].generation_notice:'');
        });
      }catch(error){feedback.textContent=error.message;throw error;}
      finally{builderBusy=false;updateBuilderControls();}
    });
  };
  await loadBuilderTopics();
}
