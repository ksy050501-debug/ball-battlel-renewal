from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

def rep(old, new, count=1):
    global text
    found = text.count(old)
    if found != count:
        raise SystemExit(f'expected {count} occurrences, found {found}: {old[:120]!r}')
    text = text.replace(old, new, count)

rep('<title>볼배틀 리뉴얼 v67</title>', '<title>볼배틀 리뉴얼 v68</title>')

rep(
'''      horcruxSegments: 7, horcruxDuration: 7, horcruxContactCooldown: .75,
      weakHp: 90, weakSpeed: 2.5, weakFiendRadiusPenalty: 15, weakDamageMultiplier: .8''',
'''      horcruxSegments: 7, horcruxDuration: 7, horcruxContactCooldown: .75, horcruxRevivePenalty: 10,
      weakHp: 70, weakSpeed: 2.5, weakFiendRadiusPenalty: 15, weakDamageMultiplier: .8'''
)

rep(
'''        horcruxUsed: false, horcruxActive: false, horcruxSegments: 0, horcruxTimer: 0, horcruxX: 0, horcruxY: 0,
        horcruxContacts: new Map(), weakened: false''',
'''        horcruxUsed: false, horcruxActive: false, horcruxSegments: 0, horcruxTimer: 0, horcruxReviveHp: 0, horcruxX: 0, horcruxY: 0,
        horcruxContacts: new Map(), weakened: false'''
)

rep(
'''      r.horcruxSegments = RIDDLE.horcruxSegments;
      r.horcruxTimer = RIDDLE.horcruxDuration;''',
'''      r.horcruxSegments = RIDDLE.horcruxSegments;
      r.horcruxTimer = RIDDLE.horcruxDuration;
      r.horcruxReviveHp = RIDDLE.weakHp;'''
)

rep(
'''      const raw = Math.max(0, Math.round(amount || 0));
      const loss = 1 + Math.floor(raw / 10);
      r.horcruxSegments = Math.max(0, r.horcruxSegments - loss);
      spawnFloatingText(target.x, target.y - target.r - 30, `호크룩스 -${loss}`, "#cbd5e1");''',
'''      const raw = Math.max(0, Math.round(amount || 0));
      const loss = 1 + Math.floor(raw / 10);
      if (raw > 0) r.horcruxReviveHp = Math.max(0, r.horcruxReviveHp - RIDDLE.horcruxRevivePenalty);
      r.horcruxSegments = Math.max(0, r.horcruxSegments - loss);
      spawnFloatingText(target.x, target.y - target.r - 30, `호크룩스 -${loss} · 부활HP ${r.horcruxReviveHp}`, "#cbd5e1");'''
)

rep(
'''      r.horcruxContacts.set(source.id, battleTime);
      r.horcruxSegments = Math.max(0, r.horcruxSegments - 1);
      spawnFloatingText(target.x, target.y - target.r - 30, "접촉 · 호크룩스 -1", "#cbd5e1");''',
'''      r.horcruxContacts.set(source.id, battleTime);
      r.horcruxReviveHp = Math.max(0, r.horcruxReviveHp - RIDDLE.horcruxRevivePenalty);
      r.horcruxSegments = Math.max(0, r.horcruxSegments - 1);
      spawnFloatingText(target.x, target.y - target.r - 30, `접촉 · 호크룩스 -1 · 부활HP ${r.horcruxReviveHp}`, "#cbd5e1");'''
)

rep(
'''      r.horcruxSegments = 0;
      r.horcruxTimer = 0;
      f.maxHp = RIDDLE.weakHp;
      f.hp = RIDDLE.weakHp;
      f.baseSpeed = RIDDLE.weakSpeed;''',
'''      r.horcruxSegments = 0;
      r.horcruxTimer = 0;
      const reviveHp = Math.max(1, Math.min(RIDDLE.weakHp, r.horcruxReviveHp || RIDDLE.weakHp));
      f.maxHp = RIDDLE.weakHp;
      f.hp = reviveHp;
      r.wand = null;
      r.elderBuff = 0;
      r.wandTimer = RIDDLE.wandSpawn;
      f.baseSpeed = RIDDLE.weakSpeed;'''
)

