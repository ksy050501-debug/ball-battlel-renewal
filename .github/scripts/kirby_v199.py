from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def sub(pattern,repl,label):
    global s
    s2,n=re.subn(pattern,repl,s,count=1,flags=re.S)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    s=s2

if '<title>볼배틀 리뉴얼 v198</title>' not in s:
    raise SystemExit('expected v198 source')
s=s.replace('<title>볼배틀 리뉴얼 v198</title>','<title>볼배틀 리뉴얼 v199</title>',1)
s=s.replace('<h1 id="mainTitle">볼배틀 리뉴얼 v198</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v199</h1>',1)

char_new='''      { id:"kirby", name:"커비", mark:"★", role:"게임", color:"#f472b6", hp:150, attack:0, speed:2.55, range:0,
        skillName:"흡입 · 카피 능력", condition:"기본 상태 10초 주기 120° 장시간 흡입 · 배회형 중립 몬스터 최대2마리 · 카피 누적피해45 → 별 이탈", desc:"기본 상태에서는 진행방향 전방120도를 3.2초 동안 천천히 흡입한다. 중립 몬스터는 캐릭터를 추적하지 않고 경기장을 제멋대로 배회하며, 공격 범위 안에 캐릭터가 들어오면 각자의 기술을 사용한다. 현재 존재하는 몬스터와 커비가 보유한 카피를 제외한 종류에서 새 몬스터가 생성된다. 소드는 회전베기, 빔은 별 채찍, 파이어는 부채꼴 화염방사, 밤은 한 번 튀는 포물선 폭탄을 사용하며 커비가 카피하면 강화판을 쓴다. 상대 본체를 삼키면 잠시 몸속에 가둔 뒤 뱉어 강하게 날리고 벽충돌 피해를 줄 수 있다. 카피 상태에서 누적 피해45를 받으면 능력이 별로 튕겨 나가며, 5초 안에 다시 닿으면 되찾는다." },'''
sub(r'      \{ id:"kirby", name:"커비", mark:"★", role:"게임", color:"#f472b6", hp:150, attack:0, speed:2\.55, range:0,\n        skillName:"흡입 · 카피 능력", condition:"[^"]*", desc:"[^"]*" \},',char_new,'kirby prose')

info_new='''      if(c.id==="kirby")return {damage:"소드 회전베기10+출혈1×4 / 빔 채찍7+둔화 / 파이어5+화상1×3 / 밤 폭탄12×2(반경58) / 뱉기 벽충돌12",tick:"기본 흡입10초 주기·3.2초 지속·전방120°·느린 흡입 / 배회형 중립 몬스터6.5초마다·최대2 / 카피 누적피해45에서 별 이탈·별5초",tip:"중립 몬스터는 적을 추적하지 않고 임의 방향으로 돌아다니다 사거리 안에 캐릭터가 들어왔을 때만 기술을 사용한다. 소드는 회전베기, 빔은 휘어지는 별 채찍, 파이어는 좁은 화염방사, 밤은 한 번 튀는 폭탄이며 카피 커비는 강화판을 사용한다."};'''
sub(r'      if\(c\.id==="kirby"\)return \{damage:"[^"]*",tick:"[^"]*",tip:"[^"]*"\};',info_new,'kirby info')

radial=r'''    function kirbyRadialSlash(source,radius,power,bleed=false,reason="커비 소드"){
      let hits=0;
      for(const e of kirbyAreaTargets(source)){
        if(Math.hypot(e.x-source.x,e.y-source.y)>radius+e.r)continue;
        const dealt=damage(e,power,source,reason);
        if(dealt>0){hits++;if(bleed)applyBleed(e,source,1,2.05,.5,4);if(!fastSimMode)spawnHitFlash(e.x,e.y,"#86efac",36);}
      }
      source.kirbyFx={kind:"sword",t:.42,max:.42,angle:Math.atan2(source.vy||0,source.vx||1),range:radius,enhanced:!source.kirbyNeutral};
      if(!fastSimMode)playSound("wind",.72);
      return hits;
    }'''
sub(r'    function kirbyRadialSlash\(source,radius,power,bleed=false,reason="커비 소드"\)\{.*?\n    \}',radial,'sword fx')

