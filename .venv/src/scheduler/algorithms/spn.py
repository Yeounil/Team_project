#Shortest-Process-Next

class SPN:
    def schedule(self, ready_queue, cores):
        time = 0

        while ready_queue:
            # 도착한 프로세스 중 burst_time이 가장 짧은 프로세스 선택
            available = [p for p in ready_queue if p['arrival_time'] <= time]
            if not available:
                time += 1
                continue

            available.sort(key=lambda p: p['burst_time'])

            for core in cores:
                if not ready_queue:
                    break
                if not core.timeline or core.timeline[-1][0] <= time:
                    process = available.pop(0)
                    ready_queue.remove(process)
                    start_time = max(time, process['arrival_time'])
                    core.timeline.append((start_time, process['pid'], process['burst_time']))
                    time = start_time + process['burst_time']