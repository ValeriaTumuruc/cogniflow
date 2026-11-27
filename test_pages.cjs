const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
async function main(){
 const calls=[];
 const ctx=vm.createContext({URLSearchParams,Date,console,location:{hostname:'student.github.io',search:'?utm_source=campus'},localStorage:{getItem:()=>null,setItem(){},removeItem(){}},document:{querySelector:()=>null,querySelectorAll:()=>[]},window:{COGNIFLOW_CONFIG:{apiBaseUrl:'https://example.supabase.co/functions/v1/research',publishableKey:'public-test-key'}},fetch:async(url,options)=>{calls.push({url,options});return {ok:true,json:async()=>({ok:true})}}});
 vm.runInContext(fs.readFileSync(path.join(__dirname,'app.js'),'utf8'),ctx);
 await vm.runInContext("request('/api/signup',{email:'test@example.com'})",ctx);
 assert.equal(calls[0].url,'https://example.supabase.co/functions/v1/research/signup');
 assert.equal(calls[0].options.headers.apikey,'public-test-key');
 ctx.window.COGNIFLOW_CONFIG={apiBaseUrl:''};
 await assert.rejects(vm.runInContext("request('/api/signup',{})",ctx),/not connected/);
 ctx.location.hostname='127.0.0.1';
 await vm.runInContext("request('/api/signup',{})",ctx);
 assert.equal(calls[1].url,'/api/signup');
 ctx.fetch=async()=>({ok:false,json:async()=>({error:'Rejected'})});
 await assert.rejects(vm.runInContext("request('/api/signup',{})",ctx),/Rejected/);
 for(const name of ['index.html','privacy.html']){
  const html=fs.readFileSync(path.join(__dirname,name),'utf8');
  assert(!/href="\/(?!\/)/.test(html),`${name}: root-relative link`);
  assert(html.indexOf('config.js')<html.indexOf('app.js'));
 }
 const files=fs.readdirSync(path.join(__dirname,'dist')).sort();
 assert.deepEqual(files,['.nojekyll','app.js','config.js','index.html','mark.svg','privacy.html','styles.css'].sort());
 assert.equal(require('node:crypto').createHash('sha256').update(fs.readFileSync(path.join(__dirname,'styles.css'))).digest('hex'),'046e8dbc9bad2882551e0997ce242502513c05d0ef5880d93397d3f7bfb3d0ce');
 console.log('Passed: hosted API routing, local fallback, honest missing-config errors, API rejection handling, project-path links, public artifact allowlist and unchanged design.');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
