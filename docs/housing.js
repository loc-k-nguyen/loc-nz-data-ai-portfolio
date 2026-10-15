'use strict';

const byId = (id) => document.getElementById(id);
const number = (value) => value == null ? 'Not available' : new Intl.NumberFormat('en-NZ', {maximumFractionDigits: 2}).format(value);
const dateLabel = (date) => new Date(`${date}T00:00:00Z`).toLocaleDateString('en-NZ', {day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC'});
let dataset;
const displayValue = (series, value) => value == null ? null : series.displayScale ? Number((value * series.displayScale).toPrecision(12)) : value;
const formattedValue = (series, value) => number(displayValue(series, value));

function option(select, value, label) {
  const node = document.createElement('option'); node.value = value; node.textContent = label; select.append(node);
}
function current() { return dataset.series.find((item) => item.id === byId('indicator').value); }
function rowsAt(series, period) { return series.values.filter(([date, geo]) => date === period && geo === 'TA').sort((a,b) => b[3]-a[3]); }
function cell(row, text) { const node = document.createElement('td'); node.textContent = text; row.append(node); }

function resetPeriods() {
  const dates = [...new Set(current().values.filter((row) => row[1] === 'TA').map((row) => row[0]))].sort().reverse();
  byId('period').replaceChildren(); dates.forEach((date) => option(byId('period'), date, dateLabel(date))); render();
}

function renderTrend(series, area) {
  const root = byId('trend'); root.replaceChildren();
  const history = series.values.filter((row) => row[1] === 'TA' && row[2] === area);
  const national = series.values.filter((row) => row[1] === 'NZ');
  byId('history-body').replaceChildren();
  for (const [date,,,value] of history) { const row=document.createElement('tr'); cell(row,dateLabel(date)); cell(row,formattedValue(series,value)); byId('history-body').append(row); }
  if (history.length < 2) { const p=document.createElement('p'); p.className='empty'; p.textContent=history.length ? 'This extract contains one observation for this area and measure. A trend cannot be inferred.' : 'This extract has no observations for this area and measure.'; root.append(p); return; }
  const all=[...history,...national];
  const times=all.map((row)=>Date.parse(row[0])); const minX=Math.min(...times), maxX=Math.max(...times);
  const maxY=Math.max(...all.map((row)=>row[3])); const minY=Math.min(0,...all.map((row)=>row[3]));
  const x=(date)=>55+(Date.parse(date)-minX)/(maxX-minX||1)*390;
  const y=(value)=>195-(value-minY)/(maxY-minY||1)*160;
  const ns='http://www.w3.org/2000/svg';
  const svg=document.createElementNS(ns,'svg'); svg.setAttribute('viewBox','0 0 470 240'); svg.setAttribute('role','img'); svg.setAttribute('aria-label',`Reported ${series.label} for ${dataset.areas[area]} and available national observations. Exact local values are in the history table.`);
  const add=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v)); if(text!==undefined)e.textContent=text;svg.append(e);return e;};
  [0,.5,1].forEach((fraction)=>{const value=minY+fraction*(maxY-minY);add('line',{x1:55,x2:445,y1:y(value),y2:y(value),stroke:'#d9ddd3'});add('text',{x:48,y:y(value)+4,'text-anchor':'end',fill:'#5b6861','font-size':10},formattedValue(series,value));});
  for (const [values,color] of [[national,'#8b9f7e'],[history,'#173c34']]) {
    if (!values.length) continue;
    add('polyline',{points:values.map(([date,,,value])=>`${x(date)},${y(value)}`).join(' '),fill:'none',stroke:color,'stroke-width':2});
    values.forEach(([date,,,value])=>{const dot=add('circle',{cx:x(date),cy:y(value),r:2.2,fill:color}); const title=document.createElementNS(ns,'title'); title.textContent=`${date}: ${formattedValue(series,value)}`;dot.append(title);});
  }
  add('text',{x:55,y:222,fill:'#5b6861','font-size':10},dateLabel(new Date(minX).toISOString().slice(0,10)));
  add('text',{x:445,y:222,'text-anchor':'end',fill:'#5b6861','font-size':10},dateLabel(new Date(maxX).toISOString().slice(0,10)));
  root.append(svg); const legend=document.createElement('div');legend.className='legend';
  [dataset.areas[area],...(national.length?['New Zealand']:[])].forEach((text)=>{const span=document.createElement('span');span.textContent=text;legend.append(span);});root.append(legend);
}

