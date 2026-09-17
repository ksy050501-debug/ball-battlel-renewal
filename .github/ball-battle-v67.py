from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def rep(old, new, count=1):
    global text
    actual = text.count(old)
    if actual != count:
        raise SystemExit(f'expected {count} occurrence(s), found {actual}: {old[:100]!r}')
    text = text.replace(old, new, count)

rep('<title>볼배틀 리뉴얼 v66</title>', '<title>볼배틀 리뉴얼 v67</title>')

rep(
'''    const RIDDLE = {\n      fiendCooldown: 13, fiendDuration: 4, fiendRadius: 95, fiendDamage: 4, fiendTick: .4,\n      fiendBurn: 2, fiendBurnDuration: 3, elderFiendRadius: 130, elderFiendDamage: 5, elderFiendBurn: 3,\n      avadaCooldown: 8, avadaCast: .35, avadaDuration: .9, avadaRange: 260, avadaWidth: 18,''',
'''    const RIDDLE = {\n      spellCooldown: 8, fiendDuration: 4, fiendRadius: 75, fiendDamage: 3, fiendTick: .4,\n      fiendBurn: 2, fiendBurnDuration: 3, elderFiendRadius: 105, elderFiendDamage: 4, elderFiendBurn: 3,\n      avadaCast: .35, avadaDuration: .9, avadaRange: 260, avadaWidth: 18,'''
)

rep(
'''      f.riddle = {\n        fiendCd: 6.5, fiendActive: 0, fiendTick: 0,\n        avadaCd: 4, avadaCast: 0, avadaLife: 0, avadaTick: 0, avadaAngle: 0, avadaTargetId: null, avadaElder: false,''',
'''      f.riddle = {\n        spellCd: 4, nextSpell: "fiend", fiendActive: 0, fiendTick: 0,\n        avadaCast: 0, avadaLife: 0, avadaTick: 0, avadaAngle: 0, avadaTargetId: null, avadaElder: false,'''
)

rep('      r.fiendCd = RIDDLE.fiendCooldown;\n', '')
rep('      r.avadaCd = RIDDLE.avadaCooldown;\n', '')

rep(
'''      r.elderBuff = Math.max(0, r.elderBuff - dt);\n      r.fiendCd = Math.max(0, r.fiendCd - dt);\n      r.avadaCd = Math.max(0, r.avadaCd - dt);''',
'''      r.elderBuff = Math.max(0, r.elderBuff - dt);\n      r.spellCd = Math.max(0, r.spellCd - dt);'''
)

rep(
'''      if (r.fiendCd <= 0) startRiddleFiendfyre(f);\n      if (r.avadaCd <= 0 && r.avadaCast <= 0 && r.avadaLife <= 0) startRiddleAvada(f);''',
'''      if (r.spellCd <= 0 && r.avadaCast <= 0 && r.avadaLife <= 0) {\n        if (r.nextSpell === "fiend") {\n          startRiddleFiendfyre(f);\n          r.nextSpell = "avada";\n        } else {\n          startRiddleAvada(f);\n          r.nextSpell = "fiend";\n        }\n        r.spellCd = RIDDLE.spellCooldown;\n      }'''
)

rep(
'''      r.fiendCd = 4;\n      r.avadaCd = 2.5;''',
'''      r.spellCd = 4;'''
)

rep(
'''        skillName: "피엔드피레 · 아바다 케다브라 · 호크룩스", condition: "피엔드피레13초 · 아바다8초 · 딱총나무 지팡이16초 · 사망 시 호크룩스 1회", desc: "뱀 형태의 불꽃을 두르고 초록색 다단 광선을 발사한다. 딱총나무 지팡이를 획득하면 불꽃 범위와 화상이 강화되고 아바다 케다브라가 거리 무관 확정타가 된다. 첫 사망 시 7칸 호크룩스로 7초를 버티면 약화 상태로 부활한다." },''',
'''        skillName: "피엔드피레 · 아바다 케다브라 · 호크룩스", condition: "공유 쿨8초 · 피엔드피레↔아바다 번갈아 시전 · 딱총나무 지팡이16초 · 사망 시 호크룩스 1회", desc: "피엔드피레와 아바다 케다브라를 하나의 쿨타임으로 번갈아 사용한다. 딱총나무 지팡이를 획득하면 불꽃 범위와 화상이 강화되고 아바다 케다브라가 거리 무관 확정타가 된다. 첫 사망 시 7칸 호크룩스로 7초를 버티면 약화 상태로 부활한다." },'''
)

