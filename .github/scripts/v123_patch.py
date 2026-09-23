from pathlib import Path
import re

path=Path('index.html')
text=path.read_text(encoding='utf-8')

def rep(old,new,count=1,label='anchor'):
    global text
    if old not in text:
        raise SystemExit(f'missing {label}')
    text=text.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v122</title>','<title>볼배틀 리뉴얼 v123</title>',1,'title')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v122</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v123</h1>',1,'main title')
rep('{ id: "conan", name: "고난", mark: "🔍", role: "애니", color: "#2563eb", hp: 165, attack: 0, speed: 2.8, range: 130,','{ id: "conan", name: "고난", mark: "🔍", role: "애니", color: "#2563eb", hp: 160, attack: 0, speed: 2.8, range: 130,',1,'Conan hp')

spider_card='''      { id: "spider_man", name: "거미남", mark: "🕷", role: "영화", color: "#dc2626", hp: 170, attack: 0, speed: 2.9, range: 0,
        skillName: "웹스윙 · 웹슈터", condition: "웹스윙 8초 · 빗나가면 벽을 타고 연속 스윙 · 비스윙 중 5초마다 거미줄 6연사", desc: "거미줄을 벽과 적에게 걸어 경기장을 연속으로 가로지른다. 평상시에는 웹슈터 연사로 적을 벽에 몰아붙여 속박한 뒤 즉시 타게팅 웹스윙으로 추격한다." },
'''
rep('      { id: "dummy_unit", name: "훈련용 더미",',spider_card+'      { id: "dummy_unit", name: "훈련용 더미",',1,'spider card')

