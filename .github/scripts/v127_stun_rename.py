from pathlib import Path

p = Path('index.html')
html = p.read_text(encoding='utf-8')

assert '<title>볼배틀 리뉴얼 v126</title>' in html
assert '<h1 id="mainTitle">볼배틀 리뉴얼 v126</h1>' in html

# v126 이전 코드에는 공용 stun 저장 프로퍼티가 아직 없어야 안전하게 전체 이름만 바꿀 수 있다.
preexisting_stun_props = html.count('.stun')
assert preexisting_stun_props == 0, f'pre-existing .stun refs: {preexisting_stun_props}'

old_refs = html.count('tanoStop')
assert old_refs >= 8, f'unexpected tanoStop ref count: {old_refs}'

# 실제 전투 로직/상태 저장 키를 동일한 의미의 공용 이름으로 일괄 변경한다.
html = html.replace('tanoStop', 'stun')

# 과거 v126 패치노트는 당시 저장명이 tanoStop이었다는 기록이므로 원문을 보존한다.
html = html.replace(
    '기존 stun·freeze·캐릭터별 타이머 저장값과 지속시간·중첩·면역·넉백·피해·연출은 그대로 유지해 전투 성능은 변경하지 않았습니다.',
    '기존 tanoStop·freeze·캐릭터별 타이머 저장값과 지속시간·중첩·면역·넉백·피해·연출은 그대로 유지해 전투 성능은 변경하지 않았습니다.'
)

html = html.replace('<title>볼배틀 리뉴얼 v126</title>', '<title>볼배틀 리뉴얼 v127</title>', 1)
html = html.replace('<h1 id="mainTitle">볼배틀 리뉴얼 v126</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v127</h1>', 1)

note = '      "v127: 공용 행동정지의 내부 저장명까지 정리했습니다. 기존 tanoStop 프로퍼티를 stun으로 전수 이름 변경하고 applyStun 및 모든 행동정지 판정·감소·차단 참조를 같은 stun 저장값으로 통일했습니다. 숫자·지속시간·적용 조건·면역·피해·넉백·연출은 변경하지 않은 순수 명칭 리팩터링입니다.",\n'
needle = '      const patchNotes = [\n'
assert needle in html
html = html.replace(needle, needle + note, 1)

# v126 역사 기록 1곳을 제외하면 실제 코드에 tanoStop이 남아 있으면 안 된다.
without_v126_history = html.replace('기존 tanoStop·freeze·캐릭터별 타이머 저장값', '기존 OLD_STOP_NAME·freeze·캐릭터별 타이머 저장값')
assert 'tanoStop' not in without_v126_history
assert 'target.stun = Math.max(target.stun || 0, duration);' in html
assert 'f.stun = Math.max(0, (f.stun || 0) - dt);' in html
assert '<title>볼배틀 리뉴얼 v127</title>' in html
assert '<h1 id="mainTitle">볼배틀 리뉴얼 v127</h1>' in html

p.write_text(html, encoding='utf-8')
print(f'renamed {old_refs} tanoStop references to stun (v126 history note preserved)')
