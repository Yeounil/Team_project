from collections import deque
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class RoundRobin:
    def __init__(self, quantum=2):
        self.quantum = quantum

    def schedule(self, ready_queue, pcores, ecores):
        time       = 0
        all_cores  = pcores + ecores
        n_cores    = len(all_cores)

        # ── 1) 프로세스 초기화 ──
        for p in ready_queue:
            p.remaining_time = p.burst_time
            p.real_burst     = 0       # 실제 "틱" 단위 서비스 시간
            p.start_time     = None
            p.finish_time    = None
            p.executed       = False

        # ── 2) RR 상태 유지 자료구조 ──
        running         = [None] * n_cores
        quantum_counter = [0]    * n_cores
        rr_queue        = deque()
        arrival_sorted  = sorted(ready_queue, key=lambda p: (p.arrival_time, p.pid))
        arrived_idx     = 0

        # ── 3) 메인 루프: 모든 프로세스 완료될 때까지 tick 단위 시뮬레이션 ──
        while not all(p.executed for p in ready_queue):
            # 3-a) 새 도착 프로세스 RR 큐에 추가
            while arrived_idx < len(arrival_sorted) and \
                  arrival_sorted[arrived_idx].arrival_time <= time:
                rr_queue.append(arrival_sorted[arrived_idx])
                arrived_idx += 1

            assigned_pid = set()

            # 3-b) 종료, 타임퀀텀 소진, 새 할당
            for i, core in enumerate(all_cores):
                proc = running[i]

                # 종료 처리: remaining_time ≤ 0 → finish_time = time+1
                if proc and proc.remaining_time <= 0:
                    if proc.finish_time is None:
                        proc.finish_time = time + 1
                    proc.executed      = True
                    running[i]         = None
                    quantum_counter[i] = 0

                # 타임퀀텀 소진 시 대기열로 복귀
                elif proc and quantum_counter[i] <= 0 and proc.remaining_time > 0:
                    rr_queue.append(proc)
                    running[i]         = None

                # 빈 코어에 새 프로세스 할당
                if running[i] is None and rr_queue:
                    for idx, p in enumerate(rr_queue):
                        if (not p.executed) and (p.pid not in assigned_pid):
                            running[i]         = p
                            quantum_counter[i] = self.quantum
                            assigned_pid.add(p.pid)
                            rr_queue.remove(p)
                            # 최초 실행 시각 기록
                            if p.start_time is None:
                                p.start_time = time
                            break

            # 3-c) 1초 tick 동안 core 성능만큼 실행
            for i, core in enumerate(all_cores):
                proc = running[i]
                if not proc or proc.remaining_time <= 0 or quantum_counter[i] <= 0:
                    core.is_idle = True
                    continue

                # P-코어는 2단위, E-코어는 1단위 처리
                work = min(core.performance, proc.remaining_time)
                proc.remaining_time -= work
                proc.real_burst     += 1       # tick 단위로만 카운트
                quantum_counter[i] -= 1

                # Gantt 차트용 기록: tick 동안 work번 1초씩
                for _ in range(work):
                    core.timeline.append((time, proc.pid, 1))

                # 전력 계산: 시동 전력은 1회, 실행 전력은 work*rate
                if core.is_idle:
                    core.total_power   += core.startup_power
                    core.startup_count += 1
                    core.is_idle        = False
                core.total_power += core.power_rate * work

                # tick 중 종료 시 finish_time = time+1
                if proc.remaining_time == 0 and proc.finish_time is None:
                    proc.finish_time = time + 1
                    proc.executed    = True
                    running[i]       = None
                    quantum_counter[i] = 0

            # 3-d) 시간 이동: 대기 중이면 다음 arrival로, 아니면 +1초
            if all(r is None for r in running) and not rr_queue and arrived_idx < len(arrival_sorted):
                time = arrival_sorted[arrived_idx].arrival_time
            else:
                time += 1

        # ── 4) 최종 메트릭 계산 ──
        for p in ready_queue:
            # finish/start 보정
            if p.finish_time is None:
                p.finish_time = time
            if p.start_time is None:
                p.start_time = p.arrival_time

            p.turn_around_time = p.finish_time - p.arrival_time
            # WT = TT – 실제 서비스 시간(tick 수)
            p.waiting_time     = p.turn_around_time - p.real_burst
            # NTT = TT / real_burst
            p.normalized_TT    = round(p.turn_around_time / p.real_burst, 2)