rep(
'''      spawnFloatingText(f.x, f.y - f.r - 46, "약화된 리들 경 부활", "#e5e7eb");
      playSound("magic", 1.1);
      log(`<strong>${escapeHtml(f.name)}</strong> 호크룩스 생존 · 체력 ${RIDDLE.weakHp}의 약화 상태로 부활`, "부활");''',
'''      spawnFloatingText(f.x, f.y - f.r - 46, `약화된 리들 경 부활 · HP ${f.hp}`, "#e5e7eb");
      playSound("magic", 1.1);
      log(`<strong>${escapeHtml(f.name)}</strong> 호크룩스 생존 · HP ${f.hp}/${RIDDLE.weakHp} 약화 상태로 부활 · 딱총나무 지팡이 사용 불가`, "부활");'''
)

rep(
'''    function collectRiddleWand(f) {
      const r = f.riddle;
      if (!r.wand) return;''',
'''    function collectRiddleWand(f) {
      const r = f.riddle;
      if (!r.wand || r.weakened) return;'''
)

rep(
'''      if (r.wand) {
        r.wand.life = Math.max(0, r.wand.life - dt);
        if (r.wand.life <= 0) { r.wand = null; r.wandTimer = RIDDLE.wandSpawn; }
        else if (Math.hypot(f.x - r.wand.x, f.y - r.wand.y) <= f.r + 14) collectRiddleWand(f);
      } else {
        r.wandTimer = Math.max(0, r.wandTimer - dt);
        if (r.wandTimer <= 0) spawnRiddleWand(f);
      }
''',
'''      if (r.weakened) {
        r.wand = null;
        r.elderBuff = 0;
      } else if (r.wand) {
        r.wand.life = Math.max(0, r.wand.life - dt);
        if (r.wand.life <= 0) { r.wand = null; r.wandTimer = RIDDLE.wandSpawn; }
        else if (Math.hypot(f.x - r.wand.x, f.y - r.wand.y) <= f.r + 14) collectRiddleWand(f);
      } else {
        r.wandTimer = Math.max(0, r.wandTimer - dt);
        if (r.wandTimer <= 0) spawnRiddleWand(f);
      }
'''
)

rep(
'''condition: "피엔드피레/아바다 공유 쿨8초 · 번갈아 시전 · 딱총나무 지팡이16초 · 사망 시 호크룩스 1회", desc: "피엔드피레와 아바다를 공유 쿨8초로 번갈아 사용한다. 딱총나무 지팡이를 획득하면 불꽃 범위와 화상이 강화되고 아바다 케다브라가 거리 무관 확정타가 된다. 첫 사망 시 7칸 호크룩스로 7초를 버티면 약화 상태로 부활한다."''',
'''condition: "피엔드피레/아바다 공유 쿨8초 · 번갈아 시전 · 딱총나무 지팡이16초 · 사망 시 호크룩스 1회", desc: "피엔드피레와 아바다를 공유 쿨8초로 번갈아 사용한다. 딱총나무 지팡이를 획득하면 불꽃 범위와 화상이 강화되고 아바다 케다브라가 거리 무관 확정타가 된다. 첫 사망 시 7칸 호크룩스로 7초를 버티면 약화 상태로 부활하며, 대기 중 피격·충돌마다 부활 HP가 10씩 감소한다. 약화 부활 후에는 딱총나무 지팡이를 얻을 수 없다."'''
)

rep(
'''if (c.id === "riddle_lord") return {damage:"피엔드피레 0.4초마다3 + 화상2×3초 / 딱총나무 강화 0.4초마다4 + 화상3×3초 · 아바다 케다브라 5×5 / 강화 6×5",tick:"공유 쿨8초 · 피엔드피레↔아바다 번갈아 시전 · 피엔드피레4초 지속 · 아바다0.9초 다단 · 딱총나무16초마다 등장·8초 유지·획득 시12초 강화",tip:"딱총나무 강화 중 피엔드피레 반경75→105, 아바다 케다브라는 거리와 조준을 무시하고 지정 대상에게 확정 적중한다. 첫 사망 때 호크룩스 7칸/7초 상태가 되며 이동·공격 불가. 적 접촉마다 1칸, 공격 피격마다 기본1칸＋피해10당 1칸 추가 감소. 생존하면 HP90·이속2.5로 부활하며 피엔드피레 반경-15, 아바다 피해20% 감소. 두 번째 부활은 없다."};''',
'''if (c.id === "riddle_lord") return {damage:"피엔드피레 0.4초마다3 + 화상2×3초 / 딱총나무 강화 0.4초마다4 + 화상3×3초 · 아바다 케다브라 5×5 / 강화 6×5",tick:"공유 쿨8초 · 피엔드피레↔아바다 번갈아 시전 · 피엔드피레4초 지속 · 아바다0.9초 다단 · 딱총나무16초마다 등장·8초 유지·획득 시12초 강화",tip:"딱총나무 강화 중 피엔드피레 반경75→105, 아바다 케다브라는 거리와 조준을 무시하고 지정 대상에게 확정 적중한다. 첫 사망 때 호크룩스 7칸/7초 상태가 되며 이동·공격 불가. 적 접촉마다 1칸, 공격 피격마다 기본1칸＋피해10당 1칸 추가 감소하며, 피격 또는 접촉 1회마다 부활 HP도 70에서 10씩 감소한다. 생존하면 최대HP70·이속2.5의 약화형으로 현재 부활HP만큼 부활하고 딱총나무 지팡이는 더 이상 획득할 수 없다. 피엔드피레 반경-15, 아바다 피해20% 감소. 두 번째 부활은 없다."};'''
)

