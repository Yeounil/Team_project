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

        for core in all_cores:
            core.current_process = None
            core.timeline = []
            core.next_free_time = 0
            core.is_idle = True
            core.total_power = 0
            core.startup_count = 0

        for proc in ready_queue:
            proc.remaining_time = proc.burst_time
            proc.start_time = None
            proc.waiting_time = 0
            proc.finish_time = None

        last_leave_time = {p.pid: p.arrival_time for p in ready_queue}

        while len(finished) < len(ready_queue):
            while process_queue and process_queue[0].arrival_time <= time:
                waiting_queue.append(process_queue.popleft())

            
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
                  
                    if last_leave_time[proc.pid] < time:
                        proc.waiting_time += time - last_leave_time[proc.pid]

         
            for core in all_cores:
                proc = core.current_process
                if proc is not None:
                    work = min(core.performance, proc.remaining_time)
                    proc.remaining_time -= work
                    quantum_counter[core.core_id] += 1
                    core.total_power += core.power_rate
                    core.timeline.append((time, proc.pid, 1))

                 
                    if proc.remaining_time <= 0:
                        proc.finish_time = time + 1
                        finished.add(proc)
                        core.current_process = None
                        core.is_idle = True
                        quantum_counter[core.core_id] = 0
                        last_leave_time[proc.pid] = time + 1
                    
                    elif quantum_counter[core.core_id] == self.time_quantum:
                        waiting_queue.append(proc)
                        core.current_process = None
                        core.is_idle = True
                        quantum_counter[core.core_id] = 0
                        last_leave_time[proc.pid] = time + 1

            time += 1

            if all(core.is_idle for core in all_cores) and not waiting_queue and process_queue:
                time = process_queue[0].arrival_time

        for proc in ready_queue:
            proc.turn_around_time = proc.finish_time - proc.arrival_time
            proc.normalized_TT = proc.turn_around_time / proc.burst_time

        for core in all_cores:
            core.current_process = None
