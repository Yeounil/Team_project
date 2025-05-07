from collections import deque
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class RoundRobin:
    def __init__(self, quantum=2):
        self.quantum = quantum  # RR 타임퀀텀 값 설정

    def schedule(self, ready_queue, pcores, ecores):
        time       = 0
        all_cores  = pcores + ecores
        n_cores    = len(all_cores)

        for p in ready_queue:
            p.remaining_time = p.burst_time
            p.real_burst     = 0
            p.start_time     = None
            p.finish_time    = None
            p.executed       = False

        running         = [None] * n_cores
        quantum_counter = [0]    * n_cores
        rr_queue        = deque()
        arrival_sorted  = sorted(ready_queue, key=lambda p: (p.arrival_time, p.pid))
        arrived_idx     = 0

        while not all(p.executed for p in ready_queue):
            while arrived_idx < len(arrival_sorted) and arrival_sorted[arrived_idx].arrival_time <= time:
                rr_queue.append(arrival_sorted[arrived_idx])
                arrived_idx += 1

            assigned_pid = set()

            for i, core in enumerate(all_cores):
                proc = running[i]

                if proc and proc.remaining_time <= 0:
                    if proc.finish_time is None:
                        proc.finish_time = time + 1
                    proc.executed = True
                    running[i] = None
                    quantum_counter[i] = 0

                elif proc and quantum_counter[i] <= 0 and proc.remaining_time > 0:
                    rr_queue.append(proc)
                    running[i] = None

                if running[i] is None and rr_queue:
                    for p in rr_queue:
                        if not p.executed and p.pid not in assigned_pid:
                            running[i] = p
                            quantum_counter[i] = self.quantum
                            assigned_pid.add(p.pid)
                            rr_queue.remove(p)
                            if p.start_time is None:
                                p.start_time = time
                            break

            for i, core in enumerate(all_cores):
                proc = running[i]

                if not proc:
                    core.is_idle = True
                    continue

                if proc.remaining_time <= 0 or quantum_counter[i] <= 0:
                    continue

                work = min(core.performance, proc.remaining_time)
                proc.remaining_time -= work
                proc.real_burst     += 1
                quantum_counter[i]  -= 1

                for _ in range(work):
                    core.timeline.append((time, proc.pid, 1))

                if core.is_idle:
                    core.total_power += core.startup_power
                    core.is_idle = False
                core.total_power += core.power_rate * work

                if proc.remaining_time == 0 and proc.finish_time is None:
                    proc.finish_time = time + 1
                    proc.executed = True
                    running[i] = None
                    quantum_counter[i] = 0

            if all(r is None for r in running) and not rr_queue and arrived_idx < len(arrival_sorted):
                time = arrival_sorted[arrived_idx].arrival_time
            else:
                time += 1

        for p in ready_queue:
            if p.finish_time is None:
                p.finish_time = time
            if p.start_time is None:
                p.start_time = p.arrival_time

            p.turn_around_time = p.finish_time - p.arrival_time
            p.waiting_time     = p.turn_around_time - p.real_burst
            p.normalized_TT    = round(p.turn_around_time / p.real_burst, 2)
