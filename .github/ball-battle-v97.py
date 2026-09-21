from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"replace expected {count}, found {n}: {old[:140]!r}")
    t=t.replace(old,new,count)

def before(anchor,addition,count=1):
    global t
    n=t.count(anchor)
    if n!=count:
        raise SystemExit(f"anchor expected {count}, found {n}: {anchor[:140]!r}")
    t=t.replace(anchor,addition+anchor,count)

rep('<title>볼배틀 리뉴얼 v96</title>','<title>볼배틀 리뉴얼 v97</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v96</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v97</h1>')

before(
'''      { id: "hinta", name: "힌타", mark: "10", role: "애니", color: "#f97316", hp: 170, attack: 12, speed: 3.0, range: 0,''',
'''      { id: "bald_cape", name: "대머리망토", mark: "○", role: "애니", color: "#facc15", hp: 170, attack: 0, speed: 2.7, range: 0,
        skillName: "보통펀치 · 연속 보통펀치 · 진심펀치", condition: "5.2초마다 보통45% / 연속35% / 진심20%", desc: "보통펀치는 활성화 뒤 벽에 튕길 때마다 가속하고 5회째 가장 가까운 적에게 돌진한다. 명중하면 적을 날려 보내며 벽 충돌 추가 피해를 준다. 연속 보통펀치는 짧고 넓은 원뿔 다단히트, 진심펀치는 무작위 방향의 좁은 붉은 부채꼴을 맵 끝까지 예고한 뒤 강력한 충격파를 발사한다." },
'''
)

