from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:180]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v83</title>','<title>볼배틀 리뉴얼 v84</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v83</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v84</h1>')
rep(
'''{ id:"newhello_sergeant", name:"뉴헬로 병장", mark:"⚔", role:"애니", color:"#4d7860", hp:170, attack:8, speed:3, range:48,''',
'''{ id:"newhello_sergeant", name:"뉴헬로 병장", mark:"⚔", role:"애니", color:"#4d7860", hp:160, attack:8, speed:3, range:48,'''
)
rep(
'''      const patchNotes = [
      "v83: 뉴헬로 병장 비접촉 광역베기 조정.''',
'''      const patchNotes = [
      "v84: 뉴헬로 병장 체력 170→160으로 10 하향. 비접촉 베기 +8, 광역 범위 +28, 일반8/와이어16, 출혈1×5·잔여 출혈 폭발, 와이어 속도650·적중 즉시 재와이어 등 나머지 전투 수치는 유지.",
      "v83: 뉴헬로 병장 비접촉 광역베기 조정.'''
)
p.write_text(t,encoding="utf-8")
