from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:160]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v80</title>','<title>볼배틀 리뉴얼 v81</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v80</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v81</h1>')

rep(
'''        skillName:"입체기동 · 회전베기", condition:"7초마다 벽 2곳에 와이어 · 기동 적중 시 즉시 재와이어", desc:"0.45초 준비 후 1초간 고속이동. 접촉하면 원형 회전베기와 출혈을 가하며, 와이어 기동 중 접촉은 별도의 강습 연출과 더 강한 16 피해를 준다. 기동 공격에 성공하면 7초 쿨을 기다리지 않고 즉시 다음 와이어 준비를 시작한다. 상대의 현재 HP가 자신보다 높을 때 차이 10당 피해 +3%, 최대 +60%. 검과 망토는 피격 범위를 늘리지 않는다." },''',
'''        skillName:"입체기동 · 회전베기", condition:"7초마다 벽 2곳에 와이어 · 기동 적중 시 즉시 재와이어", desc:"0.45초 준비 후 1초간 초당650으로 고속이동. 접촉하면 원형 회전베기와 출혈을 가하며, 와이어 기동 중 접촉은 별도의 강습 연출과 더 강한 16 피해를 준다. 출혈 중인 상대를 다시 베면 남은 출혈 피해를 즉시 터뜨린 뒤 출혈을 새로 건다. 기동 공격에 성공하면 즉시 다음 와이어 준비를 시작한다. 상대의 현재 HP가 자신보다 높을 때 차이 10당 피해 +3%, 최대 +60%." },'''
)

rep(
'''    const NEWHELLO = { period:7, windup:.45, dashDuration:1, dashSpeed:520,
      contactCooldown:1.2, spinDuration:.45, radiusBonus:28, normalDamage:8,
      dashDamage:16, bleedDamage:2, bleedTicks:3, gapForCap:200, maxBonus:.6 };''',
'''    const NEWHELLO = { period:7, windup:.45, dashDuration:1, dashSpeed:650,
      contactCooldown:1.2, spinDuration:.45, radiusBonus:28, normalDamage:8,
      dashDamage:16, bleedDamage:2, bleedTicks:3, gapForCap:200, maxBonus:.6 };'''
)

anchor='''    function newhelloContact(f,e) {
'''
insert='''    function detonateNewhelloBleed(source,target) {
      if(!target?.alive || !source?.alive || !target.bleedingTicks?.length)return 0;
      const idx=target.bleedingTicks.findIndex(b=>b.source===source);
      if(idx<0)return 0;
      const bleed=target.bleedingTicks[idx];
      const remainingTicks=typeof bleed.ticksLeft==="number"
        ? Math.max(0,bleed.ticksLeft)
        : Math.max(0,Math.ceil((bleed.t||0)/(bleed.tick||1)));
      const burst=Math.max(0,(bleed.power||0)*remainingTicks);
      target.bleedingTicks.splice(idx,1);
      if(burst<=0)return 0;
      const dealt=bodyDirectDamage(target,burst,source,"출혈 폭발","#ef4444");
      spawnBlast(target.x,target.y,44,"#7f1d1d");
      spawnParticles(target.x,target.y,"#fecaca",14);
      spawnFloatingText(target.x,target.y-target.r-52,`출혈 폭발 -${Math.round(burst)}`,"#fca5a5");
      playSound("slash",.85);
      return dealt;
    }

    function newhelloContact(f,e) {
'''
rep(anchor,insert)

rep(
'''        const dealt=damage(t,(fast?NEWHELLO.dashDamage:NEWHELLO.normalDamage)*mult,f,fast?"입체기동 강습":"쌍검 회전베기");
        if(dealt>0){
          landed=true;
          if(t.alive)applyBleed(t,f,NEWHELLO.bleedDamage*mult,3,1,NEWHELLO.bleedTicks);
        }''',
'''        const dealt=damage(t,(fast?NEWHELLO.dashDamage:NEWHELLO.normalDamage)*mult,f,fast?"입체기동 강습":"쌍검 회전베기");
        if(dealt>0){
          landed=true;
          if(t.alive)detonateNewhelloBleed(f,t);
          if(t.alive)applyBleed(t,f,NEWHELLO.bleedDamage*mult,3,1,NEWHELLO.bleedTicks);
        }'''
)

rep(
'''      if(c.id==="newhello_sergeant")return {damage:"일반 회전베기8 / 와이어 강습16 + 출혈2×3회 · HP 열세 보정 최대 ×1.6",
        tick:"기동7초 · 준비0.45초 · 고속이동1초(초당520) · 기동 적중 시 즉시 다음 와이어 준비 · 일반 베기 재사용1.2초 · 출혈 약1초마다",
        tip:"현재 HP가 상대보다 낮을 때만 HP 차이10당 베기·출혈 피해 +3%(최대60%). 일반 접촉은 흰 회전베기, 와이어 돌진 접촉은 청록 십자 강습 이펙트와 피해16이 적용된다. 와이어 강습에 성공하면 현재 돌진을 끝내고 쿨타임을 즉시 0으로 만들어 다음 프레임부터 새 와이어 준비에 들어간다. 파워스톤·추진 부스터 같은 즉시 접촉 피해는 그대로 교환되고, 캡틴 강펀치·헐크버스터처럼 짧은 선딜이 있는 접촉 공격도 같은 와이어 충돌에서는 즉시 교환타로 확정된다. 출혈은 같은 병장에게 재피격 시 갱신되며 별도 중첩되지 않는다."};''',
'''      if(c.id==="newhello_sergeant")return {damage:"일반 회전베기8 / 와이어 강습16 + 출혈2×3회 · 재타격 시 남은 출혈 즉시 폭발 후 재적용 · HP 열세 보정 최대 ×1.6",
        tick:"기동7초 · 준비0.45초 · 고속이동1초(초당650) · 기동 적중 시 즉시 다음 와이어 준비 · 일반 베기 재사용1.2초 · 출혈 약1초마다",
        tip:"현재 HP가 상대보다 낮을 때만 HP 차이10당 베기·출혈 피해 +3%(최대60%). 와이어 돌진 속도는 520→650. 병장이 건 출혈이 남아 있는 적을 다시 공격하면 그 출혈의 남은 틱 피해를 즉시 한 번에 입히고 기존 출혈을 제거한 뒤 새 3틱 출혈을 건다. 예를 들어 3틱이 모두 남아 있으면 현재 출혈 틱 피해×3을 즉시 추가로 받는다. 와이어 강습 성공 시 즉시 재와이어하며 접촉 교환타 보정은 유지된다."};'''
)

rep(
'''      "v80: 뉴헬로 병장 와이어 교전 패치.''',
'''      "v81: 뉴헬로 병장 추격/출혈 버프. 와이어 돌진 속도520→650. 병장이 건 출혈이 남은 상대를 다시 공격하면 남아 있는 출혈 틱 피해를 한 번에 즉시 입히고 기존 출혈을 제거한 뒤 새 3틱 출혈을 재적용. 일반8·와이어16·HP 열세 보정·적중 즉시 재와이어·접촉 교환타 규칙은 유지.",
      "v80: 뉴헬로 병장 와이어 교전 패치.'''
)

p.write_text(t,encoding="utf-8")
