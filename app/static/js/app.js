document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('[data-confirm]').forEach(b=>b.addEventListener('click',e=>{if(!confirm(b.dataset.confirm))e.preventDefault()}));
  const form=document.querySelector('#orderForm'); if(!form)return;
  const recalc=()=>{let total=0;form.querySelectorAll('tr[data-price]').forEach(r=>{const cents=Number(r.dataset.price),type=r.dataset.type,q=Number(r.querySelector('.qty-input').value||0);let line=type==='unit'?cents*Math.floor(q):cents*q; if(type==='unit'&&q%1!==0)line=0; total+=line;r.querySelector('.line-total').textContent='$'+(line/100).toFixed(2)});document.querySelector('#orderTotal').textContent='$'+(total/100).toFixed(2)};
  form.querySelectorAll('.qty-input').forEach(i=>i.addEventListener('input',recalc));recalc();
});
