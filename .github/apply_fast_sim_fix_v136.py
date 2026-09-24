from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if '<title>볼배틀 리뉴얼 v136</title>' in s:
    print('v136 already applied')
    raise SystemExit(0)

def replace_one(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    s = s.replace(old, new, 1)

replace_one('<title>볼배틀 리뉴얼 v135</title>', '<title>볼배틀 리뉴얼 v136</title>', 'title')

# 빠른 시뮬레이션에서는 매 스텝마다 DOM HUD/상태창을 다시 그리지 않는다.
replace_one(
'''      updateHud();
      updateStatusPanel();
    }

    function spawnParticles''',
'''      if (!fastSimMode) {
        updateHud();
        updateStatusPanel();
      }
    }

    function spawnParticles''',
'fast sim DOM suppression'
)

# 한 경기 자체가 길어질 때도 브라우저 이벤트 루프에 주기적으로 제어권을 돌려준다.
replace_one(
'''        while (running && !ended && battleTime < 500 && guard < 20000) {
          update(0.033);
          guard += 1;
        }
''',
'''        while (running && !ended && battleTime < 500 && guard < 20000) {
          update(0.033);
          guard += 1;
          if (guard % 600 === 0) {
            await new Promise(resolve => setTimeout(resolve, 0));
          }
        }
''',
'quick sim cooperative yield'
)

# fastSimMode 동안 requestAnimationFrame 루프가 같은 전투 상태를 동시에 update하지 않게 한다.
replace_one(
'''      // 배속 버튼이 실제 시뮬레이션 시간에 반영되도록 처리한다.
      // 4배속에서도 충돌/투사체가 지나치게 건너뛰지 않도록 작은 단위로 쪼개 업데이트한다.
      const gambleScale = performance.now() < gambleSlowUntil ? 0.18 : 1;
      let simLeft = realDt * speedMultiplier * gambleScale;
      const step = 0.033;
      while (simLeft > 0 && cinematicFreeze <= 0) {
        update(Math.min(step, simLeft));
        simLeft -= step;
      }
''',
'''      // 자동 테스트 중에는 simulateQuickPair만 전투 상태를 갱신한다.
      // requestAnimationFrame 루프까지 동시에 update하면 전체 테스트 상태가 중복 진행된다.
      if (!fastSimMode) {
        // 배속 버튼이 실제 시뮬레이션 시간에 반영되도록 처리한다.
        // 4배속에서도 충돌/투사체가 지나치게 건너뛰지 않도록 작은 단위로 쪼개 업데이트한다.
        const gambleScale = performance.now() < gambleSlowUntil ? 0.18 : 1;
        let simLeft = realDt * speedMultiplier * gambleScale;
        const step = 0.033;
        while (simLeft > 0 && cinematicFreeze <= 0) {
          update(Math.min(step, simLeft));
          simLeft -= step;
        }
      }
''',
'raf fast sim isolation'
)

p.write_text(s, encoding='utf-8')
print('fast simulation stability fix v136 applied')
