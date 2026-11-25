'use strict';
// Render only the bounded geometry contract, never SVG strings or HTML.
function renderStudioDiagram(diagram) {
  if (!diagram || diagram.kind !== 'schematic') return null;
  const point = p => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite) &&
    p[0] >= 0 && p[0] <= 480 && p[1] >= 0 && p[1] <= 280;
  const validLines = (lines, max) => Array.isArray(lines) && lines.length <= max &&
    lines.every(l=>Array.isArray(l) && l.length===4 && point(l.slice(0,2)) && point(l.slice(2)));
  const dimensions=diagram.dimension_lines===undefined?[]:diagram.dimension_lines;
  const guides=diagram.guides===undefined?[]:diagram.guides;
  if (!validLines(dimensions,16)||!validLines(guides,8)) return null;
  if (!Array.isArray(diagram.polygon) || diagram.polygon.length < 3 || diagram.polygon.length > 12 ||
      !diagram.polygon.every(point) || !Array.isArray(diagram.lines) || diagram.lines.length > 12 ||
      !diagram.lines.every(l=>Array.isArray(l) && l.length===4 && point(l.slice(0,2)) && point(l.slice(2))) ||
      !Array.isArray(diagram.labels) || diagram.labels.length > 10 ||
      !diagram.labels.every(l=>Array.isArray(l) && l.length===3 && point(l.slice(0,2)) && typeof l[2]==='string' && l[2].length<=60) ||
      typeof diagram.alt !== 'string' || diagram.alt.length>180) return null;
  const angles=diagram.label_angles===undefined?diagram.labels.map(()=>0):diagram.label_angles;
  if(!Array.isArray(angles)||angles.length!==diagram.labels.length||!angles.every(a=>Number.isFinite(a)&&a>=-90&&a<=90))return null;
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
  svg.append(element('polygon',{points:diagram.polygon.map(p=>p.join(',')).join(' '),fill:'#eef2f6',stroke:'#152941','stroke-width':2.3,'stroke-linejoin':'round'}));
  for(const [x1,y1,x2,y2] of guides) svg.append(element('line',{x1,y1,x2,y2,stroke:'#6b7280','stroke-width':1.2,'stroke-dasharray':'5 4'}));
  for(const [x1,y1,x2,y2] of dimensions) svg.append(element('line',{x1,y1,x2,y2,stroke:'#475569','stroke-width':1.15}));
  for(const [x1,y1,x2,y2] of diagram.lines) svg.append(element('line',{x1,y1,x2,y2,stroke:'#17365d','stroke-width':2,'stroke-linecap':'round'}));
  for(const [i,[x,y,text]] of diagram.labels.entries()) svg.append(element('text',{x,y,transform:'rotate('+angles[i]+' '+x+' '+y+')',fill:'#14284b','font-size':16,'font-family':'Arial, sans-serif','font-weight':500,'text-anchor':'middle','paint-order':'stroke','stroke':'#f7f9fc','stroke-width':3,'stroke-linejoin':'round'},text));
  wrap.append(svg);
  const caption=document.createElement('figcaption');
  caption.textContent=dimensions.length?'Use the labelled measurements; do not measure the diagram.':'Diagram not drawn to scale.';
  wrap.append(caption);
  return wrap;
}
