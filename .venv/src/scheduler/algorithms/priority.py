# Priority Scheduling (작은 priority 숫자가 높은 우선순위)

class Priority:
    def schedule(self, ready_queue, cores):
        time = 0

        while ready_queue:
            available = [p for p in ready_queue if p['arrival_time'] <= time]
            if not available:
                time += 1
                continue

            # priority라는 필드가 있어야 함 (필요시 UI에 입력 추가해야 함)
            available.sort(key=lambda p: p['priority'])

            for core in cores:
                if not ready_queue:
                    break
                if not core.timeline or core.timeline[-1][0] <= time:
                    process = available.pop(0)
                    ready_queue.remove(process)
                    start_time = max(time, process['arrival_time'])
                    core.timeline.append((start_time, process['pid']))
                    time = start_time + process['burst_time']
