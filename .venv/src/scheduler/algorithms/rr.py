from collections import deque

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
            p.real_burst = 0

        running = [None] * n_cores
        quantum_counter = [0] * n_cores
        rr_queue = deque()
        arrival_sorted = sorted(ready_queue, key=lambda p: (p.arrival_time, p.pid))
        arrived_idx = 0

        while not all(p.executed for p in ready_queue):
            # 도착한 프로세스 레디큐에 추가
            while arrived_idx < len(arrival_sorted) and arrival_sorted[arrived_idx].arrival_time <= time:
                rr_queue.append(arrival_sorted[arrived_idx])
                arrived_idx += 1

            assigned_pid = set()

            # 할당/선점/종료 처리
            for i, core in enumerate(all_cores):
                proc = running[i]

                # 종료 처리
                if proc and proc.remaining_time <= 0:
                    if proc.finish_time is None:
                        proc.finish_time = time
                    proc.executed = True
                    running[i] = None
                    quantum_counter[i] = 0

                # 타임퀀텀 소진 시 선점
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
                            if p.start_time is None:
                                p.start_time = time
                            rr_queue.remove(p)
                            break

            for i, core in enumerate(all_cores):
                proc = running[i]
                if proc and proc.remaining_time > 0 and quantum_counter[i] > 0:
                    for _ in range(core.performance):
                        if proc.remaining_time > 0 and quantum_counter[i] > 0:
                            proc.remaining_time -= 1
                            quantum_counter[i] -= 1
                            proc.real_burst += 1
                            core.timeline.append((time, proc.pid, 1))
                            core.total_power += core.power_rate
                            if core.is_idle:
                                core.total_power += core.startup_power
                                core.startup_count += 1
                            core.is_idle = False
                else:
                    core.is_idle = True

            # tick 끝나고 종료/선점 처리
            for i, core in enumerate(all_cores):
                proc = running[i]
                if proc:
                    if proc.remaining_time == 0:
                        proc.finish_time = time + 1
                        proc.executed = True
                        running[i] = None
                        quantum_counter[i] = 0
                    elif quantum_counter[i] == 0:
                        rr_queue.append(proc)
                        running[i] = None

            # 모두 idle & 큐 비었으면 다음 도착까지 점프
            if all(r is None for r in running) and not rr_queue and arrived_idx < len(arrival_sorted):
                time = arrival_sorted[arrived_idx].arrival_time
            else:
                time += 1

        # WT, TT, NTT 공식에 따라 계산
        for p in ready_queue:
            p.turn_around_time = p.finish_time - p.arrival_time
            p.waiting_time = p.turn_around_time - p.burst_time
            p.normalized_TT = round(p.turn_around_time / p.burst_time, 2)