whip=r'''    function kirbyWhip(source,range,arc,power,slow=false,reason="빔 채찍"){
      const target=source.kirbyNeutral?kirbyNeutralTarget(source):kirbyAttackTarget(source);if(!target)return false;
      const a=Math.atan2(target.y-source.y,target.x-source.x),half=arc/2;let hits=0;
      for(const e of kirbyAreaTargets(source)){
        const dx=e.x-source.x,dy=e.y-source.y,d=Math.hypot(dx,dy)||1,ea=Math.atan2(dy,dx),diff=Math.abs(Math.atan2(Math.sin(ea-a),Math.cos(ea-a)));
        if(d>range+e.r||diff>half)continue;
        const dealt=damage(e,power,source,reason);if(dealt>0){hits++;if(slow)applySlow(e,.72,.85,"kirbyBeamSlow");if(!fastSimMode)spawnHitFlash(e.x,e.y,"#fde047",38);}
      }
      source.kirbyFx={kind:"beam",t:.54,max:.54,angle:a,range,arc,enhanced:!source.kirbyNeutral};
      if(!fastSimMode)playSound("magic",.78);
      return hits>0;
    }'''
sub(r'    function kirbyWhip\(source,range,arc,power,slow=false,reason="빔 채찍"\)\{.*?\n    \}',whip,'beam fx')

flame=r'''    function kirbyFlameCone(source,range,arc,power,burn=false,reason="파이어"){
      const target=source.kirbyNeutral?kirbyNeutralTarget(source):kirbyAttackTarget(source);if(!target)return false;
      const a=Math.atan2(target.y-source.y,target.x-source.x),half=arc/2;let hits=0;
      for(const e of kirbyAreaTargets(source)){
        const dx=e.x-source.x,dy=e.y-source.y,d=Math.hypot(dx,dy)||1,ea=Math.atan2(dy,dx),diff=Math.abs(Math.atan2(Math.sin(ea-a),Math.cos(ea-a)));
        if(d>range+e.r||diff>half)continue;
        const dealt=damage(e,power,source,reason);if(dealt>0){hits++;if(burn)applyBurn(e,source,1,1.8,.6,3,"kirbyFire");if(!fastSimMode)spawnHitFlash(e.x,e.y,"#fb923c",34);}
      }
      source.kirbyFx={kind:"fire",t:.58,max:.58,angle:a,range,arc,enhanced:!source.kirbyNeutral};
      if(!fastSimMode)playSound("fireball",.72);
      return hits>0;
    }'''
sub(r'    function kirbyFlameCone\(source,range,arc,power,burn=false,reason="파이어"\)\{.*?\n    \}',flame,'fire fx')

old='m.kirbyNeutral={type,attackCd:rand(.4,1.0),recoil:0};'
new='m.kirbyNeutral={type,attackCd:rand(.4,1.0),recoil:0,wanderAngle:rand(0,Math.PI*2),wanderTime:rand(1.2,3.0),facing:0};m.kirbyNeutral.facing=m.kirbyNeutral.wanderAngle;'
if old not in s: raise SystemExit('neutral spawn state anchor missing')
s=s.replace(old,new,1)

neutral_update=r'''    function updateKirbyNeutral(f,dt){
      const n=f?.kirbyNeutral;if(!n||!f.alive)return;
      n.attackCd=Math.max(0,(n.attackCd||0)-dt);n.recoil=Math.max(0,(n.recoil||0)-dt);n.wanderTime=(n.wanderTime||0)-dt;
      if(f.kirbyFx){f.kirbyFx.t-=dt;if(f.kirbyFx.t<=0)f.kirbyFx=null;}
      if(isStunned(f)||(f.hardFreeze||0)>0){f.vx*=.90;f.vy*=.90;return;}
      if(n.recoil>0){n.facing=Math.atan2(f.vy||0,f.vx||1);return;}
      const wallPad=f.r+5;
      if(f.x<=arena.x+wallPad||f.x>=arena.x2-wallPad||f.y<=arena.y+wallPad||f.y>=arena.y2-wallPad){
        const cx=(arena.x+arena.x2)/2-f.x,cy=(arena.y+arena.y2)/2-f.y;
        n.wanderAngle=Math.atan2(cy,cx)+rand(-.75,.75);n.wanderTime=rand(.8,2.2);
      }else if(n.wanderTime<=0){
        n.wanderAngle+=rand(-1,1)*Math.PI*.85;n.wanderTime=rand(1.2,3.0);
      }
      const v=(f.baseSpeed||f.speed||2)*44;
      f.vx=Math.cos(n.wanderAngle)*v;f.vy=Math.sin(n.wanderAngle)*v;n.facing=n.wanderAngle;
      if(n.attackCd>0)return;
      const target=kirbyNeutralTarget(f);if(!target)return;
      const d=Math.hypot(target.x-f.x,target.y-f.y);
      if(n.type==="sword"){
        if(d<=f.r+28+target.r){kirbyRadialSlash(f,f.r+28,5,false,"중립 소드 회전베기");n.attackCd=1.35;}
      }else if(n.type==="beam"){
        if(d<=118){kirbyWhip(f,98,Math.PI*2/3,5,false,"중립 빔 채찍");n.attackCd=1.85;}
      }else if(n.type==="fire"){
        if(d<=100){kirbyFlameCone(f,82,Math.PI*5/18,4,false,"중립 화염방사");n.attackCd=1.45;}
      }else if(n.type==="bomb"){
        if(d<=210){kirbyThrowBomb(f,target,8,48,"중립 밤");n.attackCd=3.0;}
      }
    }'''