function render() {
  const series=current(), period=byId('period').value, area=byId('area').value;
  const rows=rowsAt(series,period); const selected=rows.find((row)=>row[2]===area);
  const national=series.values.find((row)=>row[0]===period&&row[1]==='NZ');
  byId('definition').textContent=series.note;
  byId('area-label').textContent=dataset.areas[area];byId('area-value').textContent=formattedValue(series,selected?.[3]);byId('unit-label').textContent=series.displayUnit;
  byId('national-value').textContent=formattedValue(series,national?.[3]);byId('coverage').textContent=`${rows.length} / ${Object.keys(dataset.areas).length}`;
  byId('trend-title').textContent=`${dataset.areas[area]} over time`;
  byId('table-caption').textContent=`${series.label} · ${series.displayUnit} · ${dateLabel(period)}. Values sorted high to low; no missing area is assigned zero.`;
  byId('bars').replaceChildren();
  const bars=rows.slice(0,8);if(selected&&!bars.includes(selected))bars.push(selected);
  const max=Math.max(...rows.map((row)=>Math.abs(row[3])),1);
  for(const row of bars){const wrap=document.createElement('div');wrap.className=`bar-row${row[2]===area?' selected':''}`;const label=document.createElement('div');label.className='bar-label';const name=document.createElement('span');name.textContent=dataset.areas[row[2]];const value=document.createElement('span');value.textContent=formattedValue(series,row[3]);label.append(name,value);const track=document.createElement('div');track.className='bar-track';track.setAttribute('aria-hidden','true');const fill=document.createElement('div');fill.className='bar-fill';fill.style.width=`${Math.abs(row[3])/max*100}%`;track.append(fill);wrap.append(label,track);byId('bars').append(wrap);}
  byId('table-body').replaceChildren();for(const record of rows){const row=document.createElement('tr');if(record[2]===area)row.className='selected';cell(row,dataset.areas[record[2]]);cell(row,formattedValue(series,record[3]));cell(row,dateLabel(record[0]));byId('table-body').append(row);}
  renderTrend(series,area);
}

function download() {
  const series=current(), area=byId('area').value;
  const quote=(value)=>`"${String(value).replaceAll('"','""')}"`;
  const rows=[['period','geography','indicator','unit','value','source_vintage','source_value','source_unit_label'],...series.values.filter((row)=>row[1]==='TA'&&row[2]===area).map(([date,,,value])=>[date,dataset.areas[area],series.name,series.displayUnit,displayValue(series,value),dataset.source.vintage,value,series.unit])];
  const url=URL.createObjectURL(new Blob([rows.map((row)=>row.map(quote).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download=`housing-${series.id}-${area}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

fetch('data.json').then((response)=>{if(!response.ok)throw new Error('Data unavailable');return response.json();}).then((data)=>{
  dataset=data;data.series.forEach((item)=>option(byId('indicator'),item.id,item.label));Object.entries(data.areas).sort((a,b)=>a[1].localeCompare(b[1])).forEach(([id,name])=>option(byId('area'),id,name));
  const wellington=Object.keys(data.areas).find((id)=>data.areas[id]==='Wellington City');if(wellington)byId('area').value=wellington;
  byId('quality-note').textContent=`${number(data.quality.sourceRows)} source rows across ${data.quality.territorialAuthorities} territorial authorities. The source has ${data.quality.sourceDuplicateKeys} duplicate reporting keys in other series. The five displayed series pass numeric and unique-key checks. No duplicate records are silently averaged.`;
  byId('indicator').addEventListener('change',resetPeriods);byId('area').addEventListener('change',render);byId('period').addEventListener('change',render);byId('download').addEventListener('click',download);
  resetPeriods();byId('explorer').hidden=false;byId('load-state').hidden=true;
}).catch(()=>{byId('load-state').textContent='The dashboard data could not load. Please reload, or use the source CSV and SQL in the project repository.';});
