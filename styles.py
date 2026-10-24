CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
#MainMenu, footer {visibility: hidden;}

.stApp {
  background: linear-gradient(135deg,#0B1020,#101a3a,#0b2a2f,#0B1020);
  background-size: 400% 400%; animation: bgShift 24s ease infinite;
}
@keyframes bgShift {0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}

/* ---------- hero ---------- */
.hero {position:relative; overflow:hidden; padding:34px 30px 70px; border-radius:24px;
  background: linear-gradient(120deg,#00e5a8 0%,#2f80ff 50%,#a855f7 100%); background-size:200% 200%;
  animation: bgShift 10s ease infinite, fadeDown .9s ease both; box-shadow:0 18px 50px rgba(47,128,255,.35);}
.hero h1 {margin:0; font-weight:800; font-size:2.5rem; color:#fff; letter-spacing:-.5px;}
.hero p {margin:6px 0 0; color:rgba(255,255,255,.92); font-size:1.05rem;}
.road {position:absolute; left:0; right:0; bottom:0; height:34px; background:rgba(0,0,0,.35);}
.road::before {content:""; position:absolute; top:15px; left:0; right:0; height:3px;
  background:repeating-linear-gradient(90deg,#fff 0 28px,transparent 28px 56px); animation: roadMove 1s linear infinite;}
.car {position:absolute; bottom:22px; font-size:2.4rem; animation: drive 7s linear infinite;}
.car2 {position:absolute; bottom:22px; font-size:2rem; animation: drive 11s linear infinite; animation-delay:-4s; opacity:.85}
@keyframes drive {from{left:-80px} to{left:105%}}
@keyframes roadMove {from{background-position:0 0} to{background-position:-56px 0}}
.bubble {position:absolute; border-radius:50%; background:rgba(255,255,255,.14); animation: floaty 9s ease-in-out infinite;}
@keyframes floaty {0%,100%{transform:translateY(0)} 50%{transform:translateY(-22px)}}
@keyframes fadeDown {from{opacity:0; transform:translateY(-24px)} to{opacity:1; transform:none}}
@keyframes fadeUp {from{opacity:0; transform:translateY(26px)} to{opacity:1; transform:none}}
@keyframes pop {0%{transform:scale(.4); opacity:0} 70%{transform:scale(1.12)} 100%{transform:scale(1); opacity:1}}
@keyframes pulse {0%,100%{box-shadow:0 0 0 0 rgba(0,229,168,.55)} 50%{box-shadow:0 0 0 16px rgba(0,229,168,0)}}
@keyframes shake {0%,100%{transform:translateX(0)} 25%{transform:translateX(-6px)} 75%{transform:translateX(6px)}}
@keyframes grow {from{width:0}}

/* ---------- cards ---------- */
.kpi-row {display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:14px; margin:8px 0 6px;}
.kpi {background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.12); border-radius:18px; padding:16px 18px;
  backdrop-filter: blur(8px); animation: fadeUp .7s ease both; transition: transform .25s, box-shadow .25s, border-color .25s;}
.kpi:hover {transform: translateY(-6px) scale(1.03); box-shadow:0 14px 34px rgba(0,229,168,.25); border-color:#00e5a8;}
.kpi .ico {font-size:1.6rem;} .kpi .val {font-size:1.55rem; font-weight:800; color:#fff;}
.kpi .lbl {font-size:.78rem; color:#9fb0d6; text-transform:uppercase; letter-spacing:.8px;}
.grade {display:inline-block; width:92px; height:92px; line-height:92px; text-align:center; border-radius:50%;
  font-size:2.3rem; font-weight:800; color:#0B1020; animation: pop .8s cubic-bezier(.2,1.4,.4,1) both, pulse 2s infinite 1s;}
.panel {background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.1); border-radius:18px; padding:16px 20px; animation: fadeUp .6s ease both;}
.shake {animation: shake .5s ease 2;}
.chip {display:inline-block; padding:4px 12px; margin:2px 4px 2px 0; border-radius:999px; font-size:.78rem; font-weight:600;
  background:rgba(0,229,168,.15); color:#00e5a8; border:1px solid rgba(0,229,168,.4); animation: pop .6s both;}
.chip.warn {background:rgba(255,184,0,.15); color:#ffb800; border-color:rgba(255,184,0,.45);}
.bar-wrap {background:rgba(255,255,255,.08); border-radius:999px; height:16px; overflow:hidden; margin:6px 0 14px;}
.bar {height:100%; border-radius:999px; animation: grow 1.4s cubic-bezier(.2,.8,.2,1) both;}

/* ---------- widgets ---------- */
.stButton > button {border-radius:14px; font-weight:700; border:0; padding:.7rem 1.2rem; color:#06101f;
  background:linear-gradient(90deg,#00e5a8,#2f80ff); transition: transform .2s, box-shadow .2s;}
.stButton > button:hover {transform: translateY(-3px) scale(1.03); box-shadow:0 10px 26px rgba(0,229,168,.45); color:#06101f;}
.stButton > button:active {transform: scale(.97);}
.stTabs [data-baseweb="tab"] {font-weight:600; border-radius:12px 12px 0 0; transition: background .25s, transform .25s;}
.stTabs [data-baseweb="tab"]:hover {background:rgba(0,229,168,.12); transform:translateY(-2px);}
section[data-testid="stSidebar"] {background:linear-gradient(180deg,#0e1633,#0a2430); border-right:1px solid rgba(255,255,255,.08);}
div[data-testid="stPlotlyChart"] {animation: fadeUp .8s ease both;}
.footer {text-align:center; color:#7e8db3; font-size:.85rem; margin-top:40px; padding:14px;}
</style>
"""

HERO = """
<div class="hero">
  <div class="bubble" style="width:90px;height:90px;right:6%;top:10%"></div>
  <div class="bubble" style="width:50px;height:50px;right:22%;top:55%;animation-delay:-3s"></div>
  <div class="bubble" style="width:130px;height:130px;right:-30px;top:35%;animation-delay:-5s"></div>
  <h1>⛽ MPG Predictor <span style="font-weight:600">AI</span></h1>
  <p>Enter a car's specs &mdash; our machine-learning engine estimates its fuel efficiency in seconds.</p>
  <div class="road"></div><div class="car">🚗</div><div class="car2">🚙</div>
</div>
"""

GAUGE = """
<html><body style="margin:0;background:transparent;font-family:Poppins,Segoe UI,sans-serif;color:#fff;overflow:hidden">
<svg id="g" viewBox="0 0 400 250" width="100%" style="max-height:330px">
  <defs><filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <g id="arcs"></g><g id="ticks"></g>
  <g id="needle" filter="url(#glow)" transform="rotate(-90 200 210)">
    <polygon points="194,210 206,210 200,82" fill="#fff"/></g>
  <circle cx="200" cy="210" r="14" fill="#0B1020" stroke="#fff" stroke-width="4"/>
  <text id="num" x="200" y="178" text-anchor="middle" font-size="46" font-weight="800" fill="#fff">0.0</text>
  <text x="200" y="244" text-anchor="middle" font-size="14" fill="#9fb0d6" letter-spacing="2">MILES PER GALLON</text>
</svg>
<script>
const V=__VALUE__, MAX=50, cx=200, cy=210, R=150;
const segs=[[0,15,'#ff4d4d'],[15,22,'#ff9f43'],[22,30,'#ffd32a'],[30,38,'#7bed9f'],[38,50,'#00e5a8']];
const pt=(v,r)=>{const a=Math.PI*(1-v/MAX);return [cx+r*Math.cos(a), cy-r*Math.sin(a)];};
const arcs=document.getElementById('arcs');
segs.forEach(([a,b,c])=>{const [x1,y1]=pt(a,R),[x2,y2]=pt(b,R),[x3,y3]=pt(b,R-26),[x4,y4]=pt(a,R-26);
  const p=document.createElementNS('http://www.w3.org/2000/svg','path');
  p.setAttribute('d',`M${x1} ${y1} A${R} ${R} 0 0 1 ${x2} ${y2} L${x3} ${y3} A${R-26} ${R-26} 0 0 0 ${x4} ${y4}Z`);
  p.setAttribute('fill',c);p.setAttribute('opacity','.92');arcs.appendChild(p);});
const ticks=document.getElementById('ticks');
for(let v=0;v<=50;v+=10){const [x,y]=pt(v,R+16);const t=document.createElementNS('http://www.w3.org/2000/svg','text');
  t.setAttribute('x',x);t.setAttribute('y',y+4);t.setAttribute('text-anchor','middle');t.setAttribute('font-size','13');
  t.setAttribute('fill','#9fb0d6');t.textContent=v;ticks.appendChild(t);}
const needle=document.getElementById('needle'), num=document.getElementById('num');
const target=Math.max(0,Math.min(MAX,V)), dur=1900, t0=performance.now();
const ease=t=>1-Math.pow(1-t,4);
function frame(now){
  let p=Math.min(1,(now-t0)/dur), e=ease(p);
  // small overshoot wobble at the end
  let wob = p<1 ? 0 : 0;
  const cur=target*e + (p<1 ? Math.sin(p*14)*(1-p)*2.2 : 0);
  needle.setAttribute('transform',`rotate(${-90+(cur/MAX)*180} ${cx} ${cy})`);
  num.textContent=(target*e).toFixed(1);
  if(p<1) requestAnimationFrame(frame); else num.textContent=target.toFixed(1);
}
requestAnimationFrame(frame);
</script></body></html>
"""