sub(r'    function updateKirbyNeutral\(f,dt\)\{.*?\n    \}\n    function kirbySwallowEnemy',neutral_update+'\n    function kirbySwallowEnemy','neutral wander')

anchor='''    function updateKirby(f,dt){
      const k=f?.kirby;if(!k||!f.alive)return;'''
repl='''    function updateKirby(f,dt){
      const k=f?.kirby;if(!k||!f.alive)return;
      if(f.kirbyFx){f.kirbyFx.t-=dt;if(f.kirbyFx.t<=0)f.kirbyFx=null;}'''
if anchor not in s: raise SystemExit('updateKirby anchor missing')
s=s.replace(anchor,repl,1)

draw_world=r'''    function drawKirbyWorld(){
      if(fastSimMode)return;
      for(const b of kirbyBombs){
        const sy=b.y-b.z*.42,shadow=clamp(1-b.z/95,.18,.72);ctx.save();ctx.globalAlpha=shadow;ctx.fillStyle="rgba(15,23,42,.72)";ctx.beginPath();ctx.ellipse(b.x,b.y+6,11,4.5,0,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;ctx.shadowColor=b.color;ctx.shadowBlur=15;ctx.fillStyle="#111827";ctx.strokeStyle="#c4b5fd";ctx.lineWidth=2;ctx.beginPath();ctx.arc(b.x,sy,b.r+1,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.strokeStyle="#f59e0b";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(b.x+4,sy-6);ctx.quadraticCurveTo(b.x+8,sy-13,b.x+12,sy-9);ctx.stroke();ctx.fillStyle="#fde047";ctx.beginPath();ctx.arc(b.x+12+Math.cos(battleTime*18)*2,sy-9+Math.sin(battleTime*18)*2,2.2,0,Math.PI*2);ctx.fill();ctx.restore();
      }
      for(const st of kirbyCopyStars){const info=KIRBY_COPY[st.type],a=clamp(st.life/st.maxLife,0,1);ctx.save();ctx.globalAlpha=.45+.55*a;ctx.shadowColor=info?.color||"#fde68a";ctx.shadowBlur=16;drawKirbyStar(st.x,st.y,st.r,info?.color||"#fde68a",battleTime*3);ctx.restore();}
      for(const f of fighters){if(!f.alive||!f.kirby||f.kirby.inhaleTime<=0)continue;const k=f.kirby,a=k.inhaleAngle,half=KIRBY.inhaleCone/2;ctx.save();ctx.lineCap="round";for(let i=0;i<11;i++){const phase=(battleTime*.58+i/11)%1,aa=a-half+(i/10)*KIRBY.inhaleCone+Math.sin(battleTime*4+i)*.045,start=KIRBY.inhaleRange*(1-phase)+f.r+8,end=Math.max(f.r+8,start-42),bend=Math.sin(i*2.2+battleTime*5)*10,sx=f.x+Math.cos(aa)*start,sy=f.y+Math.sin(aa)*start,ex=f.x+Math.cos(aa)*end,ey=f.y+Math.sin(aa)*end,nx=-Math.sin(aa),ny=Math.cos(aa);ctx.globalAlpha=.18+.50*phase;ctx.strokeStyle=i%3===0?"#fff":"#fbcfe8";ctx.lineWidth=1.4+(i%3)*.55;ctx.beginPath();ctx.moveTo(sx,sy);ctx.quadraticCurveTo((sx+ex)/2+nx*bend,(sy+ey)/2+ny*bend,ex,ey);ctx.stroke();}ctx.globalAlpha=.30;ctx.strokeStyle="#f9a8d4";ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(f.x,f.y,KIRBY.inhaleRange,a-half,a+half);ctx.stroke();ctx.restore();}
      for(const f of fighters){const fx=f.kirbyFx;if(!f.alive||!fx||fx.t<=0)continue;const q=1-fx.t/fx.max;ctx.save();ctx.lineCap="round";ctx.lineJoin="round";
        if(fx.kind==="sword"){
          const r=fx.range,rot=fx.angle-Math.PI*.95+q*Math.PI*1.9;ctx.globalAlpha=.28+.58*(1-q);ctx.strokeStyle="#86efac";ctx.shadowColor="#dcfce7";ctx.shadowBlur=18;ctx.lineWidth=fx.enhanced?12:8;ctx.beginPath();ctx.arc(f.x,f.y,r,rot-.72,rot+.72);ctx.stroke();ctx.strokeStyle="#f8fafc";ctx.lineWidth=fx.enhanced?4:2.5;ctx.beginPath();ctx.arc(f.x,f.y,r-3,rot-.62,rot+.62);ctx.stroke();
        }else if(fx.kind==="beam"){
          const sweep=-.85+q*1.7,a=fx.angle+sweep,range=fx.range,startX=f.x+Math.cos(a)*f.r*.55,startY=f.y+Math.sin(a)*f.r*.55,endX=f.x+Math.cos(a)*range,endY=f.y+Math.sin(a)*range,side=fx.enhanced?30:20,nx=-Math.sin(a),ny=Math.cos(a),cx=(startX+endX)/2+nx*Math.sin(q*Math.PI)*side,cy=(startY+endY)/2+ny*Math.sin(q*Math.PI)*side;ctx.globalAlpha=.88;ctx.strokeStyle="#fef08a";ctx.shadowColor="#fde047";ctx.shadowBlur=18;ctx.lineWidth=fx.enhanced?6:4;ctx.beginPath();ctx.moveTo(startX,startY);ctx.quadraticCurveTo(cx,cy,endX,endY);ctx.stroke();for(let i=1;i<=9;i++){const t=i/9,u=1-t,x=u*u*startX+2*u*t*cx+t*t*endX,y=u*u*startY+2*u*t*cy+t*t*endY;drawKirbyStar(x,y,fx.enhanced?5.2:4.1,"#fde047",battleTime*4+i*.4);}
        }else if(fx.kind==="fire"){
          const half=fx.arc/2;ctx.globalCompositeOperation="lighter";for(let i=0;i<15;i++){const t=(i+.5)/15,aa=fx.angle-half+fx.arc*t+Math.sin(battleTime*12+i)*.025,len=fx.range*(.48+.48*((i*37)%11)/10),wide=4+7*(i%4)/3;ctx.globalAlpha=.22+.50*(1-q);ctx.strokeStyle=i%3===0?"#fef08a":i%2?"#fb923c":"#ef4444";ctx.lineWidth=wide;ctx.beginPath();ctx.moveTo(f.x+Math.cos(aa)*(f.r*.55),f.y+Math.sin(aa)*(f.r*.55));ctx.quadraticCurveTo(f.x+Math.cos(aa)*len*.55-Math.sin(aa)*Math.sin(battleTime*14+i)*8,f.y+Math.sin(aa)*len*.55+Math.cos(aa)*Math.sin(battleTime*14+i)*8,f.x+Math.cos(aa)*len,f.y+Math.sin(aa)*len);ctx.stroke();}
        }
        ctx.restore();
      }
    }'''
