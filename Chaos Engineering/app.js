const active = new Set();
const base = { availability: '99.98%', success: '99.7%', latency: '142 ms', budget: '86%', score: '99.8' };
const effects = {
  latency: {availability:-.02,success:-.4,latency:1450,budget:-12,score:-5, service:'payment', state:'degraded', circuit:'HALF-OPEN', retry:'3 рет қайталау', fallback:'Дайын', scaling:'1 replica'},
  failure: {availability:-.08,success:-1.1,latency:88,budget:-22,score:-10, service:'inventory', state:'protected', circuit:'CLOSED', retry:'Қалыпты', fallback:'CACHE ACTIVE', scaling:'1 replica'},
  network: {availability:-.20,success:-2.5,latency:690,budget:-31,score:-18, service:'gateway', state:'degraded', circuit:'OPEN', retry:'Exponential backoff', fallback:'Gateway жауап', scaling:'1 replica'},
  overload: {availability:-.12,success:-.9,latency:420,budget:-18,score:-11, service:'order', state:'protected', circuit:'CLOSED', retry:'Қалыпты', fallback:'Дайын', scaling:'3 replicas'}
};
const el=id=>document.getElementById(id);
function stamp(){return new Date().toLocaleTimeString('kk-KZ',{hour12:false});}
function log(text){const item=document.createElement('li');item.innerHTML=`<time>${stamp()}</time><span>${text}</span>`;el('log').prepend(item);}
function resetServices(){document.querySelectorAll('.service').forEach(s=>s.className='service healthy');}
function render(){
  let a=99.98,s=99.7,l=142,b=86,score=99.8; let circuit='CLOSED',retry='Қалыпты',fallback='Дайын',scaling='1 replica'; resetServices();
  active.forEach(type=>{const e=effects[type];a+=e.availability;s+=e.success;l=Math.max(l,e.latency);b+=e.budget;score+=e.score;el(e.service).className=`service ${e.state}`;circuit=e.circuit==='OPEN'?'OPEN':circuit;retry=e.retry==='Қалыпты'?retry:e.retry;fallback=e.fallback==='Дайын'?fallback:e.fallback;scaling=e.scaling==='1 replica'?scaling:e.scaling;});
  el('availability').textContent=`${a.toFixed(2)}%`;el('success').textContent=`${s.toFixed(1)}%`;el('latency').textContent=`${l} ms`;el('budget').textContent=`${Math.max(0,b)}%`;el('score').textContent=Math.max(0,score).toFixed(1);
  el('availabilityNote').textContent=a>=99.9?'SLO: ≥ 99.9%':'SLO БҰЗЫЛДЫ';el('successNote').textContent=s>=99?'Жақсы':'Төмендеді';el('latencyNote').textContent=l<=500?'Бюджет: 500 ms':'Latency budget exceeded';el('budgetNote').textContent=b>30?'Қауіпсіз аймақ':'ШЕКТІ АЙМАҚ';
  ['availabilityNote','successNote','latencyNote','budgetNote'].forEach(id=>el(id).className=(a<99.9||s<99||l>500||b<=30)?'bad':'ok');
  el('circuit').textContent=circuit;el('retry').textContent=retry;el('fallback').textContent=fallback;el('scaling').textContent=scaling;el('circuit').className=circuit==='OPEN'?'danger':circuit==='HALF-OPEN'?'warn':'';el('fallback').className=fallback.includes('ACTIVE')?'warn':'';
  const failure=Math.min(145,active.size*23+(active.has('network')?25:0)); el('successLine').setAttribute('points',`0,15 60,14 120,15 180,13 240,15 300,${15+failure} 360,${18+failure*.55} 420,${14+failure*.3} 480,${16+failure*.18} 540,15 600,14`);
  el('activeCount').textContent=`${active.size} белсенді`;const problematic=active.size>0;el('stateText').textContent=problematic?'Тәжірибе орындалуда':'Жүйе қалыпты';el('stateDot').style.background=problematic?'var(--yellow)':'var(--green)';el('stateDot').style.boxShadow=problematic?'0 0 10px var(--yellow)':'0 0 10px var(--green)';
}
document.querySelectorAll('.experiment').forEach(btn=>btn.addEventListener('click',()=>{const t=btn.dataset.type;if(active.has(t)){active.delete(t);btn.classList.remove('active');log(`${btn.querySelector('b').textContent}: эксперимент тоқтатылды.`)}else{active.add(t);btn.classList.add('active');log(`${btn.querySelector('b').textContent}: fault injection басталды.`)}render();}));
el('resetBtn').onclick=()=>{active.clear();document.querySelectorAll('.experiment').forEach(b=>b.classList.remove('active'));log('Барлық fault injection тоқтатылды. Жүйе baseline күйіне келді.');render();};
el('clearLog').onclick=()=>el('log').innerHTML='';render();
