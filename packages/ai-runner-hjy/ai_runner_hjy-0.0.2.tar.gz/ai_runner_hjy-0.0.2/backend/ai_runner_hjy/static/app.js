'use strict';
const $ = (s)=>document.querySelector(s);
const setText = (sel, v)=>{ const el=$(sel); if(el) el.textContent = v; }

window.addEventListener('DOMContentLoaded', ()=>{
  const btnRun = $('#btnRun');
  const statusBar = $('#statusBar');
  const spinner = $('#spinner');
  const timerEl = $('#timer');
  let tickTimer=null, startTs=0;

  function startLoading(){
    btnRun.disabled = true;
    spinner.classList.remove('hidden');
    startTs = performance.now();
    tickTimer = setInterval(()=>{ const t=((performance.now()-startTs)/1000).toFixed(1); timerEl.textContent=`${t}s`; },100);
    statusBar.textContent = '执行中…';
  }
  function stopLoading(){
    btnRun.disabled = false;
    spinner.classList.add('hidden');
    clearInterval(tickTimer); tickTimer=null;
    statusBar.textContent = '就绪';
  }

  async function call(){
    const project = $('#project').value.trim();
    const route = $('#route').value.trim();
    let vars = $('#vars').value.trim();
    try{ vars = vars? JSON.parse(vars): null; }catch(e){ alert('Runtime Variables 不是合法 JSON'); return; }
    const payload = { project_name: project, route_key: route, variables: vars };
    startLoading();
    try{
      const res = await fetch('/invoke', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      const data = await res.json();
      setText('#httpStatus', data.status ?? '-');
      setText('#duration', (data.duration_ms? data.duration_ms+' ms': '-'));
      $('#reqJson').textContent = JSON.stringify(data.request ?? {}, null, 2);
      $('#metaJson').textContent = JSON.stringify(data.meta ?? {}, null, 2);
      $('#respJson').textContent = JSON.stringify(data.response ?? data, null, 2);
      $('#errJson').textContent = JSON.stringify(data.error ?? {}, null, 2);
    }catch(e){
      alert('请求失败：'+ e.message);
    }finally{
      stopLoading();
    }
  }

  btnRun.addEventListener('click', ()=>call());

  document.querySelectorAll('button.copy').forEach(btn=>{
    btn.addEventListener('click', (e)=>{
      const sel = btn.getAttribute('data-copy');
      const el = document.querySelector(sel);
      if(el){ navigator.clipboard.writeText(el.textContent||''); btn.textContent='已复制'; setTimeout(()=>btn.textContent='复制',1200); }
    });
  });
});