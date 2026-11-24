const fs=require('node:fs');
const assert=require('node:assert/strict');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
const script=html.match(/<script>([\s\S]*)<\/script>/)[1];
const app={innerHTML:''}, label={textContent:''}, store={};
const document={getElementById:id=>id==='app'?app:id==='workspace-label'?label:null};
const localStorage={getItem:k=>store[k]??null,setItem:(k,v)=>store[k]=v};
const checks=`
let count=0;
function check(name,condition){assert.ok(condition,name);count++}
check('role only',($().innerHTML.match(/<button/g)||[]).length===1);
go('staffsignin');check('sign-in',$().innerHTML.includes('Mr Stephenson'));
go('staffhome');check('dashboard',($().innerHTML.match(/staff-tile/g)||[]).length===9&&$().innerHTML.includes('Completion'));
for(const id of Object.keys(staffModules)){go('staff:'+id);check('route '+id,$().innerHTML.includes('Back to workspace'))}
go('staff:classes');check('initial progress',statsFor([data.classes[0]]).rate===50);
check('create class',addClass('Year 12A','Physics'));const cid=currentClass().id;
check('reject duplicate',!addClass('Year 12A','Physics'));
check('add learner',addPupil(cid,'Student Z'));const pid=currentClass().pupils[0].id;
check('create assignment',addAssignment(cid,'Practice','2026-12-01'));const aid=data.assignments.at(-1).id;
check('initial record',recordFor(assignmentFor(aid),pid).status==='Not started');
check('reject invalid score',!updateRecord(aid,pid,'Completed',101));
check('record score',updateRecord(aid,pid,'Completed',90));
check('class stats',statsFor([currentClass()]).rate===100&&statsFor([currentClass()]).average===90);
check('resource',addResource('New resource','Physics','Lesson activity','Example'));const rid=data.resources.at(-1).id;
check('link resource',addAssignment(cid,'New resource','',rid));
check('assignment relation',data.assignments.at(-1).resourceId===rid);
persist();check('reload',loadData().classes.some(c=>c.id===cid));
go('role');go('student');check('other role rejected',view==='role');
return count;`;
const count=new Function('document','window','localStorage','assert',script+'\n'+checks)(document,{scrollTo(){}},localStorage,assert);
console.log(count+' smoke checks passed (mocked DOM)');