rep(
'''      if (c.id === "riddle_lord") return {damage:"피엔드피레 0.4초마다4 + 화상2×3초 / 딱총나무 강화 0.4초마다5 + 화상3×3초 · 아바다 케다브라 5×5 / 강화 6×5",tick:"피엔드피레13초·4초 지속 · 아바다8초·0.9초 다단 · 딱총나무16초마다 등장·8초 유지·획득 시12초 강화",tip:"딱총나무 강화 중 피엔드피레 반경95→130, 아바다 케다브라는 거리와 조준을 무시하고 지정 대상에게 확정 적중한다. 첫 사망 때 호크룩스 7칸/7초 상태가 되며 이동·공격 불가. 적 접촉마다 1칸, 공격 피격마다 기본1칸＋피해10당 1칸 추가 감소. 생존하면 HP90·이속2.5로 부활하며 피엔드피레 반경-15, 아바다 피해20% 감소. 두 번째 부활은 없다."};''',
'''      if (c.id === "riddle_lord") return {damage:"피엔드피레 0.4초마다3 + 화상2×3초 / 딱총나무 강화 0.4초마다4 + 화상3×3초 · 아바다 케다브라 5×5 / 강화 6×5",tick:"공유 쿨8초 · 첫 피엔드피레는 4초 뒤 · 이후 피엔드피레↔아바다 교대 · 피엔드피레4초 지속 · 아바다0.9초 다단 · 딱총나무16초마다 등장·8초 유지·획득 시12초 강화",tip:"딱총나무 강화 중 피엔드피레 반경75→105, 아바다 케다브라는 거리와 조준을 무시하고 지정 대상에게 확정 적중한다. 첫 사망 때 호크룩스 7칸/7초 상태가 되며 이동·공격 불가. 적 접촉마다 1칸, 공격 피격마다 기본1칸＋피해10당 1칸 추가 감소. 생존하면 HP90·이속2.5로 부활하며 피엔드피레 반경-15, 아바다 피해20% 감소. 두 번째 부활은 없다."};'''
)

rep(
'''      if(f.riddle){const r=f.riddle;if(r.horcruxActive)return {ratio:clamp(r.horcruxSegments/RIDDLE.horcruxSegments,0,1),className:"rage-fill",text:`호크룩스 ${r.horcruxSegments}/${RIDDLE.horcruxSegments} · 부활 ${r.horcruxTimer.toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">접촉 -1 · 공격 피격 -1＋피해10당 추가 -1</div>'};return {ratio:r.elderBuff>0?clamp(r.elderBuff/RIDDLE.elderDuration,0,1):clamp(1-r.wandTimer/RIDDLE.wandSpawn,0,1),className:"skill-fill",text:r.elderBuff>0?`딱총나무 강화 ${r.elderBuff.toFixed(1)}초`:r.wand?`딱총나무 지팡이 · 남은 ${r.wand.life.toFixed(1)}초`:`딱총나무 등장 ${r.wandTimer.toFixed(1)}초`,extraTextHtml:`<div class="status-skill-label">${r.weakened?"약화 부활 · ":""}피엔드피레 ${r.fiendCd.toFixed(1)}초 · 아바다 ${r.avadaCd.toFixed(1)}초</div>`};}''',
'''      if(f.riddle){const r=f.riddle;if(r.horcruxActive)return {ratio:clamp(r.horcruxSegments/RIDDLE.horcruxSegments,0,1),className:"rage-fill",text:`호크룩스 ${r.horcruxSegments}/${RIDDLE.horcruxSegments} · 부활 ${r.horcruxTimer.toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">접촉 -1 · 공격 피격 -1＋피해10당 추가 -1</div>'};const next=r.nextSpell==="fiend"?"피엔드피레":"아바다";return {ratio:r.elderBuff>0?clamp(r.elderBuff/RIDDLE.elderDuration,0,1):clamp(1-r.wandTimer/RIDDLE.wandSpawn,0,1),className:"skill-fill",text:r.elderBuff>0?`딱총나무 강화 ${r.elderBuff.toFixed(1)}초`:r.wand?`딱총나무 지팡이 · 남은 ${r.wand.life.toFixed(1)}초`:`딱총나무 등장 ${r.wandTimer.toFixed(1)}초`,extraTextHtml:`<div class="status-skill-label">${r.weakened?"약화 부활 · ":""}다음 ${next} ${r.spellCd.toFixed(1)}초 · 공유 쿨8초</div>`};}'''
)

rep(
'''    const patchNotes = [\n      "v66:''',
'''    const patchNotes = [\n      "v67: 리들 경 1차 대규모 너프. 피엔드피레와 아바다 케다브라가 공유 쿨8초를 사용하며 피엔드피레→아바다 순서로 번갈아 시전. 첫 피엔드피레는 4초 뒤 발동. 피엔드피레 반경95→75, 딱총나무 강화 반경130→105, 틱 피해4→3, 강화 틱 피해5→4. 화상·아바다·딱총나무·호크룩스 수치는 유지.",\n      "v66:'''
)

# Ensure the old independent cooldown state is gone from executable code/status.
for stale in ('r.fiendCd', 'r.avadaCd', 'RIDDLE.fiendCooldown', 'RIDDLE.avadaCooldown'):
    if stale in text:
        raise SystemExit(f'stale independent cooldown reference remains: {stale}')

path.write_text(text, encoding='utf-8')
print('v67 Riddle shared cooldown patch applied')
