from collections import deque

class RoundRobin:
    def __init__(self, time_quantum):
        self.time_quantum = time_quantum

    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        all_cores = pcores + ecores

        # 프로세스 초기화
        for p in ready_queue:
            p.remaining_time = p.burst_time
            p.start_time = None
            p.finish_time = None

        # 도착 대기열: 도착 시간 순으로 정렬
        arrival_queue = deque(sorted(ready_queue, key=lambda p: (p.arrival_time, p.pid)))
        rr_queue = deque()
        running = [None] * len(all_cores)
        quantum_counter = [0] * len(all_cores)

        finished_count = 0
        total_processes = len(ready_queue)

        while finished_count < total_processes:
            # 1. 현재 시간에 도착한 프로세스 rr_queue로 이동
            while arrival_queue and arrival_queue[0].arrival_time <= time:
                rr_queue.append(arrival_queue.popleft())

            # 2. 각 코어에 프로세스 할당
            assigned_pid = set()
            for i, core in enumerate(all_cores):
                # 종료된 프로세스 처리 (finish_time은 오직 여기서만 기록!)
                proc = running[i]
                if proc and proc.remaining_time <= 0:
                    if proc.finish_time is None:  # 중복 기록 방지
                        proc.finish_time = time
                        finished_count += 1
                    running[i] = None
                    quantum_counter[i] = 0
                    continue

                # 타임슬라이스 만료
                if proc and quantum_counter[i] >= self.time_quantum:
                    rr_queue.append(proc)
                    running[i] = None
                    quantum_counter[i] = 0

                # 빈 코어에 할당
                if running[i] is None:
                    for idx, cand in enumerate(rr_queue):
                        if cand.pid not in assigned_pid and cand.remaining_time > 0:
                            running[i] = cand
                            quantum_counter[i] = 0
                            assigned_pid.add(cand.pid)
                            if cand.start_time is None:
                                cand.start_time = time
                            if core.is_idle:
                                core.total_power += core.startup_power
                                core.startup_count += 1
                                core.is_idle = False
                            rr_queue.remove(cand)
                            break
                    else:
                        core.is_idle = True

            # 3. 실행
            for i, core in enumerate(all_cores):
                proc = running[i]
                if proc:
                    work = min(core.performance, proc.remaining_time)
                    proc.remaining_time -= work
                    quantum_counter[i] += 1
                    core.total_power += core.power_rate
                    core.timeline.append((time, proc.pid, 1))
                elif core.is_idle is False:
                    core.is_idle = True

          
            if all(r is None for r in running) and not rr_queue and arrival_queue:
                time = arrival_queue[0].arrival_time
            else:
                time += 1

        for p in ready_queue:
            p.turn_around_time = p.finish_time - p.arrival_time
            p.waiting_time = p.turn_around_time - p.burst_time
            p.normalized_TT = round(p.turn_around_time / p.burst_time, 2)