spider_code=r'''
    const SPIDER = {
      swingCooldown:8, swingWebSpeed:680, swingArcTime:.62, swingArcAngle:1.55,
      swingMinRadius:72, swingMaxRadius:135, chaseSpeed:720,
      meleeDamage:18, meleeKnock:620, wallDamage:12, wallMarkTime:1.25,
      volleyCooldown:5, volleyCount:6, volleyGap:.09, webSpeed:560, webDamage:2,
      webKnock:105, webSlow:.78, webSlowTime:.9, webPushWindow:1.15, bindTime:1.6
    };
    function initSpiderMan(f){
      f.spider={swingCd:SPIDER.swingCooldown,mode:"idle",swingWeb:null,arc:null,chase:null,
        webs:[],volleyCd:2.4,volleyLeft:0,volleyTimer:0,wallWebs:[]};
    }
    function spiderWebSlowMultiplier(f){
      return (f?.spiderWebSlow||0)>0&&!hasHarmfulImmunity(f)?SPIDER.webSlow:1;
    }
    function spiderSegHit(x1,y1,x2,y2,cx,cy,r){
      const dx=x2-x1,dy=y2-y1,l2=dx*dx+dy*dy||1;
      const t=clamp(((cx-x1)*dx+(cy-y1)*dy)/l2,0,1);
      const px=x1+dx*t,py=y1+dy*t;
      return Math.hypot(px-cx,py-cy)<=r?t:null;
    }
    function spiderWallPoint(x,y){return {x:clamp(x,arena.x,arena.x2),y:clamp(y,arena.y,arena.y2)};}
    function spiderFireSwingWeb(f,targetId=null,initial=false){
      const s=f?.spider;if(!s||!f.alive)return;
      let a=Math.random()*Math.PI*2;
      const target=targetId?fighters.find(e=>e.id===targetId&&e.alive):null;
      if(target)a=Math.atan2(target.y-f.y,target.x-f.x);
      s.mode="shot";s.arc=null;s.chase=null;
      s.swingWeb={x:f.x,y:f.y,vx:Math.cos(a)*SPIDER.swingWebSpeed,vy:Math.sin(a)*SPIDER.swingWebSpeed,life:1.35,targetId:target?.id||null};
      if(initial)s.swingCd=SPIDER.swingCooldown;
      if(!fastSimMode){spawnFloatingText(f.x,f.y-f.r-26,target?"타게팅 웹!":"웹스윙!","#e2e8f0");playSound("magic",.78);}
    }
    function startSpiderSwing(f,targetId=null){const s=f?.spider;if(!s||!f.alive)return;s.volleyLeft=0;s.volleyTimer=0;spiderFireSwingWeb(f,targetId,true);}
    function spiderBeginArc(f,ax,ay){
      const s=f.spider,dx=f.x-ax,dy=f.y-ay;
      const radius=clamp(Math.hypot(dx,dy)||SPIDER.swingMinRadius,SPIDER.swingMinRadius,SPIDER.swingMaxRadius);
      s.mode="arc";s.swingWeb=null;s.chase=null;s.arc={ax,ay,radius,start:Math.atan2(dy,dx),dir:Math.random()<.5?-1:1,t:0};
      f.vx=0;f.vy=0;if(!fastSimMode)spawnBlast(ax,ay,26,"#e2e8f0");
    }
    function spiderBeginChase(f,target){const s=f.spider;s.mode="chase";s.swingWeb=null;s.arc=null;s.chase={targetId:target.id};if(!fastSimMode)spawnFloatingText(target.x,target.y-target.r-30,"거미줄 적중!","#f8fafc");}
    function spiderFinishMelee(f,target){
      const s=f.spider,dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1;
      const dealt=damage(target,SPIDER.meleeDamage,f,"웹스윙 근접타격");
      if(target.alive&&dealt>0){target.vx=dx/d*SPIDER.meleeKnock;target.vy=dy/d*SPIDER.meleeKnock;target.punchFlight=Math.max(target.punchFlight||0,.34);target.punchSource=f;target.punchWallPower=0;target.punchWallHits=0;target.spiderWallMark=Math.max(target.spiderWallMark||0,SPIDER.wallMarkTime);target.spiderWallSourceId=f.id;}
      if(!fastSimMode){spawnHitFlash(target.x,target.y,"#f8fafc",115);spawnBlast(target.x,target.y,72,"#dc2626");playSound("hit",1.0);}
      s.mode="idle";s.chase=null;s.swingCd=SPIDER.swingCooldown;
    }
    function spiderFireVolleyShot(f){
      const s=f.spider,target=nearestEnemy(f)?.enemy;if(!target)return;
      const a=Math.atan2(target.y-f.y,target.x-f.x)+rand(-.075,.075);
      s.webs.push({x:f.x,y:f.y,vx:Math.cos(a)*SPIDER.webSpeed,vy:Math.sin(a)*SPIDER.webSpeed,life:1.35});if(!fastSimMode)playSound("magic",.42);
    }
    function spiderBindTarget(f,target){
      if(!target?.alive||hasHarmfulImmunity(target))return false;
      target.spiderBind=Math.max(target.spiderBind||0,SPIDER.bindTime);target.spiderWebSlow=0;target.spiderPushWindow=0;target.vx=0;target.vy=0;
      const s=f.spider;s.wallWebs.push({x:target.x,y:target.y,t:SPIDER.bindTime+.35,max:SPIDER.bindTime+.35});
      if(!fastSimMode){spawnBlast(target.x,target.y,54,"#e2e8f0");spawnParticles(target.x,target.y,"#f8fafc",24);spawnFloatingText(target.x,target.y-target.r-38,"벽 거미줄 속박!","#f8fafc");}
      s.swingCd=0;startSpiderSwing(f,target.id);return true;
    }
    function spiderCheckWallEffects(f,dt){
      for(const target of enemiesOf(f)){
        if(!target.alive)continue;
        const nearWall=target.x-target.r<=arena.x+2||target.x+target.r>=arena.x2-2||target.y-target.r<=arena.y+2||target.y+target.r>=arena.y2-2;
        if((target.spiderWallMark||0)>0&&target.spiderWallSourceId===f.id&&nearWall){target.spiderWallMark=0;const dealt=damage(target,SPIDER.wallDamage,f,"웹스윙 벽충돌");if(!fastSimMode){spawnBlast(target.x,target.y,76,"#f8fafc");spawnFloatingText(target.x,target.y-target.r-38,"벽충돌 -"+Math.round(dealt),"#fecaca");}}
        if((target.spiderPushWindow||0)>0&&target.spiderPushSourceId===f.id&&nearWall&&!(target.spiderBind>0))spiderBindTarget(f,target);
      }
      f.spider.wallWebs.forEach(w=>w.t-=dt);f.spider.wallWebs=f.spider.wallWebs.filter(w=>w.t>0);
    }
    function updateSpiderSwingWeb(f,dt){
      const s=f.spider,w=s.swingWeb;if(!w)return;
      const x1=w.x,y1=w.y,x2=w.x+w.vx*dt,y2=w.y+w.vy*dt;let hit=null,best=2;
      for(const e of enemiesOf(f)){if(!e.alive||e.tano?.hidden>0)continue;const h=spiderSegHit(x1,y1,x2,y2,e.x,e.y,e.r+7);if(h!==null&&h<best){best=h;hit=e;}}
      if(hit){w.x=x1+(x2-x1)*best;w.y=y1+(y2-y1)*best;spiderBeginChase(f,hit);return;}
      w.x=x2;w.y=y2;w.life-=dt;
      if(w.x<=arena.x||w.x>=arena.x2||w.y<=arena.y||w.y>=arena.y2||w.life<=0){const p=spiderWallPoint(w.x,w.y);spiderBeginArc(f,p.x,p.y);}
    }
    function updateSpiderVolleyWebs(f,dt){
      const s=f.spider;
      for(let i=s.webs.length-1;i>=0;i--){
        const w=s.webs[i],x1=w.x,y1=w.y,x2=w.x+w.vx*dt,y2=w.y+w.vy*dt;let hit=null,best=2;
        for(const e of enemiesOf(f)){if(!e.alive||e.tano?.hidden>0)continue;const h=spiderSegHit(x1,y1,x2,y2,e.x,e.y,e.r+5);if(h!==null&&h<best){best=h;hit=e;}}
        if(hit){
          const dealt=damage(hit,SPIDER.webDamage,f,"웹슈터");
          if(hit.alive&&dealt>0&&!hasHarmfulImmunity(hit)){const d=Math.hypot(w.vx,w.vy)||1;hit.vx+=w.vx/d*SPIDER.webKnock;hit.vy+=w.vy/d*SPIDER.webKnock;hit.spiderWebSlow=Math.max(hit.spiderWebSlow||0,SPIDER.webSlowTime);hit.spiderPushWindow=Math.max(hit.spiderPushWindow||0,SPIDER.webPushWindow);hit.spiderPushSourceId=f.id;}
          if(!fastSimMode){spawnHitFlash(hit.x,hit.y,"#e2e8f0",55);spawnParticles(hit.x,hit.y,"#f8fafc",5);}s.webs.splice(i,1);continue;
        }
        w.x=x2;w.y=y2;w.life-=dt;if(w.life<=0||w.x<arena.x-10||w.x>arena.x2+10||w.y<arena.y-10||w.y>arena.y2+10)s.webs.splice(i,1);
      }
    }
    function updateSpiderMan(f,dt){
      const s=f?.spider;if(!s||!f.alive)return;spiderCheckWallEffects(f,dt);updateSpiderVolleyWebs(f,dt);s.swingCd=Math.max(0,s.swingCd-dt);
      if(s.mode==="shot")updateSpiderSwingWeb(f,dt);
      else if(s.mode==="arc"&&s.arc){const a=s.arc;a.t+=dt;const p=clamp(a.t/SPIDER.swingArcTime,0,1),ang=a.start+a.dir*SPIDER.swingArcAngle*p;f.x=clamp(a.ax+Math.cos(ang)*a.radius,arena.x+f.r,arena.x2-f.r);f.y=clamp(a.ay+Math.sin(ang)*a.radius,arena.y+f.r,arena.y2-f.r);f.vx=0;f.vy=0;if(p>=1)spiderFireSwingWeb(f,null,false);}
      else if(s.mode==="chase"&&s.chase){const target=fighters.find(e=>e.id===s.chase.targetId&&e.alive);if(!target){s.mode="idle";s.chase=null;return;}const dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1,contact=f.r+target.r+5;if(d<=contact)spiderFinishMelee(f,target);else{const step=Math.min(Math.max(0,d-contact),SPIDER.chaseSpeed*dt);f.x=clamp(f.x+dx/d*step,arena.x+f.r,arena.x2-f.r);f.y=clamp(f.y+dy/d*step,arena.y+f.r,arena.y2-f.r);f.vx=0;f.vy=0;if(d-step<=contact+.5)spiderFinishMelee(f,target);}}
      if(s.mode!=="idle")return;
      s.volleyCd-=dt;if(s.swingCd<=0){startSpiderSwing(f);return;}
      if(s.volleyLeft<=0&&s.volleyCd<=0){s.volleyLeft=SPIDER.volleyCount;s.volleyTimer=0;s.volleyCd=SPIDER.volleyCooldown;}
      if(s.volleyLeft>0){s.volleyTimer-=dt;while(s.volleyLeft>0&&s.volleyTimer<=0){spiderFireVolleyShot(f);s.volleyLeft--;s.volleyTimer+=SPIDER.volleyGap;}}
    }
    function drawSpiderWebDecal(w){
      const alpha=clamp(w.t/w.max,0,1);ctx.save();ctx.globalAlpha=.25+.65*alpha;ctx.translate(w.x,w.y);ctx.strokeStyle="#f8fafc";ctx.lineWidth=1.4;
      for(let i=0;i<8;i++){const a=i*Math.PI/4;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(Math.cos(a)*30,Math.sin(a)*30);ctx.stroke();}
      for(const r of [9,18,27]){ctx.beginPath();ctx.arc(0,0,r,0,Math.PI*2);ctx.stroke();}ctx.restore();
    }
    function drawSpiderCharacter(f){
      const s=f.spider||{webs:[],wallWebs:[]};
      if(!f.portraitOnly&&!fastSimMode){ctx.save();ctx.beginPath();ctx.rect(arena.x,arena.y,arena.size,arena.size);ctx.clip();for(const w of s.wallWebs||[])drawSpiderWebDecal(w);if(s.swingWeb){ctx.strokeStyle="rgba(248,250,252,.85)";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(f.x,f.y);ctx.lineTo(s.swingWeb.x,s.swingWeb.y);ctx.stroke();}if(s.arc){ctx.strokeStyle="rgba(248,250,252,.82)";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(f.x,f.y);ctx.lineTo(s.arc.ax,s.arc.ay);ctx.stroke();}if(s.chase){const t=fighters.find(e=>e.id===s.chase.targetId&&e.alive);if(t){ctx.strokeStyle="rgba(248,250,252,.9)";ctx.lineWidth=2.4;ctx.beginPath();ctx.moveTo(f.x,f.y);ctx.lineTo(t.x,t.y);ctx.stroke();}}for(const w of s.webs||[]){ctx.fillStyle="#f8fafc";ctx.beginPath();ctx.arc(w.x,w.y,3,0,Math.PI*2);ctx.fill();}ctx.restore();}
      ctx.save();ctx.translate(f.x,f.y);ctx.scale(f.r/20,f.r/20);ctx.fillStyle="#dc2626";ctx.beginPath();ctx.ellipse(0,-3,15,18,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#1d4ed8";ctx.beginPath();ctx.moveTo(-13,8);ctx.lineTo(-8,18);ctx.lineTo(8,18);ctx.lineTo(13,8);ctx.closePath();ctx.fill();ctx.strokeStyle="#111827";ctx.lineWidth=1;for(let i=0;i<6;i++){const a=i*Math.PI/3;ctx.beginPath();ctx.moveTo(0,-3);ctx.lineTo(Math.cos(a)*14,Math.sin(a)*16-3);ctx.stroke();}for(const r of [5,10]){ctx.beginPath();ctx.arc(0,-3,r,0,Math.PI*2);ctx.stroke();}ctx.fillStyle="#f8fafc";ctx.strokeStyle="#111827";ctx.lineWidth=1.5;ctx.beginPath();ctx.ellipse(-5,-6,3.5,6,-.35,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.ellipse(5,-6,3.5,6,.35,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.restore();drawHealthBar(f);drawName(f);
    }
'''
rep('    function skillProgressInfo(f) {',spider_code+'\n    function skillProgressInfo(f) {',1,'spider code insert')

