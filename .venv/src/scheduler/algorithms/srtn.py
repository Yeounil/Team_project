#Shortest-Process-Next


class SRTN:
    def schedule(self, ready_queue, cores):
        time = 0
        for p in ready_queue:
            p['remaining_time'] = p['burst_time']

        ready_queue.sort(key=lambda p: p['arrival_time'])
        queue = []

        while ready_queue or queue or any(core.current_process for core in cores):
            # 도착한 프로세스 queue에 추가
            while ready_queue and ready_queue[0]['arrival_time'] <= time:
                queue.append(ready_queue.pop(0))

            queue.sort(key=lambda p: p['remaining_time'])

            for core in cores:
                if core_next_free_time <= time:
                    #한개 코어의 작업이 다 끝나면 선점
                    if core.current_process:
                        queue.append(core.current_process)
                        core.current_process = None

                if queue:
                    process = queue.pop(0)
                    run_time = 1
                    core.timeline.append((time, process['pid'], run_time))
                    process['remaining_time'] -= run_time
                    core_next_free_time = time + run_time

                    if process['remaining_time'] > 0:
                            core.current_process = process
                    else:
                        core.current_process = None

            time += 1