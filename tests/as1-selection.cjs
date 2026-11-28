'use strict';
// Exercise the actual UI handlers with a small DOM double and deferred requests.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

class Element {
  constructor() {
    this.value = '';
    this.options = [];
    this.events = {};
    this.attrs = {};
    this.classList = {toggle() {}};
  }
  addEventListener(type, handle) { this.events[type] = handle; }
  dispatch(type) { return this.events[type]({preventDefault() {}, currentTarget:this}); }
  append() {}
  add(option) { this.options.push(option); }
  querySelector() { return this.button ??= new Element(); }
  replaceChildren(...options) { this.options = options; this.value = options[0]?.value || ''; }
  setAttribute(name, value) { this.attrs[name] = value; }
  removeAttribute(name) { delete this.attrs[name]; }
  reset() {}
}
const nodes = new Map();
function element(id) {
  if (!nodes.has(id)) nodes.set(id, new Element());
  return nodes.get(id);
}
const pending = [];
class Option { constructor(label, value) { this.value = value; } }
const script = fs.readFileSync(path.join(__dirname, '../further_maths/review_bq.js'), 'utf8');
vm.runInNewContext(script, {document:{getElementById:element, createElement:()=>new Element()},
  Option, URLSearchParams, fetch:(url)=>new Promise(resolve=>pending.push({url,resolve}))});
function respond(route, data) {
  const next = pending.shift();
  assert.ok(next.url.startsWith('api/' + route));
  next.resolve({ok:true, json:async()=>data});
}
const tick = () => new Promise(resolve => setImmediate(resolve));
const record = id => ({item:{id,revision:'fixture',marks:1,payload:{
  question_latex:'Q',final_answer_latex:'A',worked_solution_latex:[],rubric:[]}}});
async function loaded(id) {
  const done = element('browse').dispatch('submit');
  respond('item', record(id));
  await done;
  element('proof').naturalWidth = 900;
  element('proof').dispatch('load');
  assert.equal(element('review').querySelector().disabled, false);
}
async function main() {
  respond('list', {ids:['one','two']});
  await tick();
  await loaded('one');
  element('filter').value='o';
  element('filter').dispatch('input');
  assert.equal(element('preview').hidden, false);
  element('filter').value='two';
  element('filter').dispatch('input');
  assert.equal(element('preview').hidden, true);
  assert.equal(element('review').querySelector().disabled, true);
  const stale = element('browse').dispatch('submit');
  element('filter').value='';
  element('filter').dispatch('input');
  element('item').value='one';
  element('item').dispatch('change');
  respond('item', record('two'));
  await stale;
  assert.equal(element('preview').hidden, true);
  await loaded('one');
  element('item').value='two';
  element('item').dispatch('change');
  assert.equal(element('review').querySelector().disabled, true);
  console.log('4 AS1 selection scenarios passed (mocked DOM)');
}
main().catch(error => {console.error(error); process.exitCode=1;});
