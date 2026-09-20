from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:180]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v81</title>','<title>볼배틀 리뉴얼 v82</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v81</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v82</h1>')

rep(
'''        skillName:"입체기동 · 회전베기", condition:"7초마다 벽 2곳에 와이어 · 기동 적중 시 즉시 재와이어", desc:"0.45초 준비 후 1초간 초당650으로 고속이동. 접촉하면 원형 회전베기와 출혈을 가하며, 와이어 기동 중 접촉은 별도의 강습 연출과 더 강한 16 피해를 준다. 출혈 중인 상대를 다시 베면 남은 출혈 피해를 즉시 터뜨린 뒤 출혈을 새로 건다. 기동 공격에 성공하면 즉시 다음 와이어 준비를 시작한다. 상대의 현재 HP가 자신보다 높을 때 차이 10당 피해 +3%, 최대 +60%." },''',
'''        skillName:"입체기동 · 회전베기", condition:"7초마다 벽 2곳에 와이어 · 근접 범위 자동 광역베기 · 기동 적중 시 즉시 재와이어", desc:"0.45초 준비 후 1초간 초당650으로 고속이동. 몸이 직접 닿지 않아도 검 사거리 안에 적이 들어오면 회전베기가 발동하고, 한 명을 계기로 발동한 베기는 베기 원 안의 모든 적에게 광역 피해와 출혈을 준다. 와이어 기동 중에는 강습16 피해가 적용된다. 출혈 중인 상대를 다시 베면 남은 출혈 피해를 즉시 터뜨린 뒤 출혈을 새로 건다. 기동 공격에 성공하면 즉시 다음 와이어 준비를 시작한다. 상대의 현재 HP가 자신보다 높을 때 차이 10당 피해 +3%, 최대 +60%." },'''
)

rep(
'''    const NEWHELLO = { period:7, windup:.45, dashDuration:1, dashSpeed:650,
      contactCooldown:1.2, spinDuration:.45, radiusBonus:28, normalDamage:8,
      dashDamage:16, bleedDamage:2, bleedTicks:3, gapForCap:200, maxBonus:.6 };''',
'''    const NEWHELLO = { period:7, windup:.45, dashDuration:1, dashSpeed:650,
      contactCooldown:1.2, spinDuration:.45, triggerBonus:18, radiusBonus:28, normalDamage:8,
      dashDamage:16, bleedDamage:2, bleedTicks:3, gapForCap:200, maxBonus:.6 };'''
)

anchor='''    function newhelloContact(f,e) {
'''
insert='''    function newhelloInTriggerRange(f,e) {
      return !!(f?.alive && e?.alive && areEnemies(f,e) &&
        Math.hypot(e.x-f.x,e.y-f.y) <= f.r + NEWHELLO.triggerBonus + e.r);
    }

    function newhelloProximityAttack(f) {
      const n=f?.newhello;
      if(!n || newhelloBlocked(f) || n.windup>0 || n.contactCd>0 || n.dash>0)return false;
      const target=enemiesOf(f).find(e=>newhelloInTriggerRange(f,e));
      return target ? newhelloContact(f,target) : false;
    }

    function newhelloContact(f,e) {
'''
rep(anchor,insert)

rep(
'''        // 고속 이동 경로도 작은 간격으로 접촉 판정하여 적을 관통해 놓치지 않는다.
        for(const e of enemiesOf(f)){
          if(Math.hypot(e.x-f.x,e.y-f.y)<=f.r+e.r){
            newhelloContact(f,e);
            if(n.dash<=0)break;
          }
        }''',
'''        // 고속 이동 중에는 몸이 닿기 전 검 사거리부터 베기를 판정한다.
        for(const e of enemiesOf(f)){
          if(newhelloInTriggerRange(f,e)){
            newhelloContact(f,e);
            if(n.dash<=0)break;
          }
        }'''
)

