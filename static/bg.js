
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta name="theme-color" content="#030907">
<title>CYBER CONTROL</title>

<style>
*{box-sizing:border-box}
body{
 margin:0;background:#030907;color:#d9ffe8;
 font-family:Arial,sans-serif;overflow-x:hidden;
}
#matrix{
 position:fixed;inset:0;width:100%;height:100%;
 z-index:-2;opacity:.30;
}
body:after{
 content:"";position:fixed;inset:0;pointer-events:none;
 background:radial-gradient(circle at center,#00ff7615,transparent 65%);
 z-index:-1;
}
.app{
 width:100%;max-width:480px;min-height:100vh;
 margin:auto;padding:16px 13px 90px;
}
.header{
 display:flex;justify-content:space-between;
 align-items:center;border-bottom:1px solid #00ff7640;
 padding:12px 2px 17px;
}
.logo{font-weight:900;font-size:19px;letter-spacing:2px;color:#42ff91}
.logo small{display:block;font-size:9px;color:#6ba889;margin-top:4px}
.online{
 font-size:10px;color:#4cff91;
 border:1px solid #36ff7755;padding:8px;
}
.blink{display:inline-block;width:7px;height:7px;
 background:#3dff87;border-radius:50%;margin-left:5px;
 box-shadow:0 0 12px #3dff87;
 animation:blink 1s infinite}
@keyframes blink{50%{opacity:.2}}

.heading{margin:25px 0 17px}
.heading small{color:#43ff92;font-size:10px;letter-spacing:2px}
.heading h1{font-size:25px;margin:8px 0}
.heading p{font-size:11px;color:#80a991;margin:0}

.radar-box{
 position:relative;height:245px;
 display:flex;justify-content:center;align-items:center;
 margin:12px 0 20px;
 border:1px solid #21ff7440;
 background:linear-gradient(145deg,#0a1b12aa,#020805aa);
 overflow:hidden;
}
.radar{
 width:190px;height:190px;border-radius:50%;
 border:1px solid #3bff8970;position:relative;
 background:repeating-radial-gradient(
 circle,transparent 0 28px,#30ff7530 29px 30px
 );
 box-shadow:0 0 30px #00ff7620,inset 0 0 30px #00ff7610;
}
.radar:before{
 content:"";position:absolute;inset:0;border-radius:50%;
 background:conic-gradient(from 0deg,transparent 65%,#31ff8b77);
 animation:rotate 4s linear infinite;
}
.radar:after{
 content:"";position:absolute;left:50%;top:50%;
 width:8px;height:8px;border-radius:50%;
 background:#55ff9b;transform:translate(-50%,-50%);
 box-shadow:0 0 18px #55ff9b;
}
@keyframes rotate{to{transform:rotate(360deg)}}
.radar-center{
 position:absolute;inset:0;display:flex;
 align-items:center;justify-content:center;
 flex-direction:column;z-index:2;
}
.radar-center strong{font-size:23px;color:#55ff9b}
.radar-center span{font-size:9px;color:#8acba6;margin-top:5px}
.target{
 position:absolute;width:7px;height:7px;border-radius:50%;
 background:#4dff94;box-shadow:0 0 12px #4dff94;
}
.t1{top:25%;left:30%}
.t2{top:65%;left:70%}
.t3{top:35%;right:20%}
.radar-label{
 position:absolute;top:12px;left:12px;
 font-size:9px;color:#51ff99;letter-spacing:1px
}
.radar-bottom{
 position:absolute;bottom:12px;right:12px;
 font-size:9px;color:#6fa98a
}

.section-title{
 font-size:13px;margin:23px 0 12px;
 color:#65ffa4;display:flex;justify-content:space-between;
}
.section-title small{font-size:9px;color:#6b927a}

.cards{
 display:grid;grid-template-columns:1fr 1fr;gap:10px;
}
.card{
 min-height:91px;padding:14px 12px;
 border:1px solid #36ff7540;
 background:linear-gradient(140deg,#0b1b11,#06100a);
 position:relative;overflow:hidden;
}
.card:after{
 content:"";position:absolute;top:0;right:0;
 width:45px;height:1px;background:#4dff96;
 box-shadow:0 0 10px #4dff96;
}
.card span{font-size:10px;color:#83a992}
.card strong{
 display:block;font-size:22px;color:#4dff96;
 margin-top:9px;font-family:monospace;
}
.card small{font-size:8px;color:#638b72}

.system{
 margin-top:16px;padding:15px;
 background:#08140d;border:1px solid #35ff7540;
}
.system-head{
 display:flex;justify-content:space-between;
 font-size:11px;margin-bottom:15px;
}
.system-head b{color:#50ff97}
.bar-row{margin:13px 0}
.bar-label{
 display:flex;justify-content:space-between;
 font-size:10px;color:#a1c8ad;margin-bottom:7px;
}
.bar{
 height:5px;background:#183023;overflow:hidden;
}
.bar i{
 display:block;height:100%;width:75%;
 background:#41ff8d;box-shadow:0 0 12px #41ff8d;
 animation:load 3s ease-in-out infinite alternate;
}
.bar:nth-child(2) i{width:60%}
@keyframes load{from{width:30%}to{width:85%}}

.terminal{
 margin-top:15px;padding:14px;
 background:#020704;border:1px solid #29ff6938;
 font-family:monospace;font-size:10px;
 color:#50ff91;min-height:115px;
}
.terminal-title{
 color:#86b69a;margin-bottom:12px;
 font-size:9px;
}
.line{margin:8px 0;opacity:.9}
.cursor{
 display:inline-block;width:6px;height:12px;
 background:#4aff91;vertical-align:middle;
 animation:blink .8s infinite;
}
.bottom-nav{
 position:fixed;bottom:0;left:50%;
 transform:translateX(-50%);
 width:100%;max-width:480px;
 background:#06100cf5;border-top:1px solid #35ff7540;
 display:flex;justify-content:space-around;
 padding:13px 5px calc(13px + env(safe-area-inset-bottom));
 z-index:10;
}
.nav-item{
 color:#6c967a;font-size:10px;text-align:center;
}
.nav-item b{display:block;font-size:18px;margin-bottom:5px}
.nav-item.active{color:#4cff96}
.footer{
 text-align:center;color:#52745f;font-size:9px;
 margin-top:22px;
}
</style>
</head>

<body>

<canvas id="matrix"></canvas>

<main class="app">

<header class="header">
 <div class="logo">
  CYBER CONTROL
  <small>ADVANCED SECURITY SYSTEM</small>
 </div>
 <div class="online">
  <i class="blink"></i> SYSTEM ONLINE
 </div>
</header>

<section class="heading">
 <small>WELCOME TO COMMAND CENTER</small>
 <h1>مركز التحكم الذكي</h1>
 <p>لوحة مراقبة رقمية بتصميم سايبربانك متطور</p>
</section>

<div class="radar-box">
 <div class="radar-label">RADAR // ACTIVE</div>
 <div class="radar">
  <i class="target t1"></i>
  <i class="target t2"></i>
  <i class="target t3"></i>
  <div class="radar-center">
   <strong>ACTIVE</strong>
   <span>SCANNING SYSTEM</span>
  </div>
 </div>
 <div class="radar-bottom">SIGNAL: STABLE</div>
</div>

<div class="section-title">
 <b>إحصائيات النظام</b>
 <small>LIVE MONITORING</small>
</div>

<div class="cards">
 <div class="card">
  <span>حالة النظام</span>
  <strong>ONLINE</strong>
  <small>OPERATIONAL</small>
 </div>
 <div class="card">
  <span>قوة الإشارة</span>
  <strong>98%</strong>
  <small>SIGNAL STRENGTH</small>
 </div>
 <div class="card">
  <span>سرعة المعالجة</span>
  <strong id="speed">86%</strong>
  <small>PROCESSING POWER</small>
 </div>
 <div class="card">
  <span>مستوى الحماية</span>
  <strong>HIGH</strong>
  <small>SECURITY STATUS</small>
 </div>
</div>

<div class="section-title">
 <b>مراقبة الأداء</b>
 <small>PERFORMANCE</small>
</div>

<div class="system">
 <div class="system-head">
  <b>SYSTEM PERFORMANCE</b>
  <span>LIVE DATA</span>
 </div>

 <div class="bar-row">
  <div class="bar-label">
   <span>CPU PROCESSING</span>
   <span id="cpu">75%</span>
  </div>
  <div class="bar"><i id="cpuBar"></i></div>
 </div>

 <div class="bar-row">
  <div class="bar-label">
   <span>MEMORY USAGE</span>
   <span id="memory">60%</span>
  </div>
  <div class="bar"><i id="memBar"></i></div>
 </div>

 <div class="bar-row">
  <div class="bar-label">
   <span>NETWORK STATUS</span>
   <span>STABLE</span>
  </div>
  <div class="bar"><i style="width:92%"></i></div>
 </div>
</div>

<div class="section-title">
 <b>الشاشة الإلكترونية</b>
 <small>LIVE TERMINAL</small>
</div>

<div class="terminal">
 <div class="terminal-title">ROOT@CYBER-SYSTEM:~</div>
 <div class="line">[+] Initializing system...</div>
 <div class="line">[+] Security protocols active</div>
 <div class="line">[+] Monitoring connection...</div>
 <div class="line" id="terminalLine">[+] All systems operational</div>
 <span class="cursor"></span>
</div>

<div class="footer">
 CYBER CONTROL PANEL // MOBILE EDITION
 <br><br>
 DEMO INTERFACE
</div>

</main>

<nav class="bottom-nav">
 <div class="nav-item active"><b>⌂</b>الرئيسية</div>
 <div class="nav-item"><b>◎</b>الرادار</div>
 <div class="nav-item"><b>▦</b>النظام</div>
 <div class="nav-item"><b>⚙</b>الإعدادات</div>
</nav>

<script>
// MATRIX ANIMATION
const canvas=document.getElementById("matrix");
const ctx=canvas.getContext("2d");
let width,height,columns,drops;
const size=15;
const symbols="01アイウエオカキクケコABCDEF";

function resize(){
 width=canvas.width=window.innerWidth;
 height=canvas.height=window.innerHeight;
 columns=Math.ceil(width/size);
 drops=Array(columns).fill(1);
}
window.addEventListener("resize",resize);
resize();

function matrix(){
 ctx.fillStyle="rgba(3,9,6,0.10)";
 ctx.fillRect(0,0,width,height);
 ctx.font=size+"px monospace";
 ctx.fillStyle="#24ff75";

 for(let i=0;i<drops.length;i++){
  let char=symbols[Math.floor(Math.random()*symbols.length)];
  ctx.fillText(char,i*size,drops[i]*size);
  if(drops[i]*size>height && Math.random()>.975)
   drops[i]=0;
  drops[i]++;
 }
 requestAnimationFrame(matrix);
}
matrix();

// LIVE DEMO VALUES
function update(){
 let cpu=Math.floor(55+Math.random()*35);
 let memory=Math.floor(40+Math.random()*35);
 document.getElementById("cpu").textContent=cpu+"%";
 document.getElementById("memory").textContent=memory+"%";
 document.getElementById("cpuBar").style.width=cpu+"%";
 document.getElementById("memBar").style.width=memory+"%";
 document.getElementById("speed").textContent=
  Math.floor(80+Math.random()*19)+"%";
}
setInterval(update,2500);
</script>

</body>
</html>
