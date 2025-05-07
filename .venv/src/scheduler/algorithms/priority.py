from scheduler.process import Process
from scheduler.multicore.scheduler import Core
import math

class Priority:
    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        all_cores = pcores + ecores
        for p in ready_queue:
            p.executed = False
            p.start_time = None
            p.finish_time = None
            p.waiting_time = None
            p.turn_around_time = None
            p.normalized_TT = None

        while not all(p.executed for p in ready_queue):
            # 현재까지 도착한 미실행 프로세스
            available = [p for p in ready_queue if p.arrival_time <= time and not p.executed]
            if not available:
                time += 1
                continue
            avg_burst = sum(p.burst_time for p in available) / len(available)   # 평균 실행시간 계산
            # P/E 코어 할당 대상 분리
            pcore_candidates = [p for p in available if p.burst_time >= avg_burst]
            ecore_candidates = [p for p in available if p.burst_time < avg_burst]

            # P-core 우선 할당
            for core in pcores:
                if core.next_free_time <= time and pcore_candidates:
                    proc = pcore_candidates.pop(0)
                    self._assign(core, proc, time)
                    proc.executed = True

            # E-core 우선 할당
            for core in ecores:
              if core.next_free_time <= time and ecore_candidates:
                    proc = ecore_candidates.pop(0)
                    self._assign(core, proc, time)
                    proc.executed = True

            for core in pcores:
                if core.next_free_time <= time:
                    if pcore_candidates:
                        proc = pcore_candidates.pop(0)
                    elif ecore_candidates:
                        proc = ecore_candidates.pop(0)
                    else:
                        continue
                    self._assign(core, proc, time)
                    proc.executed = True

            # P-core에 할당 못한 남은 프로세스 처리
            for proc in pcore_candidates:
                # 가장 빨리 비는 P-core와 E-core의 종료시간 비교
                soonest_pcore = min(pcores, key=lambda c: c.next_free_time)
                soonest_ecore = min(ecores, key=lambda c: c.next_free_time)
                # 각 코어에서 실행 시 종료시간 예측
                p_start = max(soonest_pcore.next_free_time, proc.arrival_time)
                p_finish = p_start + (proc.burst_time + 1) // 2
                e_start = max(soonest_ecore.next_free_time, proc.arrival_time)
                e_finish = e_start + proc.burst_time
                # 더 빨리 끝나는 쪽에 할당
                if p_finish <= e_finish:
                    self._assign(soonest_pcore, proc, p_start)
                    soonest_pcore.next_free_time = p_finish
                else:
                    self._assign(soonest_ecore, proc, e_start)
                    soonest_ecore.next_free_time = e_finish
                proc.executed = True

            time += 1

    def _assign(self, core, proc, start):
        proc.real_burst = math.ceil(proc.burst_time / core.performance)
        finish = start + proc.real_burst
        core.timeline.append((start, proc.pid, proc.real_burst))
        core.next_free_time = finish
        proc.start_time = start
        proc.finish_time = finish
        proc.waiting_time = start - proc.arrival_time
        proc.turn_around_time = finish - proc.arrival_time
        proc.normalized_TT = round(proc.turn_around_time / proc.real_burst, 2)

        # 시동 전력: 코어가 유휴 상태였다면 추가
        if core.is_idle:
            core.total_power += core.startup_power
         # 동작 전력: burst * power_rate
            core.total_power += proc.real_burst * core.power_rate
