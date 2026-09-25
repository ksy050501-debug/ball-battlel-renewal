from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

def once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 marker, found {n}')
    s = s.replace(old, new, 1)

def count_replace(old, new, count, label):
    global s
    n = s.count(old)
    if n != count:
        raise SystemExit(f'{label}: expected {count} markers, found {n}')
    s = s.replace(old, new)

# Version labels.
once('<title>볼배틀 리뉴얼 v144</title>', '<title>볼배틀 리뉴얼 v145</title>', 'tab version')
once('<h1 id="mainTitle">볼배틀 리뉴얼 v144</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v145</h1>', 'visible version')

# Patch note.
anchor = '      const patchNotes = [\n'
if anchor not in s:
    raise SystemExit('patch notes anchor missing')
s = s.replace(anchor, anchor + '      "v145: 팀전 각 팀 내부 출전순서 섞기 버튼 추가. 소환수가 준 피해와 처치를 소환 주인의 전투분석 피해/처치에 즉시 귀속하며, 소환수가 받은 피해는 공격자의 피해에만 반영되고 주인의 피격에는 합산하지 않음. 캐릭터 최종 사망 시 냉기·사신·빚기회·손패 등 잔여 상태표시를 정리하고, 체력바 주변 냉기/사신/빚기회/카드 수를 겹치지 않는 배지형 UI로 재배치. 전투 수치와 판정은 변경 없음.",\n', 1)

# Team-order shuffle button.
once('''      <div class="button-row">\n        <button class="ghost" id="clearSelectionBtn">선택 해제</button>\n        <button class="danger" id="selectAllBtn">전원 참가</button>\n      </div>''', '''      <div class="button-row">\n        <button class="ghost" id="clearSelectionBtn">선택 해제</button>\n        <button class="ghost" id="shuffleTeamBtn" style="display:none;">팀 순서 섞기</button>\n        <button class="danger" id="selectAllBtn">전원 참가</button>\n      </div>''', 'team shuffle button')

once('''      $("selectAllBtn").textContent = battleMode === "team" ? "자동 편성" : "전원 참가";\n    }\n\n    function renderSelectedList() {''', '''      $("selectAllBtn").textContent = battleMode === "team" ? "자동 편성" : "전원 참가";\n      const shuffleTeamBtn = $("shuffleTeamBtn");\n      if (shuffleTeamBtn) shuffleTeamBtn.style.display = battleMode === "team" ? "" : "none";\n    }\n\n    function shuffleTeamArray(arr) {\n      for (let i = arr.length - 1; i > 0; i--) {\n        const j = Math.floor(Math.random() * (i + 1));\n        [arr[i], arr[j]] = [arr[j], arr[i]];\n      }\n    }\n\n    function shuffleTeamOrders() {\n      if (battleMode !== "team") return;\n      shuffleTeamArray(teamA);\n      shuffleTeamArray(teamB);\n      renderSelectedList();\n      showOverlay("팀 순서 섞기", "A팀과 B팀의 내부 출전 순서를 각각 섞었습니다.");\n    }\n\n    function renderSelectedList() {''', 'team shuffle function')

once('''    $("selectAllBtn").addEventListener("click", () => {''', '''    $("shuffleTeamBtn").addEventListener("click", shuffleTeamOrders);\n    $("selectAllBtn").addEventListener("click", () => {''', 'team shuffle listener')

# Generic combat-stat owner for summons. Gameplay source remains the summon; only stats roll up.
once('''    function damage(target, amount, source, reason = "공격") {''', '''    function combatStatOwner(source) {\n      if (!source) return null;\n      if (source.isSummon && source.ownerId) {\n        const owner = fighterById(source.ownerId);\n        if (owner && !owner.isSummon) return owner;\n      }\n      return source;\n    }\n\n    function creditCombatDamage(source, amount) {\n      const credit = combatStatOwner(source);\n      if (!credit || !(amount > 0)) return;\n      credit.damageDealt = (credit.damageDealt || 0) + amount;\n    }\n\n    function creditCombatKill(source) {\n      const credit = combatStatOwner(source);\n      if (!credit) return;\n      credit.kills = (credit.kills || 0) + 1;\n    }\n\n    function damage(target, amount, source, reason = "공격") {''', 'combat stat helpers')

# Damage roll-up paths.
once('''        source.damageDealt = (source.damageDealt || 0) + value;\n        source.hitsDealt += 1; source.hitsDealtSkill += 1;''', '''        creditCombatDamage(source, value);\n        source.hitsDealt += 1; source.hitsDealtSkill += 1;''', 'jabami damage credit')
once('''      if (source && source !== f) { source.damageDealt = (source.damageDealt || 0) + absorbed; source.hitsDealt++; source.hitsDealtSkill++; }''', '''      if (source && source !== f) { creditCombatDamage(source, absorbed); source.hitsDealt++; source.hitsDealtSkill++; }''', 'iron absorbed damage credit')
count_replace('''      if (source && source.alive && source !== target) source.damageDealt = (source.damageDealt || 0) + actualDamage;''', '''      if (source && source.alive && source !== target) creditCombatDamage(source, actualDamage);''', 1, 'normal damage credit')
count_replace('''      if (source && source.alive && source !== target) source.damageDealt = (source.damageDealt || 0) + actualBodyDamage;''', '''      if (source && source.alive && source !== target) creditCombatDamage(source, actualBodyDamage);''', 1, 'body damage credit')

