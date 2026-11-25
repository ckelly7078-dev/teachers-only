'use strict';
// Render only the bounded geometry contract, never SVG strings or HTML.
function renderStudioDiagram(diagram) {
  if (!diagram || diagram.kind !== 'schematic') return null;
  const point = p => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite) &&
    p[0] >= 0 && p[0] <= 480 && p[1] >= 0 && p[1] <= 280;
  if (!Array.isArray(diagram.polygon) || diagram.polygon.length < 3 || diagram.polygon.length > 12 ||
      !diagram.polygon.every(point) || !Array.isArray(diagram.lines) || diagram.lines.length > 12 ||
      !diagram.lines.every(l=>Array.isArray(l) && l.length===4 && point(l.slice(0,2)) && point(l.slice(2))) ||
      !Array.isArray(diagram.labels) || diagram.labels.length > 10 ||
      !diagram.labels.every(l=>Array.isArray(l) && l.length===3 && point(l.slice(0,2)) && typeof l[2]==='string' && l[2].length<=60) ||
      typeof diagram.alt !== 'string' || diagram.alt.length>180) return null;
  const wrap=document.createElement('figure');
  wrap.className='studio-diagram';
  const ns='http://www.w3.org/2000/svg';
  function element(tag,attrs,text) {
    const node=document.createElementNS(ns,tag);
    for(const [key,value] of Object.entries(attrs)) node.setAttribute(key,String(value));
    if(text!==undefined) node.textContent=text;
    return node;
  }
  const svg=element('svg',{viewBox:'0 0 480 280',role:'img','aria-label':diagram.alt,width:'100%',height:'auto'});
  svg.append(element('polygon',{points:diagram.polygon.map(p=>p.join(',')).join(' '),fill:'#e5edf8',stroke:'#17365d','stroke-width':2.5,'stroke-linejoin':'round'}));
  for(const [x1,y1,x2,y2] of diagram.lines) svg.append(element('line',{x1,y1,x2,y2,stroke:'#17365d','stroke-width':2,'stroke-linecap':'round'}));
  for(const [x,y,text] of diagram.labels) svg.append(element('text',{x,y,fill:'#14284b','font-size':14,'font-family':'Arial, sans-serif','text-anchor':'middle'},text));
  wrap.append(svg);
  const caption=document.createElement('figcaption');
  caption.textContent='Diagram not drawn to scale.';
  wrap.append(caption);
  return wrap;
}