rep('        if (c.id === "conan") initConan(preview);','        if (c.id === "conan") initConan(preview);\n        if (c.id === "spider_man") initSpiderMan(preview);',1,'preview init')
rep('      if (c.id === "conan") initConan(fighter);','      if (c.id === "conan") initConan(fighter);\n      if (c.id === "spider_man") initSpiderMan(fighter);',1,'fighter init')
rep('      if (f.conan) { drawConanCharacter(f); return; }','      if (f.conan) { drawConanCharacter(f); return; }\n      if (f.spider) { drawSpiderCharacter(f); return; }',1,'draw dispatch')
rep('      if (f.conan) updateConan(f, dt);','      if (f.conan) updateConan(f, dt);\n      if (f.spider) updateSpiderMan(f, dt);',1,'update dispatch')

skill='''      if(f.spider){const s=f.spider||{};const active=s.mode&&s.mode!=="idle";return {ratio:active?1:clamp(1-(s.swingCd||0)/SPIDER.swingCooldown,0,1),className:active?"rage-fill":"skill-fill",text:active?(s.mode==="arc"?"웹스윙 · 벽 타기":s.mode==="chase"?"웹스윙 · 적 추격":"웹스윙 · 거미줄 발사"):("웹스윙 "+Math.max(0,s.swingCd||0).toFixed(1)+"초"),extraTextHtml:'<div class="status-skill-label">웹스윙 8초 · 적을 못 맞히면 벽을 축으로 부채꼴 이동 후 다시 발사, 적중할 때까지 반복</div><div class="status-skill-label">비스윙 중 5초마다 웹슈터 6연사 · 발당2·약넉백·0.9초 둔화 · 벽에 밀리면 1.6초 속박 후 타게팅 웹스윙</div>'};}\n'''
rep('      if(f.conan){',skill+'      if(f.conan){',1,'status info')

