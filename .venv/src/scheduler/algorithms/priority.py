import math
from typing import List
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class Priority:
    def schedule(self, ready_queue: List[Process], pcores: List[Core], ecores: List[Core]):
        cores = pcores + ecores
        time = 0

        avg_burst = sum(p.burst_time for p in ready_queue) / len(ready_queue)

        p_queue = [p for p in ready_queue if p.burst_time >= avg_burst]
        e_queue = [p for p in ready_queue if p.burst_time <  avg_burst]

        for p in ready_queue:
            p.executed = False

        while p_queue or e_queue:
            assigned = False

            free_cores = [c for c in cores if c.next_free_time <= time]
            available_tasks = [p for p in (p_queue + e_queue) if p.arrival_time <= time]

            if not free_cores or not available_tasks:
                next_events = []
                next_events.extend([c.next_free_time for c in cores if c.next_free_time > time])

                next_events.extend([p.arrival_time for p in (p_queue + e_queue) if p.arrival_time > time])
                if not next_events:
                    break
                time = min(next_events)
                continue

            for core in free_cores:
                proc = None
                if core.core_type == 'P':
                    for p in p_queue:
                        if p.arrival_time <= time:
                            proc = p
                            p_queue.remove(p)
                            break
                else:
                    for p in e_queue:
                        if p.arrival_time <= time:
                            proc = p
                            e_queue.remove(p)
                            break
                    if proc is None:
                        for p in p_queue:
                            if p.arrival_time <= time:
                                soonest_p = min(c.next_free_time for c in pcores)
                                if (soonest_p - time) >= p.burst_time:
                                    proc = p
                                    p_queue.remove(p)
                                break

                if proc is None:
                    continue

                assigned = True
                start = time
                core.timeline.append((start, proc.pid))
                duration = math.ceil(proc.burst_time / 2) if core.core_type == 'P' else proc.burst_time
                proc.start_time = start
                proc.finish_time = start + duration
                proc.executed = True
                core.next_free_time = proc.finish_time

            if not assigned:
                future_times = [c.next_free_time for c in cores if c.next_free_time > time]
                if future_times:
                    time = min(future_times)
                else:
                    break