sub(r'    function drawKirbyWorld\(\)\{.*?\n    \}\n    function drawKirbyNeutral',draw_world+'\n    function drawKirbyNeutral','draw world')

draw_neutral=r'''    function drawKirbyNeutral(f){
      const n=f.kirbyNeutral,type=n.type,info=KIRBY_COPY[type],a=n.facing??Math.atan2(f.vy||0,f.vx||1);ctx.save();ctx.translate(f.x,f.y);ctx.rotate(a);ctx.scale(f.r/13,f.r/13);ctx.lineWidth=1.3;ctx.shadowColor=info.color;ctx.shadowBlur=8;ctx.fillStyle="#7c2d12";ctx.beginPath();ctx.ellipse(-5,9,5,3,.15,0,Math.PI*2);ctx.ellipse(5,9,5,3,-.15,0,Math.PI*2);ctx.fill();
      if(type==="sword"){
        ctx.fillStyle="#facc8b";ctx.strokeStyle="#92400e";ctx.beginPath();ctx.arc(0,0,10,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle="#16a34a";ctx.beginPath();ctx.moveTo(-10,-5);ctx.quadraticCurveTo(0,-19,13,-8);ctx.lineTo(8,-3);ctx.lineTo(-8,-3);ctx.closePath();ctx.fill();ctx.strokeStyle="#f8fafc";ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(8,1);ctx.lineTo(19,-5);ctx.stroke();ctx.strokeStyle="#fbbf24";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(7,0);ctx.lineTo(11,6);ctx.stroke();
      }else if(type==="beam"){
        ctx.fillStyle="#f59e0b";ctx.strokeStyle="#92400e";ctx.beginPath();ctx.arc(0,1,10,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle="#fff";ctx.beginPath();ctx.ellipse(4,-1,5.5,7,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#2563eb";ctx.beginPath();ctx.ellipse(5,-1,2.3,4.2,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#111827";ctx.beginPath();ctx.arc(5,-1,1.1,0,Math.PI*2);ctx.fill();drawKirbyStar(15,-5,4,"#fde047",battleTime*3);
      }else if(type==="fire"){
        ctx.fillStyle="#fb7185";ctx.strokeStyle="#9f1239";ctx.beginPath();ctx.arc(0,2,10,0,Math.PI*2);ctx.fill();ctx.stroke();for(let i=-2;i<=2;i++){ctx.fillStyle=i%2?"#fde047":"#f97316";ctx.beginPath();ctx.moveTo(i*4-4,-5);ctx.quadraticCurveTo(i*4,-21-Math.abs(i)*2,i*4+4,-5);ctx.closePath();ctx.fill();}
      }else{
        ctx.fillStyle="#374151";ctx.strokeStyle="#111827";ctx.beginPath();ctx.arc(0,1,10,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle="#7c3aed";ctx.beginPath();ctx.arc(-2,-7,9,Math.PI,0);ctx.lineTo(7,-3);ctx.lineTo(-9,-3);ctx.closePath();ctx.fill();ctx.strokeStyle="#f59e0b";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(5,-10);ctx.quadraticCurveTo(9,-16,13,-12);ctx.stroke();ctx.fillStyle="#fde047";ctx.beginPath();ctx.arc(14,-12,2,0,Math.PI*2);ctx.fill();
      }
      ctx.fillStyle="#111827";ctx.beginPath();ctx.arc(5,2,1.3,0,Math.PI*2);ctx.fill();ctx.restore();drawHealthBar(f);ctx.font="800 9px system-ui";ctx.textAlign="center";ctx.fillStyle=info.color;ctx.fillText(kirbyCopyName(type),f.x,f.y+f.r+18);
    }'''
