from collections import deque

class RoundRobin:
    def __init__(self, time_quantum):
        self.time_quantum = time_quantum

    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        all_cores = pcores + ecores
        process_queue = deque(sorted(ready_queue, key=lambda p: (p.arrival_time, p.pid)))
        waiting_queue = deque()
        finished = set()
        quantum_counter = {core.core_id: 0 for core in all_cores}

        while len(finished) < len(ready_queue):
            # 도착한 프로세스 waiting_queue에 추가
            while process_queue and process_queue[0].arrival_time <= time:
                waiting_queue.append(process_queue.popleft())

            # 각 코어가 비어있으면 프로세스 할당
            for core in all_cores:
                if core.current_process is None and waiting_queue:
                    proc = waiting_queue.popleft()
                    core.current_process = proc
                    quantum_counter[core.core_id] = 0
                    if proc.start_time is None:
                        proc.start_time = time
                    if core.is_idle:
                        core.total_power += core.startup_power
                        core.startup_count += 1
                        core.is_idle = False

            did_work = False
            for core in all_cores:
                proc = core.current_process
                if proc is not None:
                    # P코어 2, E코어 1만큼 처리
                    work = min(core.performance, proc.remaining_time)
                    proc.remaining_time -= work
                    quantum_counter[core.core_id] += 1
                    core.total_power += core.power_rate
                    core.timeline.append((time, proc.pid, 1))
                    did_work = True

                    # 프로세스가 끝났을 때
                    if proc.remaining_time <= 0:
                        proc.finish_time = time + 1
                        proc.turn_around_time = proc.finish_time - proc.arrival_time
                        proc.waiting_time = proc.turn_around_time - proc.burst_time
                        proc.normalized_TT = proc.turn_around_time / proc.burst_time
                        finished.add(proc)
                        core.current_process = None
                        quantum_counter[core.core_id] = 0
                        core.is_idle = True

                    # 타임퀀텀 끝나면 프로세스 다시 waiting_queue 뒤로
                    elif quantum_counter[core.core_id] == self.time_quantum:
                        proc.arrival_time = time + 1
                        waiting_queue.append(proc)
                        core.current_process = None
                        quantum_counter[core.core_id] = 0
                        core.is_idle = True

            time += 1

            # 아무 일도 안 한 경우(모든 코어 idle)에는 time을 다음 프로세스 도착 시각으로 점프
            if not did_work and not waiting_queue and process_queue:
                next_arrival = process_queue[0].arrival_time
                time = next_arrival
