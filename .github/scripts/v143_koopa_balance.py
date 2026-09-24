from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 marker, found {n}')
    s=s.replace(old,new,1)

def exact_count(old,new,count,label):
    global s
    n=s.count(old)
    if n!=count:
        raise SystemExit(f'{label}: expected {count} markers, found {n}')
    s=s.replace(old,new)

exact_count('볼배틀 리뉴얼 v142','볼배틀 리뉴얼 v143',2,'version')

once('condition:"등껍질 11초 주기 · 불기둥 9초 주기 · 저체력일수록 불기둥 1→4개", desc:"거대한 몸집의 마왕형 캐릭터. 등껍질 돌진으로 적을 강하게 날리고 벽충돌 피해를 만들며, 마지막 3초에는 상대를 추적한다. 돌진이 끝나면 제자리에서 3초 기절한다. 맵 중앙을 축으로 회전하는 불기둥은 체력이 낮을수록 늘어난다."',
     'condition:"등껍질 11초 주기 · 불기둥 20초 주기 · 저체력일수록 불기둥 1→4개", desc:"거대한 몸집의 마왕형 캐릭터. 등껍질 돌진으로 적을 강하게 날리고 벽충돌 피해를 만들며, 마지막 3초에는 상대를 추적한다. 상대와 충돌하면 즉시 돌진을 끝내고 제자리에서 3초 기절하며, 기절 중 받는 피해가 2배가 된다. 맵 중앙을 축으로 회전하는 불기둥은 체력이 낮을수록 늘어난다."',
     'character description')

once('tick: "등껍질 11초 주기·6초 지속·종료 후 3초 기절 / 불기둥 9초 주기·4.5초 지속",\n          tip: "등껍질은 돌진 1회 동안 같은 상대를 최대 1회만 타격하며, 마지막 3초 동안 적을 추적한다. 중앙 회전 불기둥은 HP 75% 초과 1개, 50~75% 2개, 25~50% 3개, 25% 이하 4개다. 넉백 저항은 없다."',
     'tick: "등껍질 11초 주기·6초 지속·충돌 시 즉시 종료 후 3초 기절 / 불기둥 20초 주기·4.5초 지속",\n          tip: "등껍질은 돌진 1회 동안 같은 상대를 최대 1회만 타격하며, 마지막 3초 동안 적을 추적한다. 상대와 충돌해 기절한 3초 동안 쿱하가 받는 피해는 2배다. 중앙 회전 불기둥은 HP 75% 초과 1개, 50~75% 2개, 25~50% 3개, 25% 이하 4개다. 넉백 저항은 없다."',
     'damage info')

once('firePeriod:9, fireDuration:4.5, fireDamage:6, fireBurnDamage:1, fireBurnTicks:4, fireBurnTick:.6,',
     'firePeriod:20, fireDuration:4.5, fireDamage:6, fireBurnDamage:1, fireBurnTicks:4, fireBurnTick:.6,',
     'fire cooldown')

once('if(!fastSimMode){spawnHitFlash(target.x,target.y,"#bef264",58);spawnParticles(target.x,target.y,"#84cc16",10);}\n      return dealt>0;',
     'if(!fastSimMode){spawnHitFlash(target.x,target.y,"#bef264",58);spawnParticles(target.x,target.y,"#84cc16",10);}\n      koopaEndShell(source);\n      return dealt>0;',
     'shell collision recovery')

once('if (tryHeroLeonGuardBlock(target, reason)) return 0;\n',
     'if (tryHeroLeonGuardBlock(target, reason)) return 0;\n      if (target.koopa?.recovery > 0) amount *= 2;\n',
     'koopa vulnerability')

once('if(k.recovery>0)return {ratio:clamp(k.recovery/KOOPA.recoveryStun,0,1),className:"rage-fill",text:`등껍질 후 기절 ${k.recovery.toFixed(1)}초`,extraTextHtml:`<div class="status-skill-label">불기둥 ${fire?`발동 중 · ${fireCount}개 · ${fire.life.toFixed(1)}초`:`${Math.max(0,k.fireCd).toFixed(1)}초 후`}</div>`};',
     'if(k.recovery>0)return {ratio:clamp(k.recovery/KOOPA.recoveryStun,0,1),className:"rage-fill",text:`등껍질 후 기절 ${k.recovery.toFixed(1)}초 · 받는 피해 ×2`,extraTextHtml:`<div class="status-skill-label">불기둥 ${fire?`발동 중 · ${fireCount}개 · ${fire.life.toFixed(1)}초`:`${Math.max(0,k.fireCd).toFixed(1)}초 후`}</div>`};',
     'recovery status')

once('if(k.shellActive)return {ratio:clamp(k.shellTime/KOOPA.shellDuration,0,1),className:"skill-fill",text:`등껍질 돌진 ${k.shellTime.toFixed(1)}초${k.shellTime<=KOOPA.shellTrackAt?" · 추적 중":""}`,extraTextHtml:`<div class="status-skill-label">종료 후 3초 기절 · 불기둥 ${fire?`${fireCount}개 발동 중`:`${Math.max(0,k.fireCd).toFixed(1)}초 후`}</div>`};',
     'if(k.shellActive)return {ratio:clamp(k.shellTime/KOOPA.shellDuration,0,1),className:"skill-fill",text:`등껍질 돌진 ${k.shellTime.toFixed(1)}초${k.shellTime<=KOOPA.shellTrackAt?" · 추적 중":""}`,extraTextHtml:`<div class="status-skill-label">충돌 시 즉시 3초 기절(받피×2) · 불기둥 ${fire?`${fireCount}개 발동 중`:`${Math.max(0,k.fireCd).toFixed(1)}초 후`}</div>`};',
     'shell status')

anchor='      const patchNotes = [\n'
if anchor not in s:
    raise SystemExit('patch notes anchor missing')
s=s.replace(anchor,anchor+'      "v143: 쿱하 밸런스 조정. 등껍질 돌진이 상대와 충돌하면 즉시 종료되고 3초 기절하며, 그 기절 동안 받는 피해가 2배가 됨. 회전 불기둥 쿨타임 9초→20초. 그 외 쿱하 수치와 기술 구조는 유지.",\n',1)

p.write_text(s,encoding='utf-8')
print('v143 patch applied')
