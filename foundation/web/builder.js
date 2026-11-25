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
    info:byId('builder-mode').value==='model'?byId('builder-info').value.trim():''};
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
function updateBuilderControls(){
  const s=builderSelection(), error=builderProblem(s);
  byId('builder-unit-summary').textContent=s.units.length?s.units.join(', '):'Choose units';
  byId('builder-topic-summary').textContent=s.topics.length?s.topics.length+' topic'+(s.topics.length===1?'':'s')+' selected':'Choose topics';
  byId('builder-count').min=String(Math.max(1,s.topics.length));
  byId('builder-info').disabled=builderBusy||s.mode!=='model';
  byId('builder-ai-option').disabled=!builderAI;
  byId('builder-info-help').textContent=s.mode==='model'?'Optional: guide emphasis, numerical choices and available wording variants. Unsupported features may not be possible. Do not include pupil data.':'Optional guidance is only used in AI mode. Local generation costs nothing.';
  byId('builder-gate').textContent=error||`${s.count} questions · ${s.units.length} unit${s.units.length===1?'':'s'} · ${s.topics.length} selected topic${s.topics.length===1?'':'s'}. Each selected topic will be represented.`;
  byId('builder-submit').disabled=builderBusy||!!error;
  for(const id of ['builder-count','builder-difficulty','builder-mode'])byId(id).disabled=builderBusy;
  for(const control of byId('builder-unit-options').querySelectorAll('input'))control.disabled=builderBusy;
  for(const control of byId('builder-topic-options').querySelectorAll('input'))control.disabled=builderBusy||(!control.checked&&s.topics.length>=10);
  byId('builder-retry').hidden=!builderError;
  byId('builder-retry').disabled=builderBusy;
}
function configureBuilderAI(available){
  builderAI=!!available;
  if(!builderConfigured){byId('builder-mode').value=builderAI?'model':'local';builderConfigured=true;}
  if(!builderAI)byId('builder-mode').value='local';
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
      const feedback=byId('builder-feedback');feedback.textContent=settings.mode==='model'?'AI is designing and checking your selected topics…':'Generating and checking your selected topics…';
      try{
        await workspaceTask(async()=>{
          const rows=await api('studio-mixed',settings,true);
          await showStudioBatch(rows);
          feedback.textContent=rows.length+' validated questions added to this worksheet.'+(rows[0]?.generation_notice?' '+rows[0].generation_notice:'');
        });
      }catch(error){feedback.textContent=error.message;throw error;}
      finally{builderBusy=false;updateBuilderControls();}
    });
  };
  await loadBuilderTopics();
}
