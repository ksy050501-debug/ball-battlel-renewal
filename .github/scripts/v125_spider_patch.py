from pathlib import Path
import re

p=Path('index.html')
t=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global t
    if old not in t:
        raise SystemExit(f'missing {label}')
    t=t.replace(old,new,1)

rep('<title>볼배틀 리뉴얼 v124</title>','<title>볼배틀 리뉴얼 v125</title>','title')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v124</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v125</h1>','header')

rep('''    const SPIDER = {
      swingCooldown:8, swingWebSpeed:680, swingArcTime:.62, swingArcAngle:1.55,
      swingMinRadius:72, swingMaxRadius:135, chaseSpeed:720,
      meleeDamage:18, meleeKnock:620, wallDamage:12, wallMarkTime:1.25,
      volleyCooldown:5, volleyCount:6, volleyGap:.09, webSpeed:560, webDamage:2,
      webKnock:105, webSlow:.78, webSlowTime:.9, webPushWindow:1.15, bindTime:1.6
    };''','''    const SPIDER = {
      swingCooldown:8, swingWebSpeed:680, swingArcTime:.62, swingArcAngle:1.55,
      swingMinRadius:72, swingMaxRadius:135, swingMinAnchorDistance:140, swingMaxChains:5, chaseSpeed:720,
      meleeDamage:18, meleeKnock:620, wallDamage:12, wallMarkTime:1.25,
      volleyCooldown:5, volleyCount:6, volleyGap:.09, webSpeed:560, webDamage:2,
      webKnock:105, webSlow:.78, webSlowTime:.9, webPushWindow:1.15, bindTime:1.6
    };''','SPIDER constants')

rep('''      f.spider={swingCd:SPIDER.swingCooldown,mode:"idle",swingWeb:null,arc:null,chase:null,
        webs:[],volleyCd:2.4,volleyLeft:0,volleyTimer:0,wallWebs:[]};''','''      f.spider={swingCd:SPIDER.swingCooldown,mode:"idle",swingWeb:null,arc:null,chase:null,swingCount:0,
        webs:[],volleyCd:2.4,volleyLeft:0,volleyTimer:0,wallWebs:[]};''','spider init')

needle='''    function spiderFireSwingWeb(f,targetId=null,initial=false){
      const s=f?.spider;if(!s||!f.alive)return;
      let a=Math.random()*Math.PI*2;
      const target=targetId?fighters.find(e=>e.id===targetId&&e.alive):null;
      if(target)a=Math.atan2(target.y-f.y,target.x-f.x);
      s.mode="shot";s.arc=null;s.chase=null;
      s.swingWeb={x:f.x,y:f.y,vx:Math.cos(a)*SPIDER.swingWebSpeed,vy:Math.sin(a)*SPIDER.swingWebSpeed,life:1.35,targetId:target?.id||null};
      if(initial)s.swingCd=SPIDER.swingCooldown;
      if(!fastSimMode){spawnFloatingText(f.x,f.y-f.r-26,target?"타게팅 웹!":"웹스윙!","#e2e8f0");playSound("magic",.78);}
    }
    function startSpiderSwing(f,targetId=null){const s=f?.spider;if(!s||!f.alive)return;s.volleyLeft=0;s.volleyTimer=0;spiderFireSwingWeb(f,targetId,true);}'''
repl='''    function spiderFarWallAnchor(f){
      const margin=72,candidates=[];
      for(let i=0;i<16;i++){
        const wall=Math.floor(Math.random()*4);
        let p;
        if(wall===0)p={x:arena.x,y:rand(arena.y+margin,arena.y2-margin)};
        else if(wall===1)p={x:arena.x2,y:rand(arena.y+margin,arena.y2-margin)};
        else if(wall===2)p={x:rand(arena.x+margin,arena.x2-margin),y:arena.y};
        else p={x:rand(arena.x+margin,arena.x2-margin),y:arena.y2};
        candidates.push(p);
      }
      const valid=candidates.filter(p=>Math.hypot(p.x-f.x,p.y-f.y)>=SPIDER.swingMinAnchorDistance);
      if(valid.length)return pick(valid);
      return candidates.reduce((best,p)=>Math.hypot(p.x-f.x,p.y-f.y)>Math.hypot(best.x-f.x,best.y-f.y)?p:best,candidates[0]);
    }
    function spiderFireSwingWeb(f,targetId=null,initial=false){
      const s=f?.spider;if(!s||!f.alive)return;
      let target=targetId?fighters.find(e=>e.id===targetId&&e.alive):null;
      // 마지막(5번째) 시도는 적 방향을 우선해 웹스윙이 공격으로 이어질 가능성을 높인다.
      if(!target&&(s.swingCount||0)>=SPIDER.swingMaxChains-1)target=nearestEnemy(f)?.enemy||null;
      let a;
      if(target)a=Math.atan2(target.y-f.y,target.x-f.x);
      else{const anchor=spiderFarWallAnchor(f);a=Math.atan2(anchor.y-f.y,anchor.x-f.x);}
      s.mode="shot";s.arc=null;s.chase=null;
      s.swingWeb={x:f.x,y:f.y,vx:Math.cos(a)*SPIDER.swingWebSpeed,vy:Math.sin(a)*SPIDER.swingWebSpeed,life:1.35,targetId:target?.id||null};
      if(initial)s.swingCd=SPIDER.swingCooldown;
      if(!fastSimMode){spawnFloatingText(f.x,f.y-f.r-26,target?"타게팅 웹!":"웹스윙!","#e2e8f0");playSound("magic",.78);}
    }
    function startSpiderSwing(f,targetId=null){const s=f?.spider;if(!s||!f.alive)return;s.volleyLeft=0;s.volleyTimer=0;s.swingCount=0;spiderFireSwingWeb(f,targetId,true);}'''
