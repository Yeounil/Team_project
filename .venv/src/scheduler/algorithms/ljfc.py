from scheduler.process import Process
from scheduler.multicore.scheduler import Core
import math

class LJFC:
    def schedule(self, ready_queue, pcores, ecores):
        time = 0

        while not all(p.executed for p in ready_queue):
            # 현재까지 도착한 미실행 프로세스
            available = [p for p in ready_queue if p.arrival_time <= time and not p.executed]
            if not available:
                time += 1
                continue
            avg_burst = sum(p.burst_time for p in available) / len(available)   # 평균 실행시간 계산
            # P/E 코어 할당 대상 분리
            pcore_proc = [p for p in available if p.burst_time >= avg_burst]
            ecore_proc = [p for p in available if p.burst_time < avg_burst]

            for core in pcores:
                # next_free_time < time 일 때만 진짜 쉬고 있던 코어
                if core.next_free_time < time:
                    core.is_idle = True

            for core in ecores:
                # next_free_time < time 일 때만 진짜 쉬고 있던 코어
                if core.next_free_time < time:
                    core.is_idle = True

            # P-core 우선 할당
            for core in pcores:
                if core.next_free_time <= time and pcore_proc:
                    proc = pcore_proc.pop(0)
                    self._assign(core, proc, time)
                    proc.executed = True

            # E-core 우선 할당
            for core in ecores:
                if core.next_free_time <= time and ecore_proc:
                    proc = ecore_proc.pop(0)
                    self._assign(core, proc, time)
                    proc.executed = True

            for core in pcores:
                if core.next_free_time <= time:
                    if pcore_proc:
                        proc = pcore_proc.pop(0)
                    elif ecore_proc:
                        proc = ecore_proc.pop(0)
                    else:
                        continue
                    self._assign(core, proc, time)
                    proc.executed = True

            # P-core에 할당 못한 남은 프로세스 처리
            for proc in pcore_proc:
                # 가장 빨리 비는 P-core와 E-core의 종료시간 비교
                finish_pcore = min(pcores, key=lambda c: c.next_free_time)
                # E-코어가 하나라도 있으면 finish 비교, 없으면 바로 P-코어로
                if ecores:
                    finish_ecore = min(ecores, key=lambda c: c.next_free_time)

                    # P vs E 종료 시각 예측
                    p_start = max(finish_pcore.next_free_time, proc.arrival_time)
                    p_finish = p_start + (proc.burst_time + 1) // 2

                    e_start = max(finish_ecore.next_free_time, proc.arrival_time)
                    e_finish = e_start + proc.burst_time

                    if p_finish <= e_finish:
                        self._assign(finish_pcore, proc, p_start)
                        finish_pcore.next_free_time = p_finish
                    else:
                        self._assign(finish_ecore, proc, e_start)
                        finish_ecore.next_free_time = e_finish
                else:
                    # E-코어가 없으면 무조건 P-코어
                    p_start = max(finish_pcore.next_free_time, proc.arrival_time)
                    p_finish = p_start + (proc.burst_time + 1) // 2
                    self._assign(finish_pcore, proc, p_start)
                    finish_pcore.next_free_time = p_finish

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
            core.is_idle = False
        # 동작 전력: burst * power_rate
        core.total_power += proc.real_burst * core.power_rate