rep(
'''      bounceWalls(f);
      // 기본 작은 탄환 공격 제거: 피해는 스킬에서만 발생한다.
      checkSkill(f, dt);''',
'''      bounceWalls(f);
      // 뉴헬로는 몸 충돌보다 넓은 검 사거리 안에 적이 들어오면 일반 광역베기를 발동한다.
      if(f.newhello)newhelloProximityAttack(f);
      // 기본 작은 탄환 공격 제거: 피해는 스킬에서만 발생한다.
      checkSkill(f, dt);'''
)

rep(
'''      if(c.id==="newhello_sergeant")return {damage:"일반 회전베기8 / 와이어 강습16 + 출혈2×3회 · 재타격 시 남은 출혈 즉시 폭발 후 재적용 · HP 열세 보정 최대 ×1.6",
        tick:"기동7초 · 준비0.45초 · 고속이동1초(초당650) · 기동 적중 시 즉시 다음 와이어 준비 · 일반 베기 재사용1.2초 · 출혈 약1초마다",
        tip:"현재 HP가 상대보다 낮을 때만 HP 차이10당 베기·출혈 피해 +3%(최대60%). 와이어 돌진 속도는 520→650. 병장이 건 출혈이 남아 있는 적을 다시 공격하면 그 출혈의 남은 틱 피해를 즉시 한 번에 입히고 기존 출혈을 제거한 뒤 새 3틱 출혈을 건다. 예를 들어 3틱이 모두 남아 있으면 현재 출혈 틱 피해×3을 즉시 추가로 받는다. 와이어 강습 성공 시 즉시 재와이어하며 접촉 교환타 보정은 유지된다."};''',
'''      if(c.id==="newhello_sergeant")return {damage:"일반 광역 회전베기8 / 와이어 광역 강습16 + 출혈2×3회 · 재타격 시 남은 출혈 즉시 폭발 후 재적용 · HP 열세 보정 최대 ×1.6",
        tick:"검 발동 사거리: 몸 충돌보다 +18 · 광역 베기 범위: 몸 반경보다 +28 · 기동7초 · 준비0.45초 · 고속이동1초(초당650) · 기동 적중 시 즉시 다음 와이어 준비 · 일반 베기 재사용1.2초",
        tip:"뉴헬로는 상대와 몸이 닿지 않아도 검 사거리(+18)에 들어오면 베기가 발동한다. 공격을 발동시킨 상대가 누구든, 그 순간 병장 중심의 더 큰 베기 원(+28) 안에 있는 모든 적이 같은 베기 피해와 출혈을 받는다. 따라서 캡틴·박사처럼 직접 충돌 시 반격하는 상대를 실제 몸 충돌 전에 벨 수 있다. 단 실제로 몸이 부딪히면 기존 접촉 반격은 정상 발동한다. 출혈 폭발·와이어 적중 즉시 재와이어·접촉 교환타 보정은 그대로 유지된다."};'''
)

rep(
'''        extraTextHtml:'<div class="status-skill-label">일반8 / 와이어16 + 출혈 · 적중 시 즉시 재와이어 · HP 열세 시 최대 +60%</div>'};}''',
'''        extraTextHtml:'<div class="status-skill-label">검 사거리 +18 · 광역범위 +28 · 일반8 / 와이어16 + 출혈 · 적중 시 즉시 재와이어</div>'};}'''
)

rep(
'''      const patchNotes = [
      "v81: 뉴헬로 병장 추격/출혈 버프.''',
'''      const patchNotes = [
      "v82: 뉴헬로 병장 비접촉 광역베기 추가. 몸 충돌 거리보다 +18 안에 적이 들어오면 접촉하지 않아도 베기가 발동하며, 발동 시 병장 중심 +28 베기 원 안의 모든 적에게 동일한 일반8/와이어16 피해·출혈을 광역 적용. 와이어 고속 이동 중에도 몸 충돌 전 검 사거리에서 판정한다. 실제 몸 충돌 시 상대의 기존 접촉 공격/반격은 그대로 발동. 출혈 폭발·속도650·적중 즉시 재와이어·HP 열세 보정은 유지.",
      "v81: 뉴헬로 병장 추격/출혈 버프.'''
)

p.write_text(t,encoding="utf-8")
