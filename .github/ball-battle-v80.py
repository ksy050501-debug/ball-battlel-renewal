from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:140]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v79</title>','<title>볼배틀 리뉴얼 v80</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v79</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v80</h1>')

rep(
'''        skillName:"입체기동 · 회전베기", condition:"7초마다 벽 2곳에 와이어 · 접촉 시 쌍검 회전", desc:"0.45초 준비 후 1초간 고속이동. 접촉하면 원형 회전베기와 출혈을 가하며, 고속 기동 중에는 피해와 연출이 강화된다. 상대의 현재 HP가 자신보다 높을 때 차이 10당 피해 +3%, 최대 +60%. 검과 망토는 피격 범위를 늘리지 않는다." },''',
'''        skillName:"입체기동 · 회전베기", condition:"7초마다 벽 2곳에 와이어 · 기동 적중 시 즉시 재와이어", desc:"0.45초 준비 후 1초간 고속이동. 접촉하면 원형 회전베기와 출혈을 가하며, 와이어 기동 중 접촉은 별도의 강습 연출과 더 강한 16 피해를 준다. 기동 공격에 성공하면 7초 쿨을 기다리지 않고 즉시 다음 와이어 준비를 시작한다. 상대의 현재 HP가 자신보다 높을 때 차이 10당 피해 +3%, 최대 +60%. 검과 망토는 피격 범위를 늘리지 않는다." },'''
)

old_contact='''    function newhelloContact(f,e) {
      const n=f.newhello;
      if(!n || !e.alive || !areEnemies(f,e) || newhelloBlocked(f) || n.windup>0)return;
      const fast=n.dash>0;
      if(fast ? n.hits.has(e.id) : n.contactCd>0)return;
      n.spin=NEWHELLO.spinDuration;n.spinFast=fast;n.contactCd=NEWHELLO.contactCooldown;
      const victims=enemiesOf(f).filter(t=>Math.hypot(t.x-f.x,t.y-f.y)<=f.r+NEWHELLO.radiusBonus+t.r);
      for(const t of victims){
        if(fast && n.hits.has(t.id))continue;
        if(fast)n.hits.add(t.id);
        const mult=newhelloMultiplier(f,t);
        const dealt=damage(t,(fast?NEWHELLO.dashDamage:NEWHELLO.normalDamage)*mult,f,fast?"입체기동 회전베기":"쌍검 회전베기");
        if(dealt>0 && t.alive)applyBleed(t,f,NEWHELLO.bleedDamage*mult,3,1,NEWHELLO.bleedTicks);
        spawnHitFlash(t.x,t.y,fast?"#67e8f9":"#e2e8f0",fast?38:23);
      }
      spawnBlast(f.x,f.y,f.r+NEWHELLO.radiusBonus,fast?"#22d3ee":"#cbd5e1");
      if(fast){spawnParticles(f.x,f.y,"#a5f3fc",14);screenShake=Math.max(screenShake,.35);}
      playSound("slash",fast?1:.65);
    }'''
new_contact='''    function newhelloContact(f,e) {
      const n=f.newhello;
      if(!n || !e.alive || !areEnemies(f,e) || newhelloBlocked(f) || n.windup>0)return false;
      const fast=n.dash>0;
      if(fast ? n.hits.has(e.id) : n.contactCd>0)return false;
      n.spin=NEWHELLO.spinDuration;n.spinFast=fast;n.contactCd=NEWHELLO.contactCooldown;
      let landed=false;
      const victims=enemiesOf(f).filter(t=>Math.hypot(t.x-f.x,t.y-f.y)<=f.r+NEWHELLO.radiusBonus+t.r);
      for(const t of victims){
        if(fast && n.hits.has(t.id))continue;
        if(fast)n.hits.add(t.id);
        const mult=newhelloMultiplier(f,t);
        const dealt=damage(t,(fast?NEWHELLO.dashDamage:NEWHELLO.normalDamage)*mult,f,fast?"입체기동 강습":"쌍검 회전베기");
        if(dealt>0){
          landed=true;
          if(t.alive)applyBleed(t,f,NEWHELLO.bleedDamage*mult,3,1,NEWHELLO.bleedTicks);
        }
        if(fast){
          const hitAngle=Math.atan2(t.y-f.y,t.x-f.x);
          spawnHitFlash(t.x,t.y,"#ecfeff",62);
          spawnBlast(t.x,t.y,68,"#0891b2");
          spawnSlash(t.x,t.y,hitAngle+Math.PI*.28,94,"#67e8f9");
          spawnSlash(t.x,t.y,hitAngle-Math.PI*.28,94,"#cffafe");
          spawnParticles(t.x,t.y,"#a5f3fc",24);
          spawnFloatingText(t.x,t.y-t.r-38,"와이어 강습!","#67e8f9");
        }else{
          spawnHitFlash(t.x,t.y,"#e2e8f0",23);
        }
      }
      if(fast){
        spawnBlast(f.x,f.y,f.r+NEWHELLO.radiusBonus+12,"#06b6d4");
        spawnParticles(f.x,f.y,"#ecfeff",18);
        triggerHitStop(.12);
        screenShake=Math.max(screenShake,.48);
        if(landed){
          n.mutualContactUntil=battleTime+.08;
          n.dash=0;
          n.anchors=[];
          n.cd=0;
          spawnFloatingText(f.x,f.y-f.r-48,"연속 와이어!","#cffafe");
        }
      }else{
        spawnBlast(f.x,f.y,f.r+NEWHELLO.radiusBonus,"#cbd5e1");
      }
      playSound("slash",fast?1.25:.65);
      return landed;
    }'''
rep(old_contact,new_contact)

