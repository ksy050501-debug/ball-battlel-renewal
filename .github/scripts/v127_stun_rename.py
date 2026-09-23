from pathlib import Path

p = Path('index.html')
html = p.read_text(encoding='utf-8')

assert '<title>볼배틀 리뉴얼 v126</title>' in html
assert '<h1 id="mainTitle">볼배틀 리뉴얼 v126</h1>' in html

old_refs = html.count('tanoStop')
assert old_refs >= 8, f'unexpected tanoStop ref count: {old_refs}'
assert 'target.tanoStop = Math.max(target.tanoStop || 0, duration);' in html

# Pure identifier rename. Every runtime read/write/blocking check uses the same new state name.
html = html.replace('tanoStop', 'stun')

# Historical v126 note is reworded so the obsolete identifier does not remain anywhere in the file.
html = html.replace(
    '기존 stun·freeze·캐릭터별 타이머 저장값과 지속시간·중첩·면역·넉백·피해·연출은 그대로 유지해 전투 성능은 변경하지 않았습니다.',
    '기존 행동정지 저장값·freeze·캐릭터별 타이머의 지속시간·중첩·면역·넉백·피해·연출은 그대로 유지해 전투 성능은 변경하지 않았습니다.'
)

html = html.replace('<title>볼배틀 리뉴얼 v126</title>', '<title>볼배틀 리뉴얼 v127</title>', 1)
html = html.replace('<h1 id="mainTitle">볼배틀 리뉴얼 v126</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v127</h1>', 1)

note = '      "v127: 공용 행동정지의 내부 저장명까지 정리했습니다. 기존 캐릭터 전용 이름의 행동정지 프로퍼티를 stun으로 전수 이름 변경하고 applyStun 및 모든 행동정지 판정·감소·차단 참조를 같은 stun 저장값으로 통일했습니다. 숫자·지속시간·적용 조건·면역·피해·넉백·연출은 변경하지 않은 순수 명칭 리팩터링입니다.",\n'
needle = '      const patchNotes = [\n'
assert needle in html
html = html.replace(needle, needle + note, 1)

assert 'tanoStop' not in html
assert 'target.stun = Math.max(target.stun || 0, duration);' in html
assert 'f.stun = Math.max(0, (f.stun || 0) - dt);' in html
assert '<title>볼배틀 리뉴얼 v127</title>' in html
assert '<h1 id="mainTitle">볼배틀 리뉴얼 v127</h1>' in html

p.write_text(html, encoding='utf-8')
print(f'renamed {old_refs} action-stop references to stun')
