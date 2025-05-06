from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class Priority:
    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        # 모든 프로세서의 실행 여부 초기화
        for p in ready_queue:
            p.executed = False
        # 아직 실행되지 않은 모든 프로세스가 실행될 때까지 반복함
        while not all(p.executed for p in ready_queue):
            # 현재 시간까지 도착은 했으나 아직 실행안된  프로세스를 골라냄
            available = [p for p in ready_queue if p.arrival_time <= time and not p.executed]
            # 실행할 프로세스가 없으면 time에 +1하고 다시 검사
            if not available:
                time += 1
                continue
            # 현재 대기 중인 프로세스의 평균 실행시간 계산
            avg_burst = sum(p.burst_time for p in available) / len(available)

            # 각 코어에 할당할 프로세스 분리
            pcore_proc = [p for p in available if p.burst_time > avg_burst]
            ecore_proc = [p for p in available if p.burst_time <= avg_burst]

            # P-core에 우선하여 할당
            for core in pcores:
                if core.next_free_time <= time and pcore_proc:
                    proc = pcore_proc.pop(0)
                    self._assign(core, proc, time)
                    proc.executed = True

            # E-core에 우선하여 할당
            for core in ecores:
                if core.next_free_time <= time and ecore_proc:
                    proc = ecore_proc.pop(0)
                    self._assign(core, proc, time)
                    proc.executed = True

            # 지금 일하고 있지 않은 P-core가 있다면 아직 할당 못한 heavy나 heavy가 없으면 light를 실행
            for core in pcores:
                if core.next_free_time <= time:
                    if pcore_proc:
                        proc = pcore_proc.pop(0)
                    elif ecore_proc:
                        proc = ecore_proc.pop(0)
                    else:
                        continue # 할당할 프로세스가 없으면 패스
                    self._assign(core, proc, time)
                    proc.executed = True

            # P-core에 할당 못한 남은 프로세스 처리
            for proc in pcore_proc:
                # 가장 빨리 비는 P-core와 E-core의 종료시간 찾기
                finish_pcore = min(pcores, key=lambda c: c.next_free_time)
                finish_ecore = min(ecores, key=lambda c: c.next_free_time)
                # P-core에서 실행 시작 및 종료 시간 예측
                p_start = max(finish_pcore.next_free_time, proc.arrival_time)
                p_finish = p_start + (proc.burst_time + 1) // 2
                # E-core에서 실행 시작 및 종료 시간 예측
                e_start = max(finish_ecore.next_free_time, proc.arrival_time)
                e_finish = e_start + proc.burst_time
                # 더 빨리 끝나는 쪽에 할당
                if p_finish <= e_finish:
                    self._assign(finish_pcore, proc, p_start)
                    finish_pcore.next_free_time = p_finish
                else:
                    self._assign(finish_ecore, proc, e_start)
                    finish_ecore.next_free_time = e_finish
                proc.executed = True

            time += 1

    def _assign(self, core, proc, start):
        # 코어 종류별 실제 동작 시간 계산
        if core.core_type == 'P':
            burst = (proc.burst_time + 1) // 2
        else:
            burst = proc.burst_time
        # 종료 시간 계산
        finish = start + burst
        # 코어 타임라인에 기록
        core.timeline.append((start, proc.pid, burst))
        core.next_free_time = finish
        proc.start_time = start
        proc.finish_time = finish
        proc.waiting_time = start - proc.arrival_time
        proc.turn_around_time = finish - proc.arrival_time
        proc.normalized_TT = round(proc.turn_around_time / proc.burst_time, 2)

        # 전력 계산: 유휴 상태라면 시동 전력 + 동작 전력
        if core.is_idle:
            core.total_power += core.startup_power
            core.startup_count += 1
        core.total_power += burst * core.power_rate