rep(
'''      f.newhello={cd:NEWHELLO.period, windup:0, dash:0, spin:0, spinFast:false,
        contactCd:0, anchors:[], angle:0, hits:new Set(), trail:[]};''',
'''      f.newhello={cd:NEWHELLO.period, windup:0, dash:0, spin:0, spinFast:false,
        contactCd:0, anchors:[], angle:0, hits:new Set(), trail:[], mutualContactUntil:0};'''
)

rep(
'''        for(const e of enemiesOf(f)){
          if(Math.hypot(e.x-f.x,e.y-f.y)<=f.r+e.r)newhelloContact(f,e);
        }
        if(f.x-f.r<=arena.x || f.x+f.r>=arena.x2 || f.y-f.r<=arena.y || f.y+f.r>=arena.y2){''',
'''        for(const e of enemiesOf(f)){
          if(Math.hypot(e.x-f.x,e.y-f.y)<=f.r+e.r){
            newhelloContact(f,e);
            if(n.dash<=0)break;
          }
        }
        if(n.dash<=0)break;
        if(f.x-f.r<=arena.x || f.x+f.r>=arena.x2 || f.y-f.r<=arena.y || f.y+f.r>=arena.y2){'''
)

rep(
'''        f.captain.punch = { target, dx, dy, phase: "windup", timer: CAPTAIN.punchWindup };
        return;''',
'''        f.captain.punch = { target, dx, dy, phase: "windup", timer: CAPTAIN.punchWindup };
        // 와이어 강습과 같은 접촉 프레임이면 강펀치가 상대 선타에 의해 사라지지 않도록 교환타로 즉시 확정한다.
        if ((target.newhello?.mutualContactUntil || 0) >= battleTime) {
          f.captain.punch.timer = 0;
          updateCaptainPunch(f, 0);
        }
        return;'''
)

rep(
'''      f.iron.punch = { target, dx, dy, phase: "windup", timer: IRON.hulkWindup };
    }''',
'''      f.iron.punch = { target, dx, dy, phase: "windup", timer: IRON.hulkWindup };
      // 와이어 강습과 동시 접촉한 헐크버스터 강타도 선후 처리 때문에 씹히지 않게 즉시 교환타 처리.
      if ((target.newhello?.mutualContactUntil || 0) >= battleTime) {
        f.iron.punch.timer = 0;
        updateIronPunch(f, 0);
      }
    }'''
)

rep(
'''      if(c.id==="newhello_sergeant")return {damage:"일반 회전베기8 / 기동 회전베기16 + 출혈2×3회 · HP 열세 보정 최대 ×1.6",
        tick:"기동7초 · 준비0.45초 · 고속이동1초(초당520) · 일반 베기 재사용1.2초 · 출혈 약1초마다",
        tip:"현재 HP가 상대보다 낮을 때만 HP 차이10당 베기·출혈 피해 +3%(최대60%). 접촉으로 원형 베기 발동, 범위는 본체 반지름+28. 고속 기동 한 번당 같은 적에게 베기는 1회만 적중. 출혈은 같은 병장에게 재피격 시 갱신되며 별도 중첩되지 않는다. 와이어 발사 방향은 준비 시작 시 고정되며 자동 추적하지 않는다."};''',
'''      if(c.id==="newhello_sergeant")return {damage:"일반 회전베기8 / 와이어 강습16 + 출혈2×3회 · HP 열세 보정 최대 ×1.6",
        tick:"기동7초 · 준비0.45초 · 고속이동1초(초당520) · 기동 적중 시 즉시 다음 와이어 준비 · 일반 베기 재사용1.2초 · 출혈 약1초마다",
        tip:"현재 HP가 상대보다 낮을 때만 HP 차이10당 베기·출혈 피해 +3%(최대60%). 일반 접촉은 흰 회전베기, 와이어 돌진 접촉은 청록 십자 강습 이펙트와 피해16이 적용된다. 와이어 강습에 성공하면 현재 돌진을 끝내고 쿨타임을 즉시 0으로 만들어 다음 프레임부터 새 와이어 준비에 들어간다. 파워스톤·추진 부스터 같은 즉시 접촉 피해는 그대로 교환되고, 캡틴 강펀치·헐크버스터처럼 짧은 선딜이 있는 접촉 공격도 같은 와이어 충돌에서는 즉시 교환타로 확정된다. 출혈은 같은 병장에게 재피격 시 갱신되며 별도 중첩되지 않는다."};'''
)

rep(
'''        extraTextHtml:'<div class="status-skill-label">일반8 / 기동16 + 출혈 · HP 열세 시 최대 +60%</div>'};}''',
'''        extraTextHtml:'<div class="status-skill-label">일반8 / 와이어16 + 출혈 · 적중 시 즉시 재와이어 · HP 열세 시 최대 +60%</div>'};}'''
)

rep(
'''      const patchNotes = [
      "v79: 신규 애니 캐릭터 뉴헬로 병장 추가.''',
'''      const patchNotes = [
      "v80: 뉴헬로 병장 와이어 교전 패치. 일반 회전베기8/와이어 강습16 수치를 재확인하고, 와이어 적중은 청록 십자베기·대형 충격파·강한 히트스톱으로 일반 접촉과 연출을 완전히 분리. 와이어 돌진 중 공격 성공 시 현재 돌진을 끝내고 쿨을 즉시 0으로 만들어 다음 와이어를 바로 준비. 파워스톤·추진 부스터 등 즉시 접촉 피해의 교환을 유지하고, 캡틴 강펀치·헐크버스터처럼 선딜이 있는 접촉 공격도 같은 와이어 충돌에서는 즉시 교환타 처리해 선후 순서로 씹히지 않게 보정. 기존 다른 캐릭터 수치 유지.",
      "v79: 신규 애니 캐릭터 뉴헬로 병장 추가.'''
)

p.write_text(t,encoding="utf-8")