# Kills roll up to summon owner while logs still name the actual source.
count_replace('''if (source && source.alive && source !== target) source.kills = (source.kills || 0) + 1;''', '''if (source && source.alive && source !== target) creditCombatKill(source);''', 2, 'dummy kill credit')
count_replace('''      if (source && source.alive && !target.isSummon) {\n          source.kills += 1;''', '''      if (source && source.alive && !target.isSummon) {\n          creditCombatKill(source);''', 2, 'normal kill credit')
once('''      if (source && source.alive && !target.isSummon) {\n        source.kills = (source.kills || 0) + 1;''', '''      if (source && source.alive && !target.isSummon) {\n        creditCombatKill(source);''', 'horcrux kill credit')

# Battle analysis reads the already-attributed owner totals, preventing lost/dead-summon stats or double counting.
old_analysis = '''      const rows = fighters\n        .filter(f => !f.isSummon)\n        .sort((a, b) => {\n          const sa=a.baseId==="justice_ally"?justiceSummonBattleStats(a):{damage:0,kills:0};\n          const sb=b.baseId==="justice_ally"?justiceSummonBattleStats(b):{damage:0,kills:0};\n          return ((b.damageDealt||0)+sb.damage)-((a.damageDealt||0)+sa.damage);\n        });\n\n      const combined=new Map(rows.map(f=>{\n        const summon=f.baseId==="justice_ally"?justiceSummonBattleStats(f):{damage:0,kills:0};\n        return [f.id,{\n          damage:(f.damageDealt||0)+summon.damage,\n          kills:(f.kills||0)+summon.kills\n        }];\n      }));'''
new_analysis = '''      const rows = fighters\n        .filter(f => !f.isSummon)\n        .sort((a, b) => (b.damageDealt || 0) - (a.damageDealt || 0));\n\n      const combined = new Map(rows.map(f => [f.id, {\n        damage: f.damageDealt || 0,\n        kills: f.kills || 0\n      }]));'''
once(old_analysis, new_analysis, 'battle analysis rollup')

# Clear visual stack/state residue on final death. This runs centrally for every actual death effect.
once('''    function clearDefeatedFighterArtifacts(target) {''', '''    function clearDefeatedFighterStatusStacks(target) {\n      if (!target) return;\n      target.elsaCold = 0;\n      target.hardFreeze = 0;\n      target.hardFreezeImmune = 0;\n      if (target.jabami) {\n        target.jabami.debt = 0;\n        target.jabami.debtChances = 0;\n      }\n      if (target.duelist && Array.isArray(target.duelist.hand)) target.duelist.hand.length = 0;\n      for (const source of fighters) {\n        if (source?.elsa?.targets instanceof Map) source.elsa.targets.delete(target.id);\n        if (source?.conan?.targets instanceof Map) source.conan.targets.delete(target.id);\n        if (Array.isArray(source?.conan?.assaults)) source.conan.assaults = source.conan.assaults.filter(a => a.targetId !== target.id);\n      }\n    }\n\n    function clearDefeatedFighterArtifacts(target) {''', 'death stack cleanup helper')
once('''    function triggerDeathEffect(target) {\n      clearDefeatedFighterArtifacts(target);''', '''    function triggerDeathEffect(target) {\n      clearDefeatedFighterStatusStacks(target);\n      clearDefeatedFighterArtifacts(target);''', 'death stack cleanup call')

