from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')
orig = s

repls = [
    ('<title>볼배틀 리뉴얼 v64</title>', '<title>볼배틀 리뉴얼 v65</title>'),
    ('quickDamage: 12, freakDamage: 24, quickSpeed: 380, freakSpeed: 570, maxContacts: 3,\n      dashWait: 4, dashSpeed: 480, dashDamage: 10, concussion: 2, slowMultiplier: .6',
     'quickDamage: 18, freakDamage: 50, quickSpeed: 380, freakSpeed: 570, maxContacts: 3,\n      dashWait: 4, dashSpeed: 480, dashDamage: 12, concussion: 2, slowMultiplier: .6'),
    ('// 빠른 대신 시전 당시 방향에 20~40도 오차. 발사 후 유도하지 않는다.',
     '// 빠른 대신 시전 당시 방향에 10~25도 오차. 발사 후 유도하지 않는다.'),
    ('angle=Math.atan2(target.y-b.y,target.x-b.x)+(Math.random()<.5?-1:1)*rand(Math.PI/9,Math.PI*2/9);',
     'angle=Math.atan2(target.y-b.y,target.x-b.x)+(Math.random()<.5?-1:1)*rand(Math.PI/18,Math.PI*5/36);'),
    ("extraTextHtml:'<div class=\"status-skill-label\">속공12 / 괴짜 속공24 · 돌진10＋뇌진탕2초</div>'",
     "extraTextHtml:'<div class=\"status-skill-label\">속공18 / 괴짜 속공50 · 돌진12＋뇌진탕2초</div>'")
]
for old, new in repls:
    assert old in s, f'missing: {old[:80]}'
    s = s.replace(old, new, 1)

anchor = '      "v64: 힌타 벽 반사 시 접촉 잠금을 해제해 같은 적 재타격 명시 보장(총3회 유지). 대기 공을 4초간 못 잡으면 직선 대쉬480, 경로 적에게 돌진당 1회 피해10·측면 넉백·넉백 후 뇌진탕2초(이속40% 감소). 공 접촉 시 스파이크, 비행 공 재타격 금지 유지.",'
note = '      "v65: 힌타 공격력 상향. 3터치·재등장5초·대쉬 대기4초는 유지하고 속공12→18, 괴짜 속공24→50, 괴짜 속공 오차20~40도→10~25도, 대쉬 피해10→12로 조정.",\n'
assert anchor in s
s = s.replace(anchor, note + anchor, 1)

assert s != orig
path.write_text(s, encoding='utf-8')
