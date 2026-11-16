// Execute the real generated payload and page code against a small DOM adapter.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync('docs/index.html','utf8');
class Element {
  constructor(id=''){this.id=id;this.children=[];this.style={};this.dataset={};this.events={};this.attrs={};this.html='';}
  set innerHTML(s){this.html=s;this.children=[];}
  get innerHTML(){return this.html;}
  appendChild(e){this.children.push(e);return e;}
  setAttribute(k,v){this.attrs[k]=v;}
  addEventListener(k,v){this.events[k]=v;}
  querySelector(){if(!this.input)this.input=new Element();return this.input;}
  closest(){return this;}
  getBoundingClientRect(){return {left:0,top:0,width:820};}
}
const ids=new Map(),get=id=>{if(!ids.has(id))ids.set(id,new Element(id));return ids.get(id)};
const stats=[...html.matchAll(/data-stat="([^"]+)"/g)].map(m=>{const e=new Element();e.dataset.stat=m[1];return e});
const document={getElementById:get,createElement:()=>new Element(),createElementNS:()=>new Element(),querySelectorAll:s=>s==='[data-stat]'?stats:[get('tab-podium'),get('tab-spokojna')]};
const context=vm.createContext({document,console});
vm.runInContext(fs.readFileSync('docs/results.js','utf8'),context);
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
assert.equal(get('yearrows').children.length,23);
assert.equal(get('buyrows').children.length,9); // 3 buys, total, 5 reserves
assert.ok(stats.every(e=>e.textContent!==undefined && e.textContent!==''));
for(const strat of ['podium','spokojna']){
 vm.runInContext(`cur='${strat}';render()`,context);
 const total=vm.runInContext(`STR[cur].buy.reduce((s,k)=>{const p=limitOf(PX[k]);return s+shares(CAP/STR[cur].n,p)*p*(1+FEE)},0)`,context);
 assert.ok(total<=20000);
}
assert.equal(get('buyrows').children.length,16);
// A price containing a Polish thousands separator must be parsed completely.
const row=get('buyrows').children[0];row.input.events.change({target:{value:'1 234,50'}});
assert.equal(vm.runInContext("limits[cur+STR[cur].buy[0]]",context),1234.5);
console.log('Page smoke: both tabs, 23 years, generated stats, budgets and price editing OK');