# Compact, non-overlapping stack badges above the health bar.
once('''    function drawHealthBar(f) {\n      if (suppressMarioSpinUi) return;\n      if (f.portraitOnly) return;''', '''    function drawHealthStackBadges(f, barY) {\n      if (!f?.alive) return;\n      const badges = [];\n      const cold = Math.max(0, Math.min(ELSA.coldMax, Math.floor(f.elsaCold || 0)));\n      if (cold > 0) badges.push({ text: `❄ ${cold}/${ELSA.coldMax}`, fill: "rgba(14,116,144,.88)", stroke: "#bae6fd", color: "#f0f9ff" });\n      const conanMeter = conanMeterForTarget(f);\n      if (conanMeter > 0) badges.push({ text: `☠ ${Math.floor(conanMeter)}/${CONAN.maxMeter}`, fill: "rgba(127,29,29,.9)", stroke: "#fca5a5", color: "#fee2e2" });\n      if (f.jabami) {\n        const debt = Math.max(0, Math.ceil(f.jabami.debt || 0));\n        const chances = Math.max(0, Math.floor(f.jabami.debtChances || 0));\n        if (debt > 0) badges.push({ text: `빚 ${debt}`, fill: "rgba(127,29,29,.9)", stroke: "#f87171", color: "#fee2e2" });\n        if (chances > 0) badges.push({ text: `◆ 빚기회 ${chances}`, fill: "rgba(69,10,10,.9)", stroke: "#fecaca", color: "#fecaca" });\n      }\n      if (f.duelist?.equipped && Array.isArray(f.duelist.hand) && f.duelist.hand.length > 0) {\n        badges.push({ text: `카드 ${f.duelist.hand.length}`, fill: "rgba(30,58,138,.9)", stroke: "#bfdbfe", color: "#eff6ff" });\n      }\n      if (!badges.length) return;\n\n      const perRow = 2, gap = 4, rowH = 14;\n      const rows = Math.ceil(badges.length / perRow);\n      ctx.save();\n      ctx.font = "800 9px system-ui";\n      ctx.textAlign = "center";\n      ctx.textBaseline = "middle";\n      for (let row = 0; row < rows; row++) {\n        const items = badges.slice(row * perRow, row * perRow + perRow);\n        const widths = items.map(b => Math.ceil(ctx.measureText(b.text).width) + 10);\n        const totalW = widths.reduce((sum, v) => sum + v, 0) + gap * Math.max(0, items.length - 1);\n        let px = f.x - totalW / 2;\n        const py = barY - 8 - (rows - 1 - row) * rowH;\n        items.forEach((b, i) => {\n          const bw = widths[i], bh = 11;\n          ctx.fillStyle = b.fill;\n          ctx.strokeStyle = b.stroke;\n          ctx.lineWidth = 1;\n          roundRect(ctx, px, py - bh / 2, bw, bh, 5, true, true);\n          ctx.fillStyle = b.color;\n          ctx.fillText(b.text, px + bw / 2, py + .5);\n          px += bw + gap;\n        });\n      }\n      ctx.restore();\n    }\n\n    function drawHealthBar(f) {\n      if (suppressMarioSpinUi) return;\n      if (f.portraitOnly) return;\n      if (!f.alive) return;''', 'health badge helper')

old_status_blocks = '''      if ((f.elsaCold || 0) > 0) {\n        ctx.save();ctx.font="900 10px system-ui";ctx.textAlign="left";ctx.textBaseline="middle";\n        ctx.fillStyle="#bae6fd";ctx.strokeStyle="rgba(2,6,23,.85)";ctx.lineWidth=3;\n        const snow="❄".repeat(Math.min(ELSA.coldMax,f.elsaCold||0));\n        ctx.strokeText(snow,x,y+h+10);ctx.fillText(snow,x,y+h+10);ctx.restore();\n      }\n\n      const conanMeter=conanMeterForTarget(f);\n      if(conanMeter>0){\n        ctx.save();ctx.font="900 10px system-ui";ctx.textAlign="right";ctx.textBaseline="middle";\n        ctx.strokeStyle="rgba(2,6,23,.9)";ctx.lineWidth=3;ctx.fillStyle="#f87171";\n        const label="☠ "+Math.floor(conanMeter)+"/"+CONAN.maxMeter;\n        ctx.strokeText(label,x+w,y+h+10);ctx.fillText(label,x+w,y+h+10);ctx.restore();\n      }\n\n      if (f.jabami?.debt > 0) {\n        ctx.font="900 12px system-ui";ctx.textAlign="center";ctx.textBaseline="alphabetic";ctx.lineWidth=4;ctx.strokeStyle="rgba(0,0,0,.78)";ctx.fillStyle="#f87171";\n        ctx.strokeText(`빚 ${Math.ceil(f.jabami.debt)}`,x+w/2,y-8);ctx.fillText(`빚 ${Math.ceil(f.jabami.debt)}`,x+w/2,y-8);\n      }\n'''
once(old_status_blocks, '', 'old overlapping status blocks')

old_diamonds = '''      if (f.jabami) {\n        const chances=Math.max(0,Math.floor(f.jabami.debtChances||0));\n        if(chances>0){\n          const size=5,gap=5;\n          const start=x+size/2;\n          const dy=y+h+8;\n          ctx.save();\n          for(let i=0;i<chances;i++){\n            ctx.save();\n            ctx.translate(start+i*(size+gap),dy);\n            ctx.rotate(Math.PI/4);\n            ctx.fillStyle="#ef4444";\n            ctx.strokeStyle="#fecaca";\n            ctx.lineWidth=.8;\n            ctx.fillRect(-size/2,-size/2,size,size);\n            ctx.strokeRect(-size/2,-size/2,size,size);\n            ctx.restore();\n          }\n          ctx.restore();\n        }\n      }\n\n'''
once(old_diamonds, '      drawHealthStackBadges(f, y);\n\n', 'jabami diamonds to badges')

p.write_text(s, encoding='utf-8')
print('v145 patch applied')
