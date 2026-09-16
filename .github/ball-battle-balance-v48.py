from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

def rep(old, new, count=1):
    global text
    found = text.count(old)
    if found != count:
        raise SystemExit(f'anchor count mismatch: expected {count}, got {found}: {old[:120]!r}')
    text = text.replace(old, new, count)

rep('<title>볼배틀 리뉴얼 v47</title>', '<title>볼배틀 리뉴얼 v48</title>')

rep('const roleLabels = ["전체", "전사", "마법사", "수호자", "암살자", "지원가", "저격수"];', 'const roleLabels = ["전체", "영화", "애니"];')

rep('{ id: "lisa", name: "리사", mark: "♫", role: "전사",', '{ id: "lisa", name: "리사", mark: "♫", role: "애니",')
rep('{ id: "iron_mask", name: "철가면", mark: "Fe", role: "전사",', '{ id: "iron_mask", name: "철가면", mark: "Fe", role: "영화",')
rep('{ id: "tano", name: "타노", mark: "✦", role: "전사",', '{ id: "tano", name: "타노", mark: "✦", role: "영화",')
rep('{ id: "captain", name: "캡틴", mark: "★", role: "수호자",', '{ id: "captain", name: "캡틴", mark: "★", role: "영화",')
rep('{ id: "jabami", name: "쟈바미", mark: "♦", role: "마법사",', '{ id: "jabami", name: "쟈바미", mark: "♦", role: "애니",')
rep('{ id: "justice_ally", name: "정의의 아군", mark: "D", role: "마법사", color: "#f8fafc", hp: 170,', '{ id: "justice_ally", name: "정의의 아군", mark: "D", role: "애니", color: "#f8fafc", hp: 160,')
rep('{ id: "logo_doctor", name: "로고 박사", mark: "博", role: "전사",', '{ id: "logo_doctor", name: "로고 박사", mark: "博", role: "영화",')

rep('const LISA = { patience: 40, idleDelay: 5, idleGain: 2, duration: 14, rageDuration: 4, rageRange: 190, period: 1.25, ragePeriod: 0.55, power: 8, range: 150, halfAngle: Math.PI / 4, speed: 2.7 };',
    'const LISA = { patience: 40, idleDelay: 5, idleGain: 2, duration: 14, rageDuration: 4, rageRange: 190, period: 1.25, ragePeriod: 0.55, power: 8, ragePower: 9, range: 150, halfAngle: Math.PI / 4, speed: 2.7 };')
rep('enemiesOf(f).filter(e => lisaConeTouches(f, e, angle)).forEach(e => damage(e, LISA.power, f, "파워코드 음파"));',
    'const waveDamage = f.lisa.mode === "rage" ? LISA.ragePower : LISA.power;\n      enemiesOf(f).filter(e => lisaConeTouches(f, e, angle)).forEach(e => damage(e, waveDamage, f, "파워코드 음파"));')
rep('if (c.id==="lisa") return {damage:"최근접 적 방향 90도 음파 8 · 록 사거리150 / 폭주190",',
    'if (c.id==="lisa") return {damage:"최근접 적 방향 90도 음파 8 · 폭주 음파 9 · 록 사거리150 / 폭주190",')

rep('    const patchNotes = [\n      "v47:', '    const patchNotes = [\n      "v48: 리사 일반 음파 피해 8 유지, 폭주 상태 음파만 9로 상향. 정의의 아군 본체 체력 170→160. 캐릭터 분류를 전사·마법사 등 전투 역할에서 영화·애니 출처 분류로 변경.",\n      "v47:')

path.write_text(text, encoding='utf-8')
print('patched index.html to v48')
