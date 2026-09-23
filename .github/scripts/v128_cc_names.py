from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

assert '<title>볼배틀 리뉴얼 v127</title>' in s
assert '<h1 id="mainTitle">볼배틀 리뉴얼 v127</h1>' in s

replacements = [
    ('conanKnifeSlowMultiplier', 'knifeSlowMultiplier'),
    ('conanKnifeSlow', 'knifeSlow'),
    ('spiderWebSlowMultiplier', 'webSlowMultiplier'),
    ('spiderWebSlow', 'webSlow'),
    ('hintaConcussion', 'concussionSlow'),
    ('drawHintaConcussion', 'drawConcussionSlow'),
    ('spiderBind', 'bindStun'),
    ('elsaFreezeImmune', 'hardFreezeImmune'),
    ('elsaFreezeSourceId', 'hardFreezeSourceId'),
    ('elsaFreeze', 'hardFreeze'),
    ('elsaAuraSlowMultiplier', 'coldAuraSlowMultiplier'),
    ('oshiSongDebuffs', 'songDebuffs'),
    ('updateOshiSongDebuffs', 'updateSongDebuffs'),
    ('oshiSongSlowMultiplier', 'songSlowMultiplier'),
    ('applyOshiSongDebuff', 'applySongDebuff'),
    ('oshiReducedIncomingDamage', 'songDebuffReducedIncomingDamage'),
]

# Longest/specific identifiers first so shorter names cannot partially rewrite them.
for old, new in replacements:
    s = s.replace(old, new)

# Local CC-composition names should describe the effect, not the source character.
s = s.replace('const elsaIce = coldAuraSlowMultiplier(f);', 'const coldAuraSlow = coldAuraSlowMultiplier(f);')
s = s.replace('const oshiSlow = songSlowMultiplier(f) * (f.concussionSlow > 0 ? HINTA.slowMultiplier : 1);', 'const songAndConcussionSlow = songSlowMultiplier(f) * (f.concussionSlow > 0 ? HINTA.slowMultiplier : 1);')
s = s.replace('* oshiSlow * elsaIce *', '* songAndConcussionSlow * coldAuraSlow *')
s = s.replace('const conanSlow = knifeSlowMultiplier(f) * webSlowMultiplier(f);', 'const timedCcSlow = timedCcSlowMultiplier(f);')
s = s.replace('* conanSlow;', '* timedCcSlow;')

s = s.replace('<title>볼배틀 리뉴얼 v127</title>', '<title>볼배틀 리뉴얼 v128</title>', 1)
s = s.replace('<h1 id="mainTitle">볼배틀 리뉴얼 v127</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v128</h1>', 1)

marker = '      const patchNotes = [\n'
note = '      "v128: CC 내부 이름에서 캐릭터명을 제거했습니다. 고난 흉기 둔화·거미남 웹 둔화·힌타 뇌진탕·거미남 벽속박·엘팔아 완전빙결·최애 노래 디버프의 저장값/보조 함수명을 knifeSlow·webSlow·concussionSlow·bindStun·hardFreeze·songDebuffs 등 효과 기준 이름으로 전수 변경했습니다. 수치·지속시간·중첩·면역·피해·넉백·판정·연출은 변경하지 않은 순수 명칭 리팩터링입니다.",\n'
assert marker in s
s = s.replace(marker, marker + note, 1)

# Old character-named CC identifiers must be gone from live code.
for old, _ in replacements:
    assert old not in s, old

# Behavior-critical constants and labels must remain unchanged.
for needle in [
    'knifeSlow:.75, knifeSlowDuration:3.4',
    'webSlow:.78, webSlowTime:.9',
    'concussion: 2, slowMultiplier: .6',
    'bindTime:1.6',
    'freezeTime:5.5, freezeImmune:2.5',
    'debuffDuration: 3',
    'bluntStun:.55',
    'mindDuration: 1.5',
    'target.bindStun=Math.max(target.bindStun||0,SPIDER.bindTime)',
    'refreshCcTimer(target,"knifeSlow",CONAN.knifeSlowDuration)',
    'refreshCcTimer(e,"concussionSlow",HINTA.concussion)',
    'refreshCcTimer(hit,"webSlow",SPIDER.webSlowTime)',
]:
    assert needle in s, needle

# Stun refactor from v127 must remain fully migrated.
assert 'tanoStop' not in s
assert 'function applyStun(target, duration)' in s

p.write_text(s, encoding='utf-8')
