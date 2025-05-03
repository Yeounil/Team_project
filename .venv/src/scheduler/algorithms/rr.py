from collections import deque

class RoundRobinScheduler:
    def __init__(self, time_quantum):
        self.time_quantum = time_quantum
        self.total_power = 0

    def schedule(self, ready_queue, cores):
        time = 0
        process_queue = deque(sorted(ready_queue, key=lambda p: p.arrival_time))
        waiting_queue = deque()
        finished = set()
        quantum_counter = {core.core_id: 0 for core in cores}
        while process_queue and process_queue[0].arrival_time > time:
            for core in cores:
                core.timeline.append((time, 'idle'))
            time += 1
        while len(finished) < len(ready_queue):
            while process_queue and process_queue[0].arrival_time <= time:
                waiting_queue.append(process_queue.popleft())
            for core in cores:
                if core.current_process is None and waiting_queue:
                    proc = waiting_queue.popleft()
                    core.current_process = proc
                    quantum_counter[core.core_id] = 0
                    if proc.start_time is None:
                        proc.start_time = time
                    if core.is_idle:
                        self.total_power += core.startup_power
                        core.startup_count += 1
                        core.is_idle = False
            for core in cores:
                proc = core.current_process
                if proc is not None:
                    work = min(core.performance, proc.remaining_time)
                    proc.remaining_time -= work
                    core.used_time += 1
                    quantum_counter[core.core_id] += 1
                    self.total_power += core.power_rate
                    core.timeline.append((time, proc.pid))
                    if proc.remaining_time <= 0:
                        proc.finish_time = time + 1
                        proc.turn_around_time = proc.finish_time - proc.arrival_time
                        proc.waiting_time = proc.turn_around_time - proc.burst_time
                        proc.normalized_TT = proc.turn_around_time / proc.burst_time
                        finished.add(proc)
                        core.current_process = None
                        quantum_counter[core.core_id] = 0
                        core.is_idle = True
                    elif quantum_counter[core.core_id] == self.time_quantum:
                        proc.arrival_time = time + 1
                        waiting_queue.append(proc)
                        core.current_process = None
                        quantum_counter[core.core_id] = 0
                        core.is_idle = True
                else:
                    core.timeline.append((time, 'idle'))
                    core.is_idle = True
            time += 1
            if all(core.current_process is None for core in cores) and not waiting_queue and process_queue:
                next_arrival = process_queue[0].arrival_time
                while time < next_arrival:
                    for core in cores:
                        core.timeline.append((time, 'idle'))
                    time += 1
                continue