before(
'''    const HINTA = { startDelay: 5, respawn: 5, ballRadius: 10, pickupBonus: 24,''',
r'''    const BALD_CAPE = {
      period:5.2, normalChance:.45, comboChance:.35,
      normalBounces:5, bounceAccel:1.20, dashSpeed:650, dashDuration:.82,
      normalDamage:12, wallDamage:8, wallKnockSpeed:720, wallKnockDuration:.34,
      comboRange:108, comboHalfAngle:Math.PI*43/180, comboHits:6, comboDamage:2, comboInterval:.12,
      seriousWindup:1.3, seriousDamage:30, seriousHalfAngle:Math.PI*11/180
    };

    function initBaldCape(f){
      f.baldCape={cd:2.8,mode:"",normalActive:false,bounces:0,dash:0,combo:null,serious:null,punchAnim:null};
    }
    function baldCapeBlocked(f){
      return !f?.alive||f.tanoStop>0||f.punchHold>0||f.punchFlight>0||f.vampSuppressed>0||f.joltStop>0||isCasting(f);
    }
    function baldCapeAngleDiff(a,b){return Math.abs(Math.atan2(Math.sin(a-b),Math.cos(a-b)));}
    function baldCapeConeTargets(f,angle,range,halfAngle){
      return enemiesOf(f).filter(e=>{
        if(!e.alive||e.tano?.hidden>0||(e.dodoVoid||0)>0)return false;
        const dx=e.x-f.x,dy=e.y-f.y,d=Math.hypot(dx,dy);
        if(d>range+e.r)return false;
        const extra=Math.asin(Math.min(1,e.r/Math.max(e.r,d)));
        return baldCapeAngleDiff(Math.atan2(dy,dx),angle)<=halfAngle+extra;
      });
    }
    function baldCapeRestoreCruise(f){
      const speed=(f.baseSpeed||2.7)*44;
      let a=Math.atan2(f.vy,f.vx);if(!Number.isFinite(a))a=rand(0,Math.PI*2);
      f.vx=Math.cos(a)*speed;f.vy=Math.sin(a)*speed;
    }
    function startBaldCapeSkill(f){
      const b=f.baldCape;if(!b||baldCapeBlocked(f))return false;
      const roll=Math.random();b.cd=BALD_CAPE.period;
      if(roll<BALD_CAPE.normalChance){
        b.mode="normal";b.normalActive=true;b.bounces=0;b.dash=0;
        const speed=Math.max((f.baseSpeed||2.7)*44,Math.hypot(f.vx,f.vy));
        let a=Math.atan2(f.vy,f.vx);if(!Number.isFinite(a))a=rand(0,Math.PI*2);
        f.vx=Math.cos(a)*speed;f.vy=Math.sin(a)*speed;
        spawnFloatingText(f.x,f.y-f.r-38,"보통펀치 준비","#fde68a");
        log("<strong>대머리망토</strong> 보통펀치 준비 · 벽 반사마다 가속","스킬");
        return true;
      }
      if(roll<BALD_CAPE.normalChance+BALD_CAPE.comboChance){
        const target=nearestEnemy(f).enemy;
        const angle=target?Math.atan2(target.y-f.y,target.x-f.x):rand(-Math.PI,Math.PI);
        b.mode="combo";b.combo={angle:angle,hitsLeft:BALD_CAPE.comboHits,tick:0,life:BALD_CAPE.comboInterval*BALD_CAPE.comboHits+.08};
        spawnFloatingText(f.x,f.y-f.r-38,"연속 보통펀치!","#fef08a");
        log("<strong>대머리망토</strong> 연속 보통펀치","스킬");
        return true;
      }
      const angle=rand(-Math.PI,Math.PI);
      b.mode="serious";b.serious={angle:angle,timer:BALD_CAPE.seriousWindup,firedFlash:0,savedVx:f.vx,savedVy:f.vy};
      f.vx=0;f.vy=0;
      spawnFloatingText(f.x,f.y-f.r-38,"진심펀치 예고","#fca5a5");
      playSound("warning",1);
      log("<strong>대머리망토</strong> 진심펀치 · 무작위 방향 충격파 예고","스킬");
      return true;
    }
    function baldCapeWallBounce(f){
      const b=f?.baldCape;if(!b||!b.normalActive||b.dash>0)return;
      b.bounces=Math.min(BALD_CAPE.normalBounces,b.bounces+1);
      const current=Math.max((f.baseSpeed||2.7)*44,Math.hypot(f.vx,f.vy));
      const next=current*BALD_CAPE.bounceAccel,a=Math.atan2(f.vy,f.vx);
      f.vx=Math.cos(a)*next;f.vy=Math.sin(a)*next;
      spawnFloatingText(f.x,f.y-f.r-34,"가속 "+b.bounces+"/"+BALD_CAPE.normalBounces,"#fde047");
      spawnParticles(f.x,f.y,"#fef08a",5+b.bounces);
      if(b.bounces>=BALD_CAPE.normalBounces){
        const target=nearestEnemy(f).enemy;
        if(!target){b.normalActive=false;b.mode="";baldCapeRestoreCruise(f);return;}
        const a2=Math.atan2(target.y-f.y,target.x-f.x);
        b.dash=BALD_CAPE.dashDuration;
        f.vx=Math.cos(a2)*BALD_CAPE.dashSpeed;f.vy=Math.sin(a2)*BALD_CAPE.dashSpeed;
        spawnFloatingText(f.x,f.y-f.r-44,"보통펀치!","#facc15");
        playSound("wind",1);
      }
    }
    function baldCapeContact(f,target){
      const b=f?.baldCape;if(!b||!b.normalActive||b.dash<=0||!target?.alive||!areEnemies(f,target))return false;
      const dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1;
      const dealt=damage(target,BALD_CAPE.normalDamage,f,"보통펀치");
      b.punchAnim={angle:Math.atan2(dy,dx),time:.18,serious:false};
      b.normalActive=false;b.dash=0;b.bounces=0;b.mode="";
      if(dealt>0&&target.alive){
        target.vx=dx/d*BALD_CAPE.wallKnockSpeed;target.vy=dy/d*BALD_CAPE.wallKnockSpeed;
        target.punchFlight=Math.max(target.punchFlight||0,BALD_CAPE.wallKnockDuration);
        target.punchSource=f;target.punchWallPower=BALD_CAPE.wallDamage;target.punchWallHits=0;
      }
      triggerHitStop(.14);screenShake=Math.max(screenShake,.32);
      spawnHitFlash(target.x,target.y,"#fef08a",70);spawnBlast(target.x,target.y,62,"#facc15");
      spawnFloatingText(target.x,target.y-target.r-34,"보통펀치!","#fde047");playSound("explosion",.75);
      baldCapeRestoreCruise(f);return true;
    }
    function fireBaldCapeComboTick(f){
      const b=f.baldCape,cmb=b?.combo;if(!cmb||cmb.hitsLeft<=0)return;
      baldCapeConeTargets(f,cmb.angle,BALD_CAPE.comboRange,BALD_CAPE.comboHalfAngle).forEach(e=>{
        damage(e,BALD_CAPE.comboDamage,f,"연속 보통펀치");spawnHitFlash(e.x,e.y,"#fef9c3",22);
      });
      cmb.hitsLeft--;b.punchAnim={angle:cmb.angle+rand(-.08,.08),time:.09,serious:false};playSound("hit",.35);
      if(cmb.hitsLeft<=0){b.combo=null;b.mode="";}
    }
    function fireBaldCapeSerious(f){
      const b=f.baldCape,s=b?.serious;if(!s)return;
      const victims=baldCapeConeTargets(f,s.angle,arena.size*1.65,BALD_CAPE.seriousHalfAngle);
      victims.forEach(e=>{damage(e,BALD_CAPE.seriousDamage,f,"진심펀치");spawnHitFlash(e.x,e.y,"#ef4444",100);});
      b.punchAnim={angle:s.angle,time:.22,serious:true};s.firedFlash=.28;
      triggerHitStop(.22);screenShake=Math.max(screenShake,.65);spawnParticles(f.x,f.y,"#fca5a5",30);playSound("explosion",1.4);
      spawnFloatingText(f.x,f.y-f.r-46,"진심펀치!","#ef4444");
      log("<strong>대머리망토</strong> 진심펀치 · "+victims.length+"명 적중","스킬");
      f.vx=s.savedVx;f.vy=s.savedVy;if(Math.hypot(f.vx,f.vy)<1)baldCapeRestoreCruise(f);
    }
    function updateBaldCape(f,dt){
      const b=f?.baldCape;if(!b)return;
      b.cd=Math.max(0,b.cd-dt);
      if(b.punchAnim){b.punchAnim.time=Math.max(0,b.punchAnim.time-dt);if(b.punchAnim.time<=0)b.punchAnim=null;}
      if(b.normalActive&&b.dash>0){
        b.dash=Math.max(0,b.dash-dt);
        if(b.dash<=0){b.normalActive=false;b.bounces=0;b.mode="";baldCapeRestoreCruise(f);}
      }
      if(b.combo){
        b.combo.life=Math.max(0,b.combo.life-dt);b.combo.tick-=dt;
        while(b.combo&&b.combo.tick<=0&&b.combo.hitsLeft>0){fireBaldCapeComboTick(f);if(b.combo)b.combo.tick+=BALD_CAPE.comboInterval;}
        if(b.combo&&b.combo.life<=0){b.combo=null;b.mode="";}
      }
      if(b.serious){
        if(b.serious.timer>0){
          f.vx=0;f.vy=0;b.serious.timer=Math.max(0,b.serious.timer-dt);
          if(b.serious.timer<=0)fireBaldCapeSerious(f);
        }else{
          b.serious.firedFlash=Math.max(0,b.serious.firedFlash-dt);
          if(b.serious.firedFlash<=0){b.serious=null;b.mode="";}
        }
      }
      if(b.cd<=0&&!b.normalActive&&!b.combo&&!b.serious&&!baldCapeBlocked(f))startBaldCapeSkill(f);
    }
    function drawBaldCapeCone(f,angle,range,halfAngle,fill,stroke,alpha){
      if(alpha===undefined)alpha=1;
      ctx.save();ctx.beginPath();ctx.rect(arena.x,arena.y,arena.size,arena.size);ctx.clip();
      ctx.globalAlpha=alpha;ctx.translate(f.x,f.y);ctx.rotate(angle);
      ctx.beginPath();ctx.moveTo(0,0);ctx.arc(0,0,range,-halfAngle,halfAngle);ctx.closePath();
      ctx.fillStyle=fill;ctx.fill();ctx.strokeStyle=stroke;ctx.lineWidth=2;ctx.stroke();ctx.restore();
    }
    function drawBaldCapeCharacter(f){
      const b=f.baldCape;
      if(!f.portraitOnly&&b?.serious){
        drawBaldCapeCone(f,b.serious.angle,arena.size*1.65,BALD_CAPE.seriousHalfAngle,"rgba(127,29,29,.62)","#ef4444",b.serious.timer>0?.22:.34);
        if(b.serious.timer>0){ctx.save();ctx.fillStyle="#fecaca";ctx.font="900 11px system-ui";ctx.textAlign="center";ctx.fillText("진심펀치 "+b.serious.timer.toFixed(1),f.x,f.y-f.r-42);ctx.restore();}
      }
      if(!f.portraitOnly&&b?.combo)drawBaldCapeCone(f,b.combo.angle,BALD_CAPE.comboRange,BALD_CAPE.comboHalfAngle,"rgba(250,204,21,.18)","#fde047",.75);
      if(!f.portraitOnly&&b?.normalActive){
        const glow=1+(b.bounces||0)*.13;drawRing(f.x,f.y,(f.r+9)*glow,b.dash>0?"rgba(254,240,138,.95)":"rgba(250,204,21,.62)",b.dash>0?4:2);
      }
      ctx.save();ctx.translate(f.x,f.y);ctx.scale(f.r/20,f.r/20);
      ctx.fillStyle="#f8fafc";ctx.beginPath();ctx.moveTo(-8,-2);ctx.lineTo(-24,5);ctx.lineTo(-18,28);ctx.lineTo(-7,20);ctx.closePath();ctx.fill();
      ctx.fillStyle="#facc15";ctx.strokeStyle="#a16207";ctx.lineWidth=1.2;ctx.beginPath();ctx.ellipse(0,9,12,17,0,0,Math.PI*2);ctx.fill();ctx.stroke();
      ctx.fillStyle="#dc2626";ctx.fillRect(-12,13,6,13);ctx.fillRect(6,13,6,13);ctx.beginPath();ctx.arc(-12,4,5,0,Math.PI*2);ctx.arc(12,4,5,0,Math.PI*2);ctx.fill();
      ctx.fillStyle="#f1c7a5";ctx.strokeStyle="#7c4a32";ctx.beginPath();ctx.arc(0,-9,10,0,Math.PI*2);ctx.fill();ctx.stroke();
      ctx.fillStyle="#111827";ctx.beginPath();ctx.arc(-3,-10,1,0,Math.PI*2);ctx.arc(3,-10,1,0,Math.PI*2);ctx.fill();
      ctx.strokeStyle="#92400e";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(-2,-5);ctx.lineTo(2,-5);ctx.stroke();ctx.restore();
      if(b?.punchAnim){
        const q=b.punchAnim,reach=q.serious?42:34;ctx.save();ctx.translate(f.x,f.y);ctx.rotate(q.angle);
        ctx.strokeStyle=q.serious?"#dc2626":"#eab308";ctx.lineWidth=q.serious?11:8;ctx.lineCap="round";ctx.beginPath();ctx.moveTo(f.r*.35,0);ctx.lineTo(reach,0);ctx.stroke();
        ctx.fillStyle=q.serious?"#ef4444":"#dc2626";ctx.beginPath();ctx.arc(reach+6,0,q.serious?9:7,0,Math.PI*2);ctx.fill();ctx.restore();
      }
      drawHealthBar(f);drawName(f);
    }

'''
)

