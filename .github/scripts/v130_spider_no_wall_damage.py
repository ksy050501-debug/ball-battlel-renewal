from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

assert '<title>볼배틀 리뉴얼 v129</title>' in s
assert '<h1 id="mainTitle">볼배틀 리뉴얼 v129</h1>' in s

s = s.replace('<title>볼배틀 리뉴얼 v129</title>', '<title>볼배틀 리뉴얼 v130</title>', 1)
s = s.replace('<h1 id="mainTitle">볼배틀 리뉴얼 v129</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v130</h1>', 1)

old = '      meleeDamage:18, meleeKnock:620, wallDamage:12, wallMarkTime:1.25,'
new = '      meleeDamage:18, meleeKnock:620,'
assert old in s
s = s.replace(old, new, 1)

old = '      if(target.alive&&dealt>0){target.vx=dx/d*SPIDER.meleeKnock;target.vy=dy/d*SPIDER.meleeKnock;target.punchFlight=Math.max(target.punchFlight||0,.34);target.punchSource=f;target.punchWallPower=0;target.punchWallHits=0;target.spiderWallMark=Math.max(target.spiderWallMark||0,SPIDER.wallMarkTime);target.spiderWallSourceId=f.id;}'
new = '      if(target.alive&&dealt>0){target.vx=dx/d*SPIDER.meleeKnock;target.vy=dy/d*SPIDER.meleeKnock;target.punchFlight=Math.max(target.punchFlight||0,.34);target.punchSource=null;target.punchWallPower=0;target.punchWallHits=0;}'
assert old in s
s = s.replace(old, new, 1)

old = '        if((target.spiderWallMark||0)>0&&target.spiderWallSourceId===f.id&&nearWall){target.spiderWallMark=0;const dealt=damage(target,SPIDER.wallDamage,f,"웹스윙 벽충돌");if(!fastSimMode){spawnBlast(target.x,target.y,76,"#f8fafc");spawnFloatingText(target.x,target.y-target.r-38,"벽충돌 -"+Math.round(dealt),"#fecaca");}}\n'
assert old in s
s = s.replace(old, '', 1)

old = '      f.spiderWallMark=Math.max(0,(f.spiderWallMark||0)-dt);\n'
assert old in s
s = s.replace(old, '', 1)

old = '      if (c.id === "spider_man") return {damage:"웹슈터2×6 / 속박 연계 웹스윙 근접타격18 + 벽충돌12",tick:"웹슈터5초마다6발(0.09초 간격) · 웹슈터 넉백 판정0.22초 · 그동안 벽충돌 시 속박1.6초→웹스윙 돌진",tip:"5초마다 웹슈터를 6연사한다. 각 탄은 피해2·약한 넉백·0.9초 22% 둔화를 준다. 웹슈터에 맞아 밀려나는 0.22초 안에 실제로 벽에 충돌한 경우에만 1.6초 속박되며, 예전에 맞은 뒤 한참 후 벽에 닿는 것은 속박되지 않는다. 속박 성공 시 해당 상대에게만 웹스윙 돌진을 사용해 근접타격18과 강한 넉백을 주고, 그 넉백으로 벽에 닿으면 추가12 피해를 준다. 자동·랜덤 웹스윙과 벽 부채꼴 연쇄 스윙은 없다."};'
new = '      if (c.id === "spider_man") return {damage:"웹슈터2×6 / 속박 연계 웹스윙 근접타격18",tick:"웹슈터5초마다6발(0.09초 간격) · 웹슈터 넉백 판정0.22초 · 그동안 벽충돌 시 속박1.6초→웹스윙 돌진",tip:"5초마다 웹슈터를 6연사한다. 각 탄은 피해2·약한 넉백·0.9초 22% 둔화를 준다. 웹슈터에 맞아 밀려나는 0.22초 안에 실제로 벽에 충돌한 경우에만 1.6초 속박되며, 예전에 맞은 뒤 한참 후 벽에 닿는 것은 속박되지 않는다. 속박 성공 시 해당 상대에게만 웹스윙 돌진을 사용해 근접타격18과 강한 넉백을 준다. 웹스윙 넉백으로 벽에 충돌해도 추가 피해는 없다. 자동·랜덤 웹스윙과 벽 부채꼴 연쇄 스윙은 없다."};'
assert old in s
s = s.replace(old, new, 1)

anchor = '      const patchNotes = [\n'
assert anchor in s
note = '      "v130: 거미남의 웹스윙 돌진 후 벽충돌 추가 피해를 완전히 제거했습니다. 웹스윙 근접타격18과 강한 넉백은 유지하지만, 그 넉백은 공용 강펀치 벽충돌 피해 판정에 연결되지 않으며 거미남 전용 벽충돌12 판정도 삭제했습니다. 따라서 웹스윙으로 날아간 상대가 벽에 여러 번 튕겨도 추가 피해는 0입니다.",\n'
s = s.replace(anchor, anchor + note, 1)

assert '<title>볼배틀 리뉴얼 v130</title>' in s
assert '<h1 id="mainTitle">볼배틀 리뉴얼 v130</h1>' in s
assert 'meleeDamage:18, meleeKnock:620, wallDamage:12' not in s
assert 'target.punchSource=null;target.punchWallPower=0;target.punchWallHits=0;' in s
assert 'damage:"웹슈터2×6 / 속박 연계 웹스윙 근접타격18"' in s
assert '웹스윙 넉백으로 벽에 충돌해도 추가 피해는 없다.' in s

p.write_text(s, encoding='utf-8')
