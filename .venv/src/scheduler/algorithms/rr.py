from scheduler.process import Process

class RoundRobin:
    def __init__(self, time_quantum):
        self.time_quantum = time_quantum

    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        all_cores = pcores + ecores

        for p in ready_queue:
            p.remaining_time = p.burst_time
            p.executed = False
            p.start_time = None
            p.finish_time = None

        running = [None] * len(all_cores)
        quantum_counter = [0] * len(all_cores)

 
        arrived = []
        process_queue = sorted(ready_queue, key=lambda p: (p.arrival_time, p.pid))

        while not all(p.executed for p in ready_queue):
            # 현재 시간에 도착한 프로세스 추가
            for p in process_queue:
                if p.arrival_time == time and p not in arrived:
                    arrived.append(p)

            assigned_pid = set()

 
            for i, core in enumerate(all_cores):
                proc = running[i]
                if proc:
                    if proc.remaining_time <= 0:
                        proc.finish_time = time
                        proc.executed = True
                        running[i] = None
                        quantum_counter[i] = 0
                    elif quantum_counter[i] == self.time_quantum:
                        arrived.append(proc)
                        running[i] = None
                        quantum_counter[i] = 0

            for i, core in enumerate(all_cores):
                if running[i] is None:
          
                    candidates = [p for p in arrived if not p.executed and p not in running and p.pid not in assigned_pid and p.remaining_time > 0]
                    if not candidates:
                        core.is_idle = True
                        continue
                    proc = candidates[0]
                    arrived.remove(proc)
                    running[i] = proc
                    quantum_counter[i] = 0
                    assigned_pid.add(proc.pid)
                    if proc.start_time is None:
                        proc.start_time = time
                    if core.is_idle:
                        core.total_power += core.startup_power
                        core.startup_count += 1
                    core.is_idle = False

          
            for i, core in enumerate(all_cores):
                proc = running[i]
                if proc:
                    work = min(core.performance, proc.remaining_time)
                    proc.remaining_time -= work
                    quantum_counter[i] += 1
                    core.total_power += core.power_rate
                    core.timeline.append((time, proc.pid, 1))

         
            for i, core in enumerate(all_cores):
                if running[i] is None and not core.is_idle:
                    core.is_idle = True

            time += 1

           
            if all(core.is_idle for core in all_cores) and not any(p for p in arrived if not p.executed and p.remaining_time > 0):
                next_arrivals = [p.arrival_time for p in process_queue if p.arrival_time > time]
                if next_arrivals:
                    time = min(next_arrivals)

        for p in ready_queue:
            p.turn_around_time = p.finish_time - p.arrival_time
            p.waiting_time = p.turn_around_time - p.burst_time
            p.normalized_TT = round(p.turn_around_time / p.burst_time, 2)