rep(
'''      if (c.id === "andrum") initAndrum(fighter);
      if (c.id === "riddle_lord") initRiddle(fighter);''',
'''      if (c.id === "andrum") initAndrum(fighter);
      if (c.id === "bald_cape") initBaldCape(fighter);
      if (c.id === "riddle_lord") initRiddle(fighter);'''
)

rep(
'''      if (updateIronPunch(f, dt)) return;

      updateIron(f, dt);''',
'''      if (updateIronPunch(f, dt)) return;

      updateBaldCape(f, dt);
      if (!f.alive) return;
      updateIron(f, dt);'''
)

rep(
'''          || (f.toriMeteorWalk || 0) > 0 || (f.rioStormRush || 0) > 0
          || f.baseId === "wind_rio") return;''',
'''          || (f.toriMeteorWalk || 0) > 0 || (f.rioStormRush || 0) > 0
          || f.baldCape?.normalActive || f.baldCape?.serious?.timer > 0
          || f.baseId === "wind_rio") return;'''
)

rep(
'''        f.wallBounces += 1;

        if (electricWall) {''',
'''        f.wallBounces += 1;
        baldCapeWallBounce(f);

        if (electricWall) {'''
)

rep(
'''              captainContact(a, b);
              captainContact(b, a);
              hulkContact(a, b);''',
'''              captainContact(a, b);
              captainContact(b, a);
              baldCapeContact(a, b);
              baldCapeContact(b, a);
              hulkContact(a, b);'''
)

