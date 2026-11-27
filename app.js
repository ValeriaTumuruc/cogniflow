const $ = (s) => document.querySelector(s);
const safeStore = { get(k) { try { return localStorage.getItem(k); } catch { return null; } }, set(k,v) { try { localStorage.setItem(k,v); } catch {} }, remove(k) { try { localStorage.removeItem(k); } catch {} } };
let choice;
try { choice = JSON.parse(safeStore.get('cogniflow-measurement')); } catch {}
if (!choice || choice.expires < Date.now()) { choice = null; safeStore.remove('cogniflow-measurement'); }
const params = new URLSearchParams(location.search);
const channel = (params.get('utm_source') || 'direct').replace(/[^a-zA-Z0-9_-]/g,'').slice(0,60) || 'direct';
async function request(path, body) {
 const config = window.COGNIFLOW_CONFIG || {};
 const local = ['localhost','127.0.0.1'].includes(location.hostname);
 const base = String(config.apiBaseUrl || (local ? '/api' : '')).replace(/\/$/, '');
 if (!base) throw new Error('Registration is not connected yet. Please try again once the research page is ready.');
 const endpoint = base + path.replace(/^\/api/, '');
 let response;
 try { response = await fetch(endpoint, {method:'POST',headers:{'Content-Type':'application/json', ...(config.publishableKey ? {apikey:config.publishableKey} : {})},body:JSON.stringify(body)}); }
 catch { throw new Error('Could not reach the registration service. Check your connection and try again.'); }
 let result; try { result = await response.json(); } catch { throw new Error('The registration service returned an unexpected response. Please try again later.'); }
 if (!response.ok) throw new Error(result.error || 'We could not save this. Please try again.');
 return result;
}
let visitSaved = false;
let pendingVisit;
async function count(event) {
 if (!choice?.allowed) return false;
 if (event === 'visit' && pendingVisit) return pendingVisit;
 const send = async () => { try {
   await request('/api/event', {visitor:choice.id, channel, event, eligible:true});
   if (event === 'visit') visitSaved = true;
   return true;
 } catch { return false; } };
 if (event === 'visit') { pendingVisit = send(); const ok = await pendingVisit; pendingVisit = null; return ok; }
 return send();
}
if ($('#measurement')) {
 $('#measurement').hidden = Boolean(choice);
 $('#allow-measurement').onclick = () => { choice = {allowed:true,id:crypto.randomUUID(),expires:Date.now()+30*86400000};safeStore.set('cogniflow-measurement',JSON.stringify(choice));$('#measurement').hidden=true;count('visit'); };
 $('#decline-measurement').onclick = () => { choice={allowed:false,expires:Date.now()+30*86400000};safeStore.set('cogniflow-measurement',JSON.stringify(choice));$('#measurement').hidden=true; };
 $('#measurement-settings').onclick = () => { $('#measurement').hidden=false; $('#allow-measurement').focus(); };
 count('visit');
}
document.querySelectorAll('[data-cta]').forEach(a=>a.addEventListener('click',()=>count('cta')));
const suggestions = {low:['A little room to reset','A short pause might help. Stand up, get some water and decide what feels manageable next.'],okay:['Keep the choice yours','Carry on if it feels right. You can choose when a reminder appears or turn it off.']};
document.querySelectorAll('[data-energy]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-energy]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));const s=suggestions[b.dataset.energy];$('#suggestion .suggestion-label').textContent=s[0];$('#suggestion p').textContent=s[1];}));
if ($('#signup-form')) $('#signup-form').addEventListener('submit',async e=>{
 e.preventDefault();const form=e.currentTarget;const status=$('#form-status');const button=form.querySelector('[type=submit]');
 if(!form.reportValidity()) return;
 button.disabled=true;button.textContent='Saving your registration…';status.textContent='';$('#withdrawal').hidden=true;
 try {if(choice?.allowed && !visitSaved) await count('visit'); const data=await request('/api/signup',{email:form.email.value,programme:form.programme.value,eligible:form.eligible.checked,consent:form.consent.checked,website:form.website.value,channel,visitor:choice?.allowed?choice.id:null});status.textContent='Thank you. Your request has been received. If this address was already registered, we’ve kept the existing registration.';
 if(data.withdrawal){$('#withdrawal-code').textContent=data.withdrawal;$('#withdrawal').hidden=false;}form.reset();}
 catch(err){status.textContent=err.message || 'Registration could not be saved. Check your connection and try again.';}
 finally{button.disabled=false;button.textContent='Join the testing list';status.focus();}
});
if ($('#copy-code')) $('#copy-code').onclick = async()=>{try{await navigator.clipboard.writeText($('#withdrawal-code').textContent);$('#copy-code').textContent='Copied';}catch{$('#copy-code').textContent='Select and copy the code above';}};
if ($('#withdraw-form')) $('#withdraw-form').onsubmit=async e=>{e.preventDefault();const status=$('#withdraw-status');try{await request('/api/withdraw',{token:$('#token').value.trim()});status.textContent='Withdrawal processed. Any registration matching this code has been removed.';e.target.reset();}catch(err){status.textContent=err.message;}status.focus();};

if ($('#load-prototype')) $('#load-prototype').addEventListener('click', () => {
 const stage = $('#prototype-stage');
 const frame = document.createElement('iframe');
 frame.src = stage.dataset.src;
 frame.title = 'Cogniflow Figma prototype with sample study and well-being screens';
 frame.allow = 'fullscreen';
 frame.referrerPolicy = 'strict-origin-when-cross-origin';
 stage.replaceChildren(frame);
});
const hostedRegistrationReady = Boolean(window.COGNIFLOW_CONFIG?.apiBaseUrl);
const localPreview = ['localhost','127.0.0.1'].includes(location.hostname);
if (!hostedRegistrationReady && !localPreview) {
 if ($('#signup-form')) $('#signup-form').hidden = true;
 if ($('#signup-unavailable')) $('#signup-unavailable').hidden = false;
 if ($('#measurement')) $('#measurement').hidden = true;
 if ($('#measurement-settings')) $('#measurement-settings').hidden = true;
}