rep(needle,repl,'swing fire/start')

rep('''    function spiderBeginArc(f,ax,ay){
      const s=f.spider,dx=f.x-ax,dy=f.y-ay;
      const radius=Math.max(1,Math.hypot(dx,dy));
      const start=Math.atan2(dy,dx);
      const swingAngle=clamp(150/radius,.28,1.28);
      const cx=(arena.x+arena.x2)/2,cy=(arena.y+arena.y2)/2;
      const score=dir=>{
        const a=start+dir*swingAngle;
        const ex=ax+Math.cos(a)*radius,ey=ay+Math.sin(a)*radius;
        const ox=Math.max(0,arena.x+f.r-ex,ex-(arena.x2-f.r));
        const oy=Math.max(0,arena.y+f.r-ey,ey-(arena.y2-f.r));
        return (ox*ox+oy*oy)*20+Math.hypot(ex-cx,ey-cy);
      };
      const dir=score(1)<=score(-1)?1:-1;
      s.mode="arc";s.swingWeb=null;s.chase=null;
      s.arc={ax,ay,radius,start,dir,swingAngle,t:0};
      f.vx=0;f.vy=0;
      if(!fastSimMode)spawnBlast(ax,ay,26,"#e2e8f0");
    }''','''    function spiderBeginArc(f,ax,ay){
      const s=f.spider,dx=f.x-ax,dy=f.y-ay;
      const radius=Math.max(1,Math.hypot(dx,dy));
      // 너무 가까운 벽은 스윙축으로 쓰지 않는다. 마지막 시도라면 연쇄를 끝낸다.
      if(radius<SPIDER.swingMinAnchorDistance){
        if((s.swingCount||0)>=SPIDER.swingMaxChains-1){spiderStopSwing(f);return;}
        spiderFireSwingWeb(f,null,false);return;
      }
      s.swingCount=(s.swingCount||0)+1;
      const start=Math.atan2(dy,dx);
      const swingAngle=clamp(150/radius,.28,1.28);
      const cx=(arena.x+arena.x2)/2,cy=(arena.y+arena.y2)/2;
      const score=dir=>{
        const a=start+dir*swingAngle;
        const ex=ax+Math.cos(a)*radius,ey=ay+Math.sin(a)*radius;
        const ox=Math.max(0,arena.x+f.r-ex,ex-(arena.x2-f.r));
        const oy=Math.max(0,arena.y+f.r-ey,ey-(arena.y2-f.r));
        return (ox*ox+oy*oy)*20+Math.hypot(ex-cx,ey-cy);
      };
      const dir=score(1)<=score(-1)?1:-1;
      s.mode="arc";s.swingWeb=null;s.chase=null;
      s.arc={ax,ay,radius,start,dir,swingAngle,t:0};
      f.vx=0;f.vy=0;
      if(!fastSimMode)spawnBlast(ax,ay,26,"#e2e8f0");
    }''','spiderBeginArc')