rep(
'''      if (f.andrum) { drawAndrumCharacter(f); return; }
      if (f.riddle) { drawRiddleCharacter(f); return; }''',
'''      if (f.andrum) { drawAndrumCharacter(f); return; }
      if (f.baldCape) { drawBaldCapeCharacter(f); return; }
      if (f.riddle) { drawRiddleCharacter(f); return; }'''
)

rep(
'''    function skillProgressInfo(f) {
      if(f.andrum){''',
r'''    function skillProgressInfo(f) {
      if(f.baldCape){const b=f.baldCape;
        const active=b.serious?"진심펀치 예고":b.combo?"연속 보통펀치":b.normalActive?(b.dash>0?"보통펀치 돌진":"보통펀치 가속 "+b.bounces+"/"+BALD_CAPE.normalBounces):"다음 펀치";
        return {ratio:clamp(1-b.cd/BALD_CAPE.period,0,1),className:b.serious?"rage-fill":"skill-fill",text:active+" · "+b.cd.toFixed(1)+"초",
          extraTextHtml:'<div class="status-skill-label">보통45% · 연속35% · 진심20% / 보통펀치 벽 반사마다 ×1.20 가속</div>'};}
      if(f.andrum){'''
)

rep(
'''      if (c.id === "hinta") return {damage:"속공 12 / 괴짜 속공 24 · 각 50% 확률 / 대쉬 충돌 10",''',
'''      if (c.id === "bald_cape") return {damage:"보통펀치12 + 맞은 상대 벽충돌8 / 연속 보통펀치2×6 / 진심펀치30",tick:"5.2초마다 무작위: 보통45% · 연속35% · 진심20% / 진심 선딜1.3초",tip:"보통펀치는 활성화 뒤 벽에 튕길 때마다 현재 속도가 20%씩 증가한다. 5번째 반사 직후 가장 가까운 적에게 고속 돌진하며, 명중한 적은 강하게 날아가 벽에 닿을 때마다 추가 피해8을 받는다. 연속 보통펀치는 거리108·약86도 원뿔을 0.12초 간격 6타로 공격한다. 진심펀치는 무작위 방향으로 맵 끝까지 이어지는 약22도 붉은 부채꼴을 1.3초간 표시한 뒤 범위 안 적에게 피해30을 준다."};
      if (c.id === "hinta") return {damage:"속공 12 / 괴짜 속공 24 · 각 50% 확률 / 대쉬 충돌 10",'''
)

