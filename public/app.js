/* ===== Igotdomain — shared script ===== */

// ---- Soft Aurora hero background (teal & white) ----
(function(){
  const canvas = document.getElementById('softAurora');
  if (!canvas) return;
  const gl = canvas.getContext('webgl', { alpha: false, antialias: true });
  if (!gl) {
    canvas.style.background = 'radial-gradient(ellipse at 30% 25%, #99F6E4 0%, transparent 55%), radial-gradient(ellipse at 75% 20%, #5eead4 0%, transparent 55%), #ffffff';
    return;
  }
  const vert = 'attribute vec2 position; void main(){ gl_Position = vec4(position,0.0,1.0); }';
  const frag = `
    precision highp float;
    uniform float uTime; uniform vec2 uResolution;
    float blob(vec2 uv, vec2 c, float r, float a){ vec2 d=uv-c; d.x*=a; return smoothstep(r,0.0,length(d)); }
    void main(){
      vec2 uv = gl_FragCoord.xy/uResolution; float aspect=uResolution.x/uResolution.y; float t=uTime*0.09;
      vec3 white=vec3(1.0);
      vec3 tealPale=vec3(0.776,0.980,0.937);
      vec3 tealLight=vec3(0.376,0.918,0.831);
      vec3 teal=vec3(0.078,0.722,0.651);
      vec2 c1=vec2(0.28+0.10*sin(t*0.9),0.74+0.06*cos(t*0.7));
      vec2 c2=vec2(0.72+0.08*cos(t*0.8),0.58+0.08*sin(t*0.6));
      vec2 c3=vec2(0.50+0.12*sin(t*0.5+1.0),0.90+0.05*cos(t*0.9));
      vec2 c4=vec2(0.86+0.07*sin(t*0.7+2.0),0.80+0.06*cos(t*0.5));
      vec2 c5=vec2(0.14+0.09*cos(t*0.6+3.0),0.50+0.07*sin(t*0.8));
      float b1=blob(uv,c1,0.52,aspect), b2=blob(uv,c2,0.46,aspect), b3=blob(uv,c3,0.40,aspect), b4=blob(uv,c4,0.38,aspect), b5=blob(uv,c5,0.34,aspect);
      vec3 col=white;
      col=mix(col,tealPale,b1*0.85); col=mix(col,tealLight,b2*0.55); col=mix(col,tealPale,b3*0.70); col=mix(col,teal,b4*0.32); col=mix(col,tealLight,b5*0.40);
      col=mix(white,col,0.92);
      gl_FragColor=vec4(col,1.0);
    }`;
  function compile(t,s){ const sh=gl.createShader(t); gl.shaderSource(sh,s); gl.compileShader(sh); return sh; }
  const prog=gl.createProgram();
  gl.attachShader(prog,compile(gl.VERTEX_SHADER,vert));
  gl.attachShader(prog,compile(gl.FRAGMENT_SHADER,frag));
  gl.linkProgram(prog); gl.useProgram(prog);
  const buf=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,buf);
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
  const pos=gl.getAttribLocation(prog,'position'); gl.enableVertexAttribArray(pos); gl.vertexAttribPointer(pos,2,gl.FLOAT,false,0,0);
  const uTime=gl.getUniformLocation(prog,'uTime'), uRes=gl.getUniformLocation(prog,'uResolution');
  const DPR=Math.min(window.devicePixelRatio||1,2);
  function resize(){ const r=canvas.getBoundingClientRect(); canvas.width=Math.max(1,r.width*DPR|0); canvas.height=Math.max(1,r.height*DPR|0); gl.viewport(0,0,canvas.width,canvas.height); gl.uniform2f(uRes,canvas.width,canvas.height); }
  let rt; window.addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(resize,120);}); resize();
  const start=performance.now();
  (function render(){ gl.uniform1f(uTime,(performance.now()-start)/1000); gl.drawArrays(gl.TRIANGLES,0,3); requestAnimationFrame(render); })();
})();

// ---- Onboarding email modal ----
function openModal(){ const m=document.getElementById('modalOverlay'); if(m){ m.classList.add('open'); document.body.style.overflow='hidden'; } }
function closeModal(){ const m=document.getElementById('modalOverlay'); if(m){ m.classList.remove('open'); document.body.style.overflow=''; } }
function modalOverlayClick(e){ if(e.target===document.getElementById('modalOverlay')) closeModal(); }
function modalContinue(){
  const v=(document.getElementById('modalEmail')||{}).value||'';
  if(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)){
    try{ sessionStorage.setItem('igd_email', v); }catch(e){}
    window.location.href = '/assistant';
  } else {
    const i=document.getElementById('modalEmail'); if(i){ i.style.borderColor='#DC2626'; i.focus(); }
  }
}

// ---- Cookie banner ----
function closeCookie(){ const c=document.getElementById('cookieBanner'); if(c) c.classList.remove('show'); }
function manageCookies(){ alert('Cookie preferences:\n\n\u2611 Essential (required)\n\u2610 Analytics\n\u2610 Marketing\n\nIn production this opens a granular preference center.'); }

// ---- Init shared behaviours ----
document.addEventListener('DOMContentLoaded', function(){
  // cookie
  const cookie=document.getElementById('cookieBanner');
  if(cookie) setTimeout(()=>cookie.classList.add('show'),1800);

  // nav scroll shadow
  const nav=document.querySelector('nav');
  if(nav) window.addEventListener('scroll',()=>{ nav.style.boxShadow = window.scrollY>20 ? '0 2px 20px rgba(0,0,0,0.04)' : 'none'; });

  // scroll reveal
  const obs=new IntersectionObserver((entries)=>{
    entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('visible'); if(e.target.dataset.onreveal && window[e.target.dataset.onreveal]) window[e.target.dataset.onreveal](e.target); } });
  },{threshold:0.12});
  document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
});