detail='''      if (c.id === "spider_man") return {damage:"웹스윙 근접타격18 + 벽충돌12 / 웹슈터2×6",tick:"웹스윙8초 · 벽에 걸리면 0.62초 부채꼴 스윙 후 재발사 · 웹슈터5초마다6발(0.09초 간격) · 벽 속박1.6초",tip:"웹스윙 거미줄이 적에게 닿으면 줄을 따라 즉시 접근해 근접타격18과 강한 넉백을 준다. 넉백된 적이 벽에 닿으면 추가12. 거미줄이 적 대신 벽에 닿으면 그 지점을 축으로 부채꼴 웹스윙한 뒤 다시 랜덤 거미줄을 발사하며, 상대에게 적중할 때까지 반복한다. 웹스윙 중이 아닐 때는 5초마다 웹슈터를 6연사한다. 각 탄은 피해2·약한 넉백·0.9초 22% 둔화를 주며, 이 넉백으로 상대가 벽에 닿으면 벽에 거미줄 이펙트와 함께 1.6초 속박된다. 속박 성공 시 웹스윙 쿨타임을 초기화하고 해당 상대를 향해 타게팅 거미줄을 즉시 발사한다."};\n'''
rep('      if (c.id === "conan") return {damage:',detail+'      if (c.id === "conan") return {damage:',1,'detail modal')