rep(
'''        if (c.id === "andrum") initAndrum(preview);
        if (c.id === "hinta") preview.hinta = { pose: 0 };''',
'''        if (c.id === "andrum") initAndrum(preview);
        if (c.id === "bald_cape") initBaldCape(preview);
        if (c.id === "hinta") preview.hinta = { pose: 0 };'''
)

rep(
'''      const patchNotes = [
      "v96: 쟈바미/오벨리스크 시각 요소 재정리.''',
'''      const patchNotes = [
      "v97: 애니 캐릭터 '대머리망토' 추가. 체력170·이속2.7·5.2초마다 보통펀치45%/연속 보통펀치35%/진심펀치20% 중 하나를 사용. 보통펀치는 활성화 후 벽 반사마다 현재 속도×1.20으로 누적 가속하고 5번째 반사 직후 최근접 적에게 고속 돌진, 직격12 후 강펀치 넉백을 주며 날아간 상대가 벽에 닿을 때마다 추가8 피해. 연속 보통펀치는 거리108·약86도 원뿔을 0.12초 간격으로 2×6 다단히트. 진심펀치는 무작위 방향으로 맵 끝까지 이어지는 약22도 붉은 부채꼴을 1.3초 예고한 뒤 피해30 충격파를 발사. 캐릭터 그림은 노란 슈트·흰 망토·붉은 장갑/부츠·대머리 형태로 간단하게 구현.",
      "v96: 쟈바미/오벨리스크 시각 요소 재정리.'''
)

p.write_text(t,encoding="utf-8")
