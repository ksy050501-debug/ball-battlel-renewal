from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:180]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v82</title>','<title>볼배틀 리뉴얼 v83</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v82</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v83</h1>')

rep(
'''        skillName:"입체기동 · 회전베기", condition:"7초마다 벽 2곳에 와이어 · 근접 범위 자동 광역베기 · 기동 적중 시 즉시 재와이어", desc:"0.45초 준비 후 1초간 초당650으로 고속이동. 몸이 직접 닿지 않아도 검 사거리 안에 적이 들어오면 회전베기가 발동하고, 한 명을 계기로 발동한 베기는 베기 원 안의 모든 적에게 광역 피해와 출혈을 준다. 와이어 기동 중에는 강습16 피해가 적용된다. 출혈 중인 상대를 다시 베면 남은 출혈 피해를 즉시 터뜨린 뒤 출혈을 새로 건다. 기동 공격에 성공하면 즉시 다음 와이어 준비를 시작한다. 상대의 현재 HP가 자신보다 높을 때 차이 10당 피해 +3%, 최대 +60%." },''',
'''        skillName:"입체기동 · 회전베기", condition:"7초마다 벽 2곳에 와이어 · 근접 범위 자동 광역베기 · 기동 적중 시 즉시 재와이어", desc:"0.45초 준비 후 1초간 초당650으로 고속이동. 몸이 직접 닿지 않아도 몸 충돌 거리보다 8만큼 넓은 검 사거리 안에 적이 들어오면 회전베기가 발동하고, 한 명을 계기로 발동한 베기는 베기 원 안의 모든 적에게 광역 피해와 출혈을 준다. 와이어 기동 중에는 강습16 피해가 적용된다. 출혈은 1피해씩 5회이며, 출혈 중인 상대를 다시 베면 남은 출혈 피해를 즉시 터뜨린 뒤 새 출혈을 건다. 기동 공격에 성공하면 즉시 다음 와이어 준비를 시작한다." },'''
)

rep(
'''    const NEWHELLO = { period:7, windup:.45, dashDuration:1, dashSpeed:650,
      contactCooldown:1.2, spinDuration:.45, triggerBonus:18, radiusBonus:28, normalDamage:8,
      dashDamage:16, bleedDamage:2, bleedTicks:3, gapForCap:200, maxBonus:.6 };''',
'''    const NEWHELLO = { period:7, windup:.45, dashDuration:1, dashSpeed:650,
      contactCooldown:1.2, spinDuration:.45, triggerBonus:8, radiusBonus:28, normalDamage:8,
      dashDamage:16, bleedDamage:1, bleedTicks:5, bleedDuration:5, gapForCap:200, maxBonus:.6 };'''
)

rep(
'''          if(t.alive)applyBleed(t,f,NEWHELLO.bleedDamage*mult,3,1,NEWHELLO.bleedTicks);''',
'''          if(t.alive)applyBleed(t,f,NEWHELLO.bleedDamage*mult,NEWHELLO.bleedDuration,1,NEWHELLO.bleedTicks);'''
)

rep(
'''      if(c.id==="newhello_sergeant")return {damage:"일반 광역 회전베기8 / 와이어 광역 강습16 + 출혈2×3회 · 재타격 시 남은 출혈 즉시 폭발 후 재적용 · HP 열세 보정 최대 ×1.6",
        tick:"검 발동 사거리: 몸 충돌보다 +18 · 광역 베기 범위: 몸 반경보다 +28 · 기동7초 · 준비0.45초 · 고속이동1초(초당650) · 기동 적중 시 즉시 다음 와이어 준비 · 일반 베기 재사용1.2초",
        tip:"뉴헬로는 상대와 몸이 닿지 않아도 검 사거리(+18)에 들어오면 베기가 발동한다. 공격을 발동시킨 상대가 누구든, 그 순간 병장 중심의 더 큰 베기 원(+28) 안에 있는 모든 적이 같은 베기 피해와 출혈을 받는다. 따라서 캡틴·박사처럼 직접 충돌 시 반격하는 상대를 실제 몸 충돌 전에 벨 수 있다. 단 실제로 몸이 부딪히면 기존 접촉 반격은 정상 발동한다. 출혈 폭발·와이어 적중 즉시 재와이어·접촉 교환타 보정은 그대로 유지된다."};''',
'''      if(c.id==="newhello_sergeant")return {damage:"일반 광역 회전베기8 / 와이어 광역 강습16 + 출혈1×5회 · 재타격 시 남은 출혈 즉시 폭발 후 재적용 · HP 열세 보정 최대 ×1.6",
        tick:"검 발동 사거리: 몸 충돌보다 +8 · 광역 베기 범위: 몸 반경보다 +28 · 기동7초 · 준비0.45초 · 고속이동1초(초당650) · 기동 적중 시 즉시 다음 와이어 준비 · 일반 베기 재사용1.2초 · 출혈 약1초마다 5회",
        tip:"뉴헬로는 상대와 몸이 닿지 않아도 검 사거리(+8)에 들어오면 베기가 발동한다. 공격을 발동시킨 상대가 누구든, 그 순간 병장 중심의 더 큰 베기 원(+28) 안에 있는 모든 적이 같은 베기 피해와 출혈을 받는다. 출혈은 1씩 5회이며, 병장이 건 출혈이 남아 있는 적을 다시 베면 남은 출혈 틱 피해를 즉시 한 번에 터뜨리고 새 5틱 출혈을 건다. 실제 몸 충돌 시 상대의 기존 접촉 반격은 정상 발동한다."};'''
)

rep(
'''        extraTextHtml:'<div class="status-skill-label">검 사거리 +18 · 광역범위 +28 · 일반8 / 와이어16 + 출혈 · 적중 시 즉시 재와이어</div>'};}''',
'''        extraTextHtml:'<div class="status-skill-label">검 사거리 +8 · 광역범위 +28 · 일반8 / 와이어16 + 출혈1×5 · 적중 시 즉시 재와이어</div>'};}'''
)

rep(
'''      const patchNotes = [
      "v82: 뉴헬로 병장 비접촉 광역베기 추가.''',
'''      const patchNotes = [
      "v83: 뉴헬로 병장 비접촉 광역베기 조정. 검 발동 사거리를 몸 충돌보다 +18→+8로 축소. 광역 베기 범위 +28, 일반8/와이어16, 와이어 속도650, 적중 즉시 재와이어는 유지. 출혈은 2×3회에서 1×5회로 변경하고 지속시간을 5초로 맞춤. 출혈 중 재타격 시 남은 틱 피해 즉시 폭발 후 새 5틱 출혈 재적용 규칙 유지.",
      "v82: 뉴헬로 병장 비접촉 광역베기 추가.'''
)

p.write_text(t,encoding="utf-8")
