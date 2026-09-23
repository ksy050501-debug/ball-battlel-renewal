from pathlib import Path
import re

p = Path('index.html')
t = p.read_text(encoding='utf-8')


def rep(old, new, label, count=1):
    global t
    actual = t.count(old)
    if actual < count:
        raise SystemExit(f'missing {label}: expected >= {count}, found {actual}')
    t = t.replace(old, new, count)

# Version only. No combat values are changed in this refactor.
rep('<title>볼배틀 리뉴얼 v125</title>', '<title>볼배틀 리뉴얼 v126</title>', 'title')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v125</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v126</h1>', 'header')

old_freeze = '''    function applyFreeze(target, duration) {
      if (!target || !target.alive || hasHarmfulImmunity(target)) return false;
      target.freeze = Math.max(target.freeze || 0, duration);
      return true;
    }
'''
new_freeze = '''    // v126 공용 CC 어댑터.
    // 주의: 밸런스 보존을 위해 기존 저장 필드와 중첩/면역 규칙은 그대로 둔다.
    // freeze는 역사적으로 "빙결"이라는 이름이지만 실제 효과는 이속 42%의 강둔화다.
    // tanoStop은 역사적 이름을 유지하되 공용 행동정지(stun/stop) API를 통해 사용한다.
    function applyHeavySlow(target, duration) {
      if (!target || !target.alive || hasHarmfulImmunity(target)) return false;
      target.freeze = Math.max(target.freeze || 0, duration);
      return true;
    }
    function applyFreeze(target, duration) { // 구형 캐릭터 호환용 별칭
      return applyHeavySlow(target, duration);
    }
    function applyStun(target, duration) {
      if (!target || !target.alive) return false;
      target.tanoStop = Math.max(target.tanoStop || 0, duration);
      return true;
    }
    function refreshCcTimer(target, stateKey, duration) {
      if (!target || !target.alive) return false;
      target[stateKey] = Math.max(target[stateKey] || 0, duration);
      return true;
    }
    function timedCcSlowMultiplier(target) {
      return conanKnifeSlowMultiplier(target) * spiderWebSlowMultiplier(target);
    }
'''
rep(old_freeze, new_freeze, 'common CC adapter block')

# Action stop: same tanoStop storage, now reached through a neutral API.
rep('e.tanoStop = Math.max(e.tanoStop || 0, TANO.mindDuration);', 'applyStun(e, TANO.mindDuration);', 'Tano mind stop')
rep('if(!hasHarmfulImmunity(target))target.tanoStop=Math.max(target.tanoStop||0,CONAN.bluntStun);', 'if(!hasHarmfulImmunity(target))applyStun(target,CONAN.bluntStun);', 'Conan blunt stun')
rep('if(f.spiderBind>0){f.tanoStop=Math.max(f.tanoStop||0,f.spiderBind);f.vx=0;f.vy=0;}', 'if(f.spiderBind>0){applyStun(f,f.spiderBind);f.vx=0;f.vy=0;}', 'Spider bind stop bridge')

# Timed slows: keep each legacy timer so durations, stacking, immunity and visuals are unchanged.
rep('target.conanKnifeSlow=Math.max(target.conanKnifeSlow||0,CONAN.knifeSlowDuration);', 'refreshCcTimer(target,"conanKnifeSlow",CONAN.knifeSlowDuration);', 'Conan knife slow timer')
rep('hit.spiderWebSlow=Math.max(hit.spiderWebSlow||0,SPIDER.webSlowTime);', 'refreshCcTimer(hit,"spiderWebSlow",SPIDER.webSlowTime);', 'Spider web slow timer')
rep('e.hintaConcussion=Math.max(e.hintaConcussion||0,HINTA.concussion);', 'refreshCcTimer(e,"hintaConcussion",HINTA.concussion);', 'Hinta concussion slow timer')

# Justice Ally's applyFreeze(2) is a heavy slow, not Elsa-style full freeze.
rep('applyFreeze(e,2);', 'applyHeavySlow(e,2);', 'Obelisk heavy slow')

# Neutralize character-specific local naming without changing the multiplier itself.
rep('const conanSlow = conanKnifeSlowMultiplier(f) * spiderWebSlowMultiplier(f);', 'const timedCcSlow = timedCcSlowMultiplier(f);', 'effective speed CC name')
rep('* oshiSlow * elsaIce * conanSlow;', '* oshiSlow * elsaIce * timedCcSlow;', 'effective speed CC multiplier')
rep('*conanKnifeSlowMultiplier(f)*spiderWebSlowMultiplier(f);', '*timedCcSlowMultiplier(f);', 'Hinta dash CC multiplier')

# Patch note.
needle = '''      const patchNotes = [\n      "v125:'''
insert = '''      const patchNotes = [\n      "v126: CC 내부 구조를 성능 변화 없이 정리했습니다. 공용 행동정지 applyStun, 강둔화 applyHeavySlow, 시간형 CC 타이머 refreshCcTimer를 추가하고 타노 마인드·고난 둔기·거미남 벽속박·고난 흉기·거미남 웹·힌타 뇌진탕·오벨리스크 강둔화 호출을 공용 명칭으로 연결했습니다. 기존 tanoStop·freeze·캐릭터별 타이머 저장값과 지속시간·중첩·면역·넉백·피해·연출은 그대로 유지해 전투 성능은 변경하지 않았습니다.",\n      "v125:'''
rep(needle, insert, 'v126 patch note')

p.write_text(t, encoding='utf-8')

# Build JS check file.
scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', t)
Path('/tmp/index_js_check.js').write_text('\n'.join(scripts), encoding='utf-8')

# Behavior-preservation sanity checks for all edited mechanics.
checks = [
    'mindDuration: 1.5',
    'knifeSlow:.75, knifeSlowDuration:3.4',
    'bluntStun:.55, bluntKnock:240',
    'webKnock:105, webSlow:.78, webSlowTime:.9',
    'bindTime:1.6',
    'concussion: 2, slowMultiplier: .6',
    'auraDamage:6, auraTick:1.0, auraSlow:.85',
    'freezeTime:5.5, freezeImmune:2.5',
]
for s in checks:
    if s not in t:
        raise SystemExit('behavior constant unexpectedly missing: ' + s)
