from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')
assert '<title>볼배틀 리뉴얼 v128</title>' in s
assert '<h1 id="mainTitle">볼배틀 리뉴얼 v128</h1>' in s
new_spider=r'''    const SPIDER = {
      chaseSpeed:720,
      meleeDamage:18, meleeKnock:620, wallDamage:12, wallMarkTime:1.25,
      volleyCooldown:5, volleyCount:6, volleyGap:.09, webSpeed:560, webDamage:2,
      webKnock:105, webKnockDuration:.22, webSlow:.78, webSlowTime:.9, bindTime:1.6
    };
    function initSpiderMan(f){
      f.spider={mode:"idle",chase:null,webs:[],volleyCd:2.4,volleyLeft:0,volleyTimer:0,wallWebs:[]};
    }
    function webSlowMultiplier(f){return (f?.webSlow||0)>0&&!hasHarmfulImmunity(f)?SPIDER.webSlow:1;}
    function spiderSegHit(x1,y1,x2,y2,cx,cy,r){
      const dx=x2-x1,dy=y2-y1,l2=dx*dx+dy*dy||1,t=clamp(((cx-x1)*dx+(cy-y1)*dy)/l2,0,1),px=x1+dx*t,py=y1+dy*t;
      return Math.hypot(px-cx,py-cy)<=r?t:null;
    }
    function startSpiderSwing(f,targetId){
      const s=f?.spider,target=fighters.find(e=>e.id===targetId&&e.alive);if(!s||!f.alive||!target)return false;
      s.volleyLeft=0;s.volleyTimer=0;s.mode="chase";s.chase={targetId:target.id};
      if(!fastSimMode){spawnFloatingText(f.x,f.y-f.r-28,"웹스윙 돌진!","#e2e8f0");playSound("magic",.78);}return true;
    }
    function spiderFinishMelee(f,target){
      const s=f.spider,dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1,dealt=damage(target,SPIDER.meleeDamage,f,"웹스윙 근접타격");
      if(target.alive&&dealt>0){target.vx=dx/d*SPIDER.meleeKnock;target.vy=dy/d*SPIDER.meleeKnock;target.punchFlight=Math.max(target.punchFlight||0,.34);target.punchSource=f;target.punchWallPower=0;target.punchWallHits=0;target.spiderWallMark=Math.max(target.spiderWallMark||0,SPIDER.wallMarkTime);target.spiderWallSourceId=f.id;}
      if(!fastSimMode){spawnHitFlash(target.x,target.y,"#f8fafc",115);spawnBlast(target.x,target.y,72,"#dc2626");playSound("hit",1.0);}s.mode="idle";s.chase=null;
    }
    function spiderFireVolleyShot(f){
      const s=f.spider,target=nearestEnemy(f)?.enemy;if(!target)return;const a=Math.atan2(target.y-f.y,target.x-f.x)+rand(-.075,.075);
      s.webs.push({x:f.x,y:f.y,vx:Math.cos(a)*SPIDER.webSpeed,vy:Math.sin(a)*SPIDER.webSpeed,life:1.35});if(!fastSimMode)playSound("magic",.42);
    }
    function bindStunTarget(f,target){
      if(!target?.alive||hasHarmfulImmunity(target))return false;
      target.bindStun=Math.max(target.bindStun||0,SPIDER.bindTime);target.webSlow=0;target.webKnockTime=0;target.webKnockSourceId="";target.vx=0;target.vy=0;
      const s=f.spider;s.wallWebs.push({x:target.x,y:target.y,t:SPIDER.bindTime+.35,max:SPIDER.bindTime+.35});
      if(!fastSimMode){spawnBlast(target.x,target.y,54,"#e2e8f0");spawnParticles(target.x,target.y,"#f8fafc",24);spawnFloatingText(target.x,target.y-target.r-38,"벽 거미줄 속박!","#f8fafc");}
      startSpiderSwing(f,target.id);return true;
    }
    function spiderCheckWallEffects(f,dt){
      for(const target of enemiesOf(f)){if(!target.alive)continue;const nearWall=target.x-target.r<=arena.x+2||target.x+target.r>=arena.x2-2||target.y-target.r<=arena.y+2||target.y+target.r>=arena.y2-2;
        if((target.spiderWallMark||0)>0&&target.spiderWallSourceId===f.id&&nearWall){target.spiderWallMark=0;const dealt=damage(target,SPIDER.wallDamage,f,"웹스윙 벽충돌");if(!fastSimMode){spawnBlast(target.x,target.y,76,"#f8fafc");spawnFloatingText(target.x,target.y-target.r-38,"벽충돌 -"+Math.round(dealt),"#fecaca");}}
        if((target.webKnockTime||0)>0&&target.webKnockSourceId===f.id&&nearWall&&!(target.bindStun>0))bindStunTarget(f,target);
      }
      f.spider.wallWebs.forEach(w=>w.t-=dt);f.spider.wallWebs=f.spider.wallWebs.filter(w=>w.t>0);
    }
    function updateSpiderVolleyWebs(f,dt){
      const s=f.spider;for(let i=s.webs.length-1;i>=0;i--){const w=s.webs[i],x1=w.x,y1=w.y,x2=w.x+w.vx*dt,y2=w.y+w.vy*dt;let hit=null,best=2;
        for(const e of enemiesOf(f)){if(!e.alive||e.tano?.hidden>0)continue;const h=spiderSegHit(x1,y1,x2,y2,e.x,e.y,e.r+5);if(h!==null&&h<best){best=h;hit=e;}}
        if(hit){const dealt=damage(hit,SPIDER.webDamage,f,"웹슈터");if(hit.alive&&dealt>0&&!hasHarmfulImmunity(hit)){const d=Math.hypot(w.vx,w.vy)||1;hit.vx+=w.vx/d*SPIDER.webKnock;hit.vy+=w.vy/d*SPIDER.webKnock;refreshCcTimer(hit,"webSlow",SPIDER.webSlowTime);hit.webKnockTime=Math.max(hit.webKnockTime||0,SPIDER.webKnockDuration);hit.webKnockSourceId=f.id;}if(!fastSimMode){spawnHitFlash(hit.x,hit.y,"#e2e8f0",55);spawnParticles(hit.x,hit.y,"#f8fafc",5);}s.webs.splice(i,1);continue;}
        w.x=x2;w.y=y2;w.life-=dt;if(w.life<=0||w.x<arena.x-10||w.x>arena.x2+10||w.y<arena.y-10||w.y>arena.y2+10)s.webs.splice(i,1);
      }
    }
    function updateSpiderMan(f,dt){
      const s=f?.spider;if(!s||!f.alive)return;spiderCheckWallEffects(f,dt);updateSpiderVolleyWebs(f,dt);
      if(s.mode==="chase"&&s.chase){const target=fighters.find(e=>e.id===s.chase.targetId&&e.alive);if(!target){s.mode="idle";s.chase=null;return;}const dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1,contact=f.r+target.r+5;if(d<=contact)spiderFinishMelee(f,target);else{const step=Math.min(Math.max(0,d-contact),SPIDER.chaseSpeed*dt);f.x=clamp(f.x+dx/d*step,arena.x+f.r,arena.x2-f.r);f.y=clamp(f.y+dy/d*step,arena.y+f.r,arena.y2-f.r);f.vx=0;f.vy=0;if(d-step<=contact+.5)spiderFinishMelee(f,target);}}
      if(s.mode!=="idle")return;s.volleyCd-=dt;if(s.volleyLeft<=0&&s.volleyCd<=0){s.volleyLeft=SPIDER.volleyCount;s.volleyTimer=0;s.volleyCd=SPIDER.volleyCooldown;}if(s.volleyLeft>0){s.volleyTimer-=dt;while(s.volleyLeft>0&&s.volleyTimer<=0){spiderFireVolleyShot(f);s.volleyLeft--;s.volleyTimer+=SPIDER.volleyGap;}}
    }
'''
s,n=re.subn(r'    const SPIDER = \{.*?(?=    function drawSpiderWebDecal\(w\)\{)',new_spider,s,count=1,flags=re.S);assert n==1,n
s=s.replace('if(s.swingWeb){ctx.strokeStyle="rgba(248,250,252,.85)";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(f.x,f.y);ctx.lineTo(s.swingWeb.x,s.swingWeb.y);ctx.stroke();}if(s.arc){ctx.strokeStyle="rgba(248,250,252,.82)";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(f.x,f.y);ctx.lineTo(s.arc.ax,s.arc.ay);ctx.stroke();}','')
old='''      { id: "spider_man", name: "거미남", mark: "🕷", role: "영화", color: "#dc2626", hp: 170, attack: 0, speed: 2.9, range: 0,\n        skillName: "웹스윙 · 웹슈터", condition: "웹스윙 8초 · 빗나가면 먼 벽으로 최대5연속 스윙 · 비스윙 중 5초마다 거미줄 6연사", desc: "거미줄을 벽과 적에게 걸어 경기장을 연속으로 가로지른다. 평상시에는 웹슈터 연사로 적을 벽에 몰아붙여 속박한 뒤 즉시 타게팅 웹스윙으로 추격한다." },'''
new='''      { id: "spider_man", name: "거미남", mark: "🕷", role: "영화", color: "#dc2626", hp: 170, attack: 0, speed: 2.9, range: 0,\n        skillName: "웹슈터 · 웹스윙", condition: "5초마다 거미줄 6연사 · 웹슈터 넉백 중 벽충돌 시 속박→웹스윙 돌진", desc: "웹슈터 연사로 적을 밀어낸다. 웹슈터에 맞아 밀려나는 바로 그 순간 벽에 충돌하면 속박하고 즉시 타게팅 웹스윙으로 돌진한다." },''';assert old in s;s=s.replace(old,new,1)
old='''      if (c.id === "spider_man") return {damage:"웹스윙 근접타격18 + 벽충돌12 / 웹슈터2×6",tick:"웹스윙8초 · 벽에 걸리면 0.62초 부채꼴 스윙 후 재발사 · 웹슈터5초마다6발(0.09초 간격) · 벽 속박1.6초",tip:"웹스윙 거미줄이 적에게 닿으면 줄을 따라 즉시 접근해 근접타격18과 강한 넉백을 준다. 넉백된 적이 벽에 닿으면 추가12. 거미줄이 적 대신 벽에 닿으면 그 지점을 축으로 부채꼴 웹스윙한 뒤 다시 랜덤 거미줄을 발사하며, 상대에게 적중할 때까지 반복한다. 웹스윙 중이 아닐 때는 5초마다 웹슈터를 6연사한다. 각 탄은 피해2·약한 넉백·0.9초 22% 둔화를 주며, 이 넉백으로 상대가 벽에 닿으면 벽에 거미줄 이펙트와 함께 1.6초 속박된다. 속박 성공 시 웹스윙 쿨타임을 초기화하고 해당 상대를 향해 타게팅 거미줄을 즉시 발사한다."};'''
new='''      if (c.id === "spider_man") return {damage:"웹슈터2×6 / 속박 연계 웹스윙 근접타격18 + 벽충돌12",tick:"웹슈터5초마다6발(0.09초 간격) · 웹슈터 넉백 판정0.22초 · 그동안 벽충돌 시 속박1.6초→웹스윙 돌진",tip:"5초마다 웹슈터를 6연사한다. 각 탄은 피해2·약한 넉백·0.9초 22% 둔화를 준다. 웹슈터에 맞아 밀려나는 0.22초 안에 실제로 벽에 충돌한 경우에만 1.6초 속박되며, 예전에 맞은 뒤 한참 후 벽에 닿는 것은 속박되지 않는다. 속박 성공 시 해당 상대에게만 웹스윙 돌진을 사용해 근접타격18과 강한 넉백을 주고, 그 넉백으로 벽에 닿으면 추가12 피해를 준다. 자동·랜덤 웹스윙과 벽 부채꼴 연쇄 스윙은 없다."};''';assert old in s;s=s.replace(old,new,1)
old='''      if(f.spider){const s=f.spider||{};const active=s.mode&&s.mode!=="idle";return {ratio:active?1:clamp(1-(s.swingCd||0)/SPIDER.swingCooldown,0,1),className:active?"rage-fill":"skill-fill",text:active?(s.mode==="arc"?("웹스윙 · 벽 타기 "+(s.swingCount||0)+"/"+SPIDER.swingMaxChains):s.mode==="chase"?"웹스윙 · 적 추격":"웹스윙 · 거미줄 발사"):("웹스윙 "+Math.max(0,s.swingCd||0).toFixed(1)+"초"),extraTextHtml:'<div class="status-skill-label">웹스윙 8초 · 먼 벽으로 최대5연속 · 스윙 중 몸 충돌도 근접18+강넉백</div><div class="status-skill-label">비스윙 중 5초마다 웹슈터 6연사 · 발당2·약넉백·0.9초 둔화 · 벽에 밀리면 1.6초 속박 후 타게팅 웹스윙</div>'};}'''
new='''      if(f.spider){const s=f.spider||{};const active=s.mode==="chase",firing=(s.volleyLeft||0)>0;return {ratio:active||firing?1:clamp(1-Math.max(0,s.volleyCd||0)/SPIDER.volleyCooldown,0,1),className:active?"rage-fill":"skill-fill",text:active?"웹스윙 · 적 추격":firing?("웹슈터 연사 · "+(SPIDER.volleyCount-(s.volleyLeft||0))+"/"+SPIDER.volleyCount):("웹슈터 "+Math.max(0,s.volleyCd||0).toFixed(1)+"초"),extraTextHtml:'<div class="status-skill-label">웹슈터 5초마다 6연사 · 발당2·약넉백·0.9초 둔화</div><div class="status-skill-label">웹슈터 넉백 중 벽에 충돌해야만 1.6초 속박 · 속박 성공 시 타게팅 웹스윙 돌진18+강넉백</div>'};}''';assert old in s;s=s.replace(old,new,1)
old='''      f.webSlow=Math.max(0,(f.webSlow||0)-dt);\n      f.spiderPushWindow=Math.max(0,(f.spiderPushWindow||0)-dt);\n      f.spiderWallMark=Math.max(0,(f.spiderWallMark||0)-dt);''';new='''      f.webSlow=Math.max(0,(f.webSlow||0)-dt);\n      f.webKnockTime=Math.max(0,(f.webKnockTime||0)-dt);\n      if(f.webKnockTime<=0)f.webKnockSourceId="";\n      f.spiderWallMark=Math.max(0,(f.spiderWallMark||0)-dt);''';assert old in s;s=s.replace(old,new,1)
s=s.replace('<title>볼배틀 리뉴얼 v128</title>','<title>볼배틀 리뉴얼 v129</title>',1).replace('<h1 id="mainTitle">볼배틀 리뉴얼 v128</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v129</h1>',1)
marker='      const patchNotes = [\n';note='      "v129: 거미남의 자동·랜덤 웹스윙 시스템을 삭제했습니다. 8초 자동 웹스윙·벽 앵커·부채꼴 스윙·최대5연속 재발사를 제거하고, 웹슈터와 웹슈터 벽속박 연계 타게팅 웹스윙 돌진만 유지합니다. 웹슈터에 맞은 뒤 1.15초 동안 벽속박 가능하던 지연 판정을 삭제하고, 각 탄의 실제 넉백 직후 0.22초 동안 벽에 충돌한 경우에만 1.6초 속박→타게팅 웹스윙이 발동합니다. 웹슈터2×6·22% 둔화0.9초·웹스윙18+강넉백·웹스윙 벽충돌12 수치는 유지합니다.",\n';assert marker in s;s=s.replace(marker,marker+note,1)
for x in ['swingCooldown:8','swingArcTime:.62','swingMaxChains:5','swingMinAnchorDistance:140','webPushWindow:1.15','spiderPushWindow','spiderPushSourceId','spiderBeginArc','updateSpiderSwingWeb','spiderFireSwingWeb','spiderWallPoint','s.swingCd','s.swingWeb','s.arc','s.swingCount']:assert x not in s,x
for x in ['webKnockDuration:.22','webKnockTime','webKnockSourceId','startSpiderSwing(f,target.id)','웹슈터 넉백 중 벽충돌 시 속박→웹스윙 돌진','볼배틀 리뉴얼 v129']:assert x in s,x
p.write_text(s,encoding='utf-8')