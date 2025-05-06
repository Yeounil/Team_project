from collections import deque
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class RoundRobin:
    def __init__(self, quantum=2):
        self.quantum = quantum

    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        all_cores = pcores + ecores
        n_cores = len(all_cores)

        # 프로세스 초기화
        for p in ready_queue:
            p.remaining_time = p.burst_time
            p.start_time = None
            p.finish_time = None
            p.executed = False

        running = [None] * n_cores
        quantum_counter = [0] * n_cores
        rr_queue = deque()
        arrival_sorted = sorted(ready_queue, key=lambda p: (p.arrival_time, p.pid))
        arrived_idx = 0

        # 프로세스별 실제 실행 step 카운트(정규화TT용)
        for p in ready_queue:
            p.real_burst = 0

        while not all(p.executed for p in ready_queue):
            # 도착 프로세스 추가
            while arrived_idx < len(arrival_sorted) and arrival_sorted[arrived_idx].arrival_time <= time:
                rr_queue.append(arrival_sorted[arrived_idx])
                arrived_idx += 1

            assigned_pid = set()

            # 종료/선점/할당 처리
            for i, core in enumerate(all_cores):
                proc = running[i]

                # 종료 처리
                if proc and proc.remaining_time <= 0:
                    if proc.finish_time is None:
                        proc.finish_time = time
                    proc.executed = True
                    running[i] = None
                    quantum_counter[i] = 0

                # 타임퀀텀 소진 → 다시 큐로
                if proc and quantum_counter[i] <= 0 and proc.remaining_time > 0:
                    rr_queue.append(proc)
                    running[i] = None

                # 새 프로세스 할당
                if running[i] is None:
                    for idx, p in enumerate(rr_queue):
                        if not p.executed and p.pid not in assigned_pid and p.remaining_time > 0:
                            running[i] = p
                            quantum_counter[i] = self.quantum
                            assigned_pid.add(p.pid)
                            rr_queue.remove(p)
                            break

            # [핵심] 각 코어가 "성능만큼" 반복 실행 (P=2, E=1)
            for i, core in enumerate(all_cores):
                proc = running[i]
                if proc and proc.remaining_time > 0 and quantum_counter[i] > 0:
                    performance = core.performance  # P=2, E=1
                    # 실제로 몇 번 실행했는지 기록
                    actual_exec = 0
                    for _ in range(performance):
                        if proc.remaining_time > 0 and quantum_counter[i] > 0:
                            if proc.start_time is None:
                                # 최초 실행 step의 "tick+실제 실행 step"을 기록
                                proc.start_time = time
                            proc.remaining_time -= 1
                            quantum_counter[i] -= 1
                            proc.real_burst += 1
                            actual_exec += 1
                            core.timeline.append((time, proc.pid, 1))
                            core.total_power += core.power_rate
                            if core.is_idle:
                                core.total_power += core.startup_power
                                core.startup_count += 1
                            core.is_idle = False
                    # 만약 이번 tick에서 프로세스가 끝나면 finish_time을 "tick+실행 step"으로 기록
                    if proc.remaining_time == 0 and proc.finish_time is None:
                        # 실제로 마지막 실행이 몇 번째 step에서 일어났는지 반영
                        proc.finish_time = time + 1
                        proc.executed = True
                        running[i] = None
                        quantum_counter[i] = 0
                else:
                    core.is_idle = True

            # tick 끝나고 선점/종료 재확인
            for i, core in enumerate(all_cores):
                proc = running[i]
                if proc:
                    if proc.remaining_time == 0 and proc.finish_time is None:
                        proc.finish_time = time + 1
                        proc.executed = True
                        running[i] = None
                        quantum_counter[i] = 0
                    elif quantum_counter[i] == 0:
                        rr_queue.append(proc)
                        running[i] = None

            # 시간 이동
            if all(r is None for r in running) and not rr_queue and arrived_idx < len(arrival_sorted):
                time = arrival_sorted[arrived_idx].arrival_time
            else:
                time += 1

        # WT, TT, NTT 계산
        for p in ready_queue:
            # start_time, finish_time이 None인 경우 보정
            if p.finish_time is None:
                p.finish_time = time
            if p.start_time is None:
                p.start_time = p.arrival_time
            p.turn_around_time = p.finish_time - p.arrival_time
            p.waiting_time = p.turn_around_time - p.burst_time
            # NTT는 burst_time(=real_burst)로 나누는 것이 더 직관적
            if p.burst_time > 0:
                p.normalized_TT = round(p.turn_around_time / p.burst_time, 2)
            else:
                p.normalized_TT = 0.0