old_status = '''      if(f.riddle){const r=f.riddle;if(r.horcruxActive)return {ratio:clamp(r.horcruxSegments/RIDDLE.horcruxSegments,0,1),className:"rage-fill",text:`호크룩스 ${r.horcruxSegments}/${RIDDLE.horcruxSegments} · 부활 ${r.horcruxTimer.toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">접촉 -1 · 공격 피격 -1＋피해10당 추가 -1</div>'};const next=r.nextSpell==="fiend"?"피엔드피레":"아바다";return {ratio:r.elderBuff>0?clamp(r.elderBuff/RIDDLE.elderDuration,0,1):clamp(1-r.wandTimer/RIDDLE.wandSpawn,0,1),className:"skill-fill",text:r.elderBuff>0?`딱총나무 강화 ${r.elderBuff.toFixed(1)}초`:r.wand?`딱총나무 지팡이 · 남은 ${r.wand.life.toFixed(1)}초`:`딱총나무 등장 ${r.wandTimer.toFixed(1)}초`,extraTextHtml:`<div class="status-skill-label">${r.weakened?"약화 부활 · ":""}다음 ${next} ${r.spellCd.toFixed(1)}초 · 공유 쿨8초</div>`};}'''
new_status = '''      if(f.riddle){const r=f.riddle;if(r.horcruxActive)return {ratio:clamp(r.horcruxSegments/RIDDLE.horcruxSegments,0,1),className:"rage-fill",text:`호크룩스 ${r.horcruxSegments}/${RIDDLE.horcruxSegments} · 부활 ${r.horcruxTimer.toFixed(1)}초 · 부활HP ${r.horcruxReviveHp}/${RIDDLE.weakHp}`,extraTextHtml:'<div class="status-skill-label">접촉/피격마다 부활HP -10 · 호크룩스 칸 감소 규칙 유지</div>'};const next=r.nextSpell==="fiend"?"피엔드피레":"아바다";if(r.weakened)return {ratio:clamp(1-r.spellCd/RIDDLE.spellCooldown,0,1),className:"skill-fill",text:`약화 리들 경 · 다음 ${next} ${r.spellCd.toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">딱총나무 지팡이 획득 불가 · 최대HP70</div>'};return {ratio:r.elderBuff>0?clamp(r.elderBuff/RIDDLE.elderDuration,0,1):clamp(1-r.wandTimer/RIDDLE.wandSpawn,0,1),className:"skill-fill",text:r.elderBuff>0?`딱총나무 강화 ${r.elderBuff.toFixed(1)}초`:r.wand?`딱총나무 지팡이 · 남은 ${r.wand.life.toFixed(1)}초`:`딱총나무 등장 ${r.wandTimer.toFixed(1)}초`,extraTextHtml:`<div class="status-skill-label">다음 ${next} ${r.spellCd.toFixed(1)}초 · 공유 쿨8초</div>`};}'''
rep(old_status, new_status)

rep(
'''    const patchNotes = [
      "v67: 리들 경 1차 대규모 너프.''',
'''    const patchNotes = [
      "v68: 리들 경 호크룩스 추가 너프. 약화 부활 최대HP90→70. 호크룩스 대기 중 적의 공격 피격 또는 접촉 1회마다 예정 부활HP가 10씩 감소하며, 기존 호크룩스 칸 감소 규칙도 함께 적용. 약화 부활 후에는 딱총나무 지팡이가 더 이상 생성·획득되지 않음.",
      "v67: 리들 경 1차 대규모 너프.'''
)

path.write_text(text, encoding='utf-8')
print('patched v68')
