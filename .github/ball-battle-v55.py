from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    s = s.replace(old, new, 1)

replace_once('<title>볼배틀 리뉴얼 v54</title>', '<title>볼배틀 리뉴얼 v55</title>', 'title')
replace_once('songFameGain: 10,', 'songFameGain: 15,', 'song fame gain')
replace_once('''songLevels: [
        { radius: 90, damage: 3 },
        { radius: 110, damage: 4 },
        { radius: 130, damage: 5 },
        { radius: 150, damage: 6 }
      ],''', '''songLevels: [
        { radius: 90, damage: 4 },
        { radius: 110, damage: 6 },
        { radius: 130, damage: 8 },
        { radius: 150, damage: 10 }
      ],''', 'song levels')
replace_once('''if (c.id === "oshi") return { damage: "노래 1~4단계 피해 3/4/5/6 · 반경 90/110/130/150 / 투어 초당2 · 5초 연속 체류30 / 후유증: 체류 2초당 총3을 5초 DOT / 도쿄돔 칼35 + 출혈3×8 / 공연 연장 반경175·초당4·5초40", tick: "노래 2초 · 노래 적중 1명당 인지도+10 · 적 접촉 대상별 1초마다+4 · 인지도100에 투어", tip: "노래 적중자는 3초간 이동속도 20% 감소 및 최애에게 주는 모든 피해 20% 감소(감소 후 최소 피해 1). 최대 체력 비례 피해와 푸른 눈의 백룡 등 소환수 피해에도 적용된다. 투어 3회를 마친 뒤 다시 인지도100을 채우면 도쿄돔이 시작되며, 출혈 종료까지 생존하면 공연이 연장된다." };''', '''if (c.id === "oshi") return { damage: "노래 1~4단계 피해 4/6/8/10 · 반경 90/110/130/150 / 투어 초당2 · 5초 연속 체류30 / 후유증: 체류 2초당 총3을 5초 DOT / 도쿄돔 칼35 + 출혈3×8 / 공연 연장 반경175·초당4·5초40", tick: "노래 2초 · 노래 적중 1명당 인지도+15 · 적 접촉 대상별 1초마다+4 · 인지도100에 투어", tip: "노래 적중자는 3초간 이동속도 20% 감소 및 최애에게 주는 모든 피해 20% 감소(감소 후 최소 피해 1). 최대 체력 비례 피해와 푸른 눈의 백룡 등 소환수 피해에도 적용된다. 투어 3회를 마친 뒤 다시 인지도100을 채우면 도쿄돔이 시작되며, 출혈 종료까지 생존하면 공연이 연장된다." };''', 'oshi damage info')
replace_once('''    const patchNotes = [
      "v54:''', '''    const patchNotes = [
      "v55: 최애 공격 템포 상향. 노래 1~4단계 피해를 3/4/5/6→4/6/8/10으로 올리고, 노래 적중 1명당 인지도를 +10→+15로 높였다. 접촉 인지도·디버프·투어·도쿄돔 수치는 유지한다.",
      "v54:''', 'patch note')

path.write_text(s, encoding='utf-8')
print('patched index.html to v55')