sub(r'    function drawKirbyNeutral\(f\)\{.*?\n    \}\n    function drawKirbyCharacter',draw_neutral+'\n    function drawKirbyCharacter','neutral art')

draw_kirby=r'''    function drawKirbyCharacter(f){
      const k=f.kirby||{mode:"base",baseR:16,inhaleTime:0};ctx.save();ctx.translate(f.x,f.y);applyMarioSpriteSpin(f);const scale=f.r/(k.baseR||16);ctx.scale(scale,scale);ctx.shadowColor="#f472b6";ctx.shadowBlur=12;const g=ctx.createRadialGradient(-5,-7,3,0,0,17);g.addColorStop(0,"#fecdd3");g.addColorStop(.55,"#f9a8d4");g.addColorStop(1,"#f472b6");ctx.fillStyle=g;ctx.strokeStyle="#be185d";ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(0,0,15,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle="#dc2626";ctx.beginPath();ctx.ellipse(-9,12,7.4,4.4,-.20,0,Math.PI*2);ctx.ellipse(9,12,7.4,4.4,.20,0,Math.PI*2);ctx.fill();ctx.fillStyle="#1e3a8a";ctx.beginPath();ctx.ellipse(-5,-4,2.5,5.4,0,0,Math.PI*2);ctx.ellipse(5,-4,2.5,5.4,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#fff";ctx.beginPath();ctx.ellipse(-5,-6.2,1.05,2,0,0,Math.PI*2);ctx.ellipse(5,-6.2,1.05,2,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#fb7185";ctx.globalAlpha=.60;ctx.beginPath();ctx.ellipse(-10,3,3.1,1.8,-.2,0,Math.PI*2);ctx.ellipse(10,3,3.1,1.8,.2,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;
      if(k.inhaleTime>0){ctx.fillStyle="#3f0d22";ctx.beginPath();ctx.ellipse(0,5,7.6,6.7,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#fb7185";ctx.beginPath();ctx.ellipse(0,8,4.2,2.1,0,0,Math.PI*2);ctx.fill();}else{ctx.strokeStyle="#9f1239";ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(0,4,4,.15,Math.PI-.15);ctx.stroke();}
      if(k.mode==="sword"){ctx.fillStyle="#16a34a";ctx.strokeStyle="#166534";ctx.lineWidth=1.2;ctx.beginPath();ctx.moveTo(-13,-8);ctx.quadraticCurveTo(-4,-24,9,-19);ctx.quadraticCurveTo(15,-17,12,-9);ctx.lineTo(7,-6);ctx.lineTo(-10,-6);ctx.closePath();ctx.fill();ctx.stroke();ctx.strokeStyle="#f8fafc";ctx.shadowColor="#dbeafe";ctx.shadowBlur=10;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(10,-4);ctx.lineTo(25,-18);ctx.stroke();ctx.strokeStyle="#fbbf24";ctx.lineWidth=2.4;ctx.beginPath();ctx.moveTo(9,-5);ctx.lineTo(14,1);ctx.stroke();}
      else if(k.mode==="beam"){ctx.fillStyle="#fde047";ctx.strokeStyle="#ca8a04";ctx.lineWidth=1.2;ctx.beginPath();ctx.arc(-1,-12,9,Math.PI,0);ctx.lineTo(8,-6);ctx.lineTo(-9,-6);ctx.closePath();ctx.fill();ctx.stroke();drawKirbyStar(14,-15,4.3,"#fde047",battleTime*2.8);}
      else if(k.mode==="fire"){for(let i=-3;i<=3;i++){ctx.fillStyle=i%2?"#fde047":"#fb923c";ctx.beginPath();ctx.moveTo(i*4-3,-8);ctx.quadraticCurveTo(i*4,-25-Math.abs(i)*1.7,i*4+3,-8);ctx.closePath();ctx.fill();}ctx.fillStyle="#ef4444";ctx.beginPath();ctx.arc(0,-8,7,Math.PI,0);ctx.fill();}
      else if(k.mode==="bomb"){ctx.fillStyle="#6d28d9";ctx.strokeStyle="#4c1d95";ctx.lineWidth=1.2;ctx.beginPath();ctx.arc(-1,-12,9,Math.PI,0);ctx.lineTo(8,-6);ctx.lineTo(-9,-6);ctx.closePath();ctx.fill();ctx.stroke();ctx.fillStyle="#111827";ctx.beginPath();ctx.arc(15,1,5.2,0,Math.PI*2);ctx.fill();ctx.strokeStyle="#f59e0b";ctx.beginPath();ctx.moveTo(18,-3);ctx.quadraticCurveTo(21,-8,24,-5);ctx.stroke();}
      if(k.swallowedId){ctx.globalAlpha=.22;ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(0,3,11,0,Math.PI*2);ctx.fill();}ctx.restore();drawHealthBar(f);drawName(f);
    }'''
sub(r'    function drawKirbyCharacter\(f\)\{.*?\n    \}\n\n    const MARIO',draw_kirby+'\n\n    const MARIO','kirby art')

marker='      "v198: 커비 1차 피드백 반영.'
idx=s.find(marker)
if idx<0: raise SystemExit('v198 patch note missing')
note='      "v199: 커비 비주얼·중립 몬스터 AI 재작업. 중립 몬스터는 캐릭터를 추적하지 않고 임의 방향으로 배회하며 사거리 안에 들어온 캐릭터에게만 기술 사용. 소드·빔·파이어·밤 몬스터 외형을 서로 다른 소형 캐릭터로 재구성하고, 소드 회전베기·곡선형 별 채찍·지속 화염방사·포물선 폭탄 및 흡입 바람 연출을 전면 개선. 전투 피해·카피 이탈 기준 등 핵심 수치는 유지.",\n'
s=s[:idx]+note+s[idx:]

p.write_text(s,encoding='utf-8')
