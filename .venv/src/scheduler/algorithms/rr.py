# Round Robin (RR)

class RoundRobin:
    def __init__(self, quantum):
        self.quantum = quantum

    def schedule(self, ready_queue, cores):
        time = 0
        queue = []
        ready_queue.sort(key=lambda p: p['arrival_time'])

        while ready_queue or queue:
            while ready_queue and ready_queue[0]['arrival_time'] <= time:
                queue.append(ready_queue.pop(0))

            if not queue:
                time += 1
                continue

            for core in cores:
                if not queue:
                    break
                if core.available_at <= time:
                    process = queue.pop(0)
                    start_time = time
                    run_time = min(self.quantum, process['burst_time'])
                    core.timeline.append((start_time, process['pid'], run_time))
                    process['burst_time'] -= run_time
                    core.available_at = start_time + run_time
                    if process['burst_time'] > 0:
                        process['arrival_time'] = core.available_at
                        queue.append(process)
            time += 1
                        # 아직 남은 시간 있으면 다시 큐에 넣음
                        process['arrival_time'] = time
                        queue.append(process)