rep('      f.conanKnifeSlow=Math.max(0,(f.conanKnifeSlow||0)-dt);','      f.conanKnifeSlow=Math.max(0,(f.conanKnifeSlow||0)-dt);\n      f.spiderWebSlow=Math.max(0,(f.spiderWebSlow||0)-dt);\n      f.spiderPushWindow=Math.max(0,(f.spiderPushWindow||0)-dt);\n      f.spiderWallMark=Math.max(0,(f.spiderWallMark||0)-dt);\n      f.spiderBind=Math.max(0,(f.spiderBind||0)-dt);\n      if(f.spiderBind>0){f.tanoStop=Math.max(f.tanoStop||0,f.spiderBind);f.vx=0;f.vy=0;}',1,'spider timers')

old='''      const conanSlow = conanKnifeSlowMultiplier(f);\n      const boost = f.baseId === "wind_rio" ? rioMoveBoost(f) : (f.speedBoost > 0 ? 1.45 : 1);'''
new='''      const conanSlow = conanKnifeSlowMultiplier(f);\n      const spiderSlow = spiderWebSlowMultiplier(f);\n      const boost = f.baseId === "wind_rio" ? rioMoveBoost(f) : (f.speedBoost > 0 ? 1.45 : 1);'''
if text.count(old)<2: raise SystemExit('missing movement slow anchors')
text=text.replace(old,new,2)
if text.count('* elsaIce * conanSlow;')<2: raise SystemExit('missing speed product anchors')
text=text.replace('* elsaIce * conanSlow;','* elsaIce * conanSlow * spiderSlow;',2)
rep('*conanKnifeSlowMultiplier(f);','*conanKnifeSlowMultiplier(f)*spiderWebSlowMultiplier(f);',1,'Hinta slow')

note='      "v123: 고난 체력을165→160으로 조정. 영화 신캐 \'거미남\' 추가(HP170·이속2.9). 8초마다 랜덤 거미줄을 발사해 적중 시 줄을 따라 접근해 근접18+강넉백, 벽충돌 시 추가12. 적 대신 벽에 맞으면 0.62초 부채꼴 웹스윙 뒤 다시 랜덤 거미줄을 발사하며 적중할 때까지 반복. 웹스윙 중이 아닐 때는 5초마다 웹슈터6연사(발당2·약넉백·0.9초 22% 둔화). 웹슈터 넉백으로 벽에 닿으면 1.6초 거미줄 속박, 즉시 웹스윙 쿨 초기화 후 속박 대상을 타게팅해 발사.",\n'
rep('      const patchNotes = [\n','      const patchNotes = [\n'+note,1,'patch note')

path.write_text(text,encoding='utf-8')
scripts=re.findall(r'<script[^>]*>(.*?)</script>',text,re.S)
Path('/tmp/index_js_check.js').write_text('\n'.join(scripts),encoding='utf-8')
print('patched',len(text),'bytes')