rep('''    function spiderFinishMelee(f,target){
      const s=f.spider,dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1;
      const dealt=damage(target,SPIDER.meleeDamage,f,"웹스윙 근접타격");
      if(target.alive&&dealt>0){target.vx=dx/d*SPIDER.meleeKnock;target.vy=dy/d*SPIDER.meleeKnock;target.punchFlight=Math.max(target.punchFlight||0,.34);target.punchSource=f;target.punchWallPower=0;target.punchWallHits=0;target.spiderWallMark=Math.max(target.spiderWallMark||0,SPIDER.wallMarkTime);target.spiderWallSourceId=f.id;}
      if(!fastSimMode){spawnHitFlash(target.x,target.y,"#f8fafc",115);spawnBlast(target.x,target.y,72,"#dc2626");playSound("hit",1.0);}
      s.mode="idle";s.chase=null;s.swingCd=SPIDER.swingCooldown;
    }''','''    function spiderFinishMelee(f,target){
      const s=f.spider,dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1;
      const dealt=damage(target,SPIDER.meleeDamage,f,"웹스윙 근접타격");
      if(target.alive&&dealt>0){target.vx=dx/d*SPIDER.meleeKnock;target.vy=dy/d*SPIDER.meleeKnock;target.punchFlight=Math.max(target.punchFlight||0,.34);target.punchSource=f;target.punchWallPower=0;target.punchWallHits=0;target.spiderWallMark=Math.max(target.spiderWallMark||0,SPIDER.wallMarkTime);target.spiderWallSourceId=f.id;}
      if(!fastSimMode){spawnHitFlash(target.x,target.y,"#f8fafc",115);spawnBlast(target.x,target.y,72,"#dc2626");playSound("hit",1.0);}
      s.mode="idle";s.chase=null;s.arc=null;s.swingWeb=null;s.swingCount=0;s.swingCd=SPIDER.swingCooldown;
    }
    function spiderStopSwing(f){
      const s=f?.spider;if(!s)return;
      s.mode="idle";s.swingWeb=null;s.arc=null;s.chase=null;s.swingCount=0;s.swingCd=SPIDER.swingCooldown;
      const v=randomVelocity(f.baseSpeed||f.speed||2.9);f.vx=v.vx;f.vy=v.vy;
      if(!fastSimMode)spawnFloatingText(f.x,f.y-f.r-28,"웹스윙 종료","#cbd5e1");
    }''','spider finish/stop')

old='''      else if(s.mode==="arc"&&s.arc){const a=s.arc;a.t+=dt;const p=clamp(a.t/SPIDER.swingArcTime,0,1),ang=a.start+a.dir*(a.swingAngle||SPIDER.swingArcAngle)*p;f.x=clamp(a.ax+Math.cos(ang)*a.radius,arena.x+f.r,arena.x2-f.r);f.y=clamp(a.ay+Math.sin(ang)*a.radius,arena.y+f.r,arena.y2-f.r);f.vx=0;f.vy=0;if(p>=1)spiderFireSwingWeb(f,null,false);}'''
new='''      else if(s.mode==="arc"&&s.arc){
        const a=s.arc;a.t+=dt;
        const p=clamp(a.t/SPIDER.swingArcTime,0,1),ang=a.start+a.dir*(a.swingAngle||SPIDER.swingArcAngle)*p;
        f.x=clamp(a.ax+Math.cos(ang)*a.radius,arena.x+f.r,arena.x2-f.r);f.y=clamp(a.ay+Math.sin(ang)*a.radius,arena.y+f.r,arena.y2-f.r);f.vx=0;f.vy=0;
        // 벽을 타는 도중 몸으로 적을 들이받아도 웹스윙 근접타격이 성공한다.
        const swingHit=enemiesOf(f).find(e=>e.alive&&!(e.tano?.hidden>0)&&Math.hypot(e.x-f.x,e.y-f.y)<=f.r+e.r+5);
        if(swingHit){spiderFinishMelee(f,swingHit);return;}
        if(p>=1){if((s.swingCount||0)>=SPIDER.swingMaxChains)spiderStopSwing(f);else spiderFireSwingWeb(f,null,false);}
      }'''
rep(old,new,'arc update')

# 상태창에 현재 연속 스윙 횟수 표시
old='s.mode==="arc"?"웹스윙 · 벽 타기":s.mode==="chase"?"웹스윙 · 적 추격":"웹스윙 · 거미줄 발사"'
new='s.mode==="arc"?("웹스윙 · 벽 타기 "+(s.swingCount||0)+"/"+SPIDER.swingMaxChains):s.mode==="chase"?"웹스윙 · 적 추격":"웹스윙 · 거미줄 발사"'
rep(old,new,'skill progress arc text')

note='      "v125: 거미남 웹스윙 전투성을 개선했습니다. 웹스윙 부채꼴 이동 중 적과 몸으로 충돌해도 즉시 근접18+강넉백 공격이 발동하고, 벽까지 밀리면 기존 벽충돌12도 이어집니다. 140px보다 가까운 벽은 웹스윙 앵커로 사용하지 않으며 랜덤 웹도 먼 벽 지점을 우선 조준합니다. 벽 웹스윙 연쇄는 최대5회까지만 이어지고 5번째 시도는 적 방향을 우선 조준하며, 5회 모두 실패하면 웹스윙을 종료하고 8초 쿨타임으로 복귀합니다.",\n'
anchor='      "v124: 거미남 웹스윙 이동을 수정했습니다.'
if anchor not in t: raise SystemExit('missing patch note anchor')
t=t.replace(anchor,note+anchor,1)

p.write_text(t,encoding='utf-8')

scripts=re.findall(r'<script[^>]*>([\s\S]*?)</script>',t)
Path('/tmp/index_js_check.js').write_text('\n'.join(scripts),encoding='utf-8')
