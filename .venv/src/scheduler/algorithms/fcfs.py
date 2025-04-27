# First Come First Served (FCFS)

class FCFS:
    def schedule(self, ready_queue, cores):
        time = 0
        ready_queue.sort(key=lambda p: p['arrival_time'])

        while ready_queue:
            for core in cores:
                if not ready_queue:
                    break
                if not core.timeline or core.timeline[-1][0] <= time:
                    process = ready_queue.pop(0)
                    start_time = max(time, process['arrival_time'])
                    core.timeline.append((start_time, process['pid']))
                    time = start_time + process['burst_time']
