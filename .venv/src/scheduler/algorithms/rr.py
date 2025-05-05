from scheduler.process import Process
from collections import deque

class RoundRobin:
    def __init__(self, quantum=2):
        self.quantum = quantum

    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        all_cores = pcores + ecores

        # 초기화
        for p in ready_queue:
            p.remaining_time = p.burst_time
            p.executed = False
            p.start_time = None
            p.finish_time = None
            p.real_burst = 0

        process_queue = deque(sorted(ready_queue, key=lambda p: p.arrival_time))
        waiting_queue = deque()
        running = [None] * len(all_cores)
        quantum_counter = [0] * len(all_cores)

        while not all(p.executed for p in ready_queue):
            # 도착한 프로세스 waiting_queue에 추가
            while process_queue and process_queue[0].arrival_time <= time:
                waiting_queue.append(process_queue.popleft())

            for i, core in enumerate(all_cores):
                current_proc = running[i]

                # 실행 중인 프로세스가 없거나 Quantum을 다 썼다면 새로 할당
                if (current_proc is None or quantum_counter[i] <= 0 or current_proc.remaining_time <= 0) and waiting_queue:
                    # 이전 프로세스 처리 완료
                    if current_proc and current_proc.remaining_time <= 0:
                        current_proc.finish_time = time
                        current_proc.turn_around_time = current_proc.finish_time - current_proc.arrival_time
                        current_proc.waiting_time = current_proc.turn_around_time - current_proc.burst_time
                        current_proc.normalized_TT = round(current_proc.turn_around_time / current_proc.burst_time, 2)
                        current_proc.executed = True
                        running[i] = None

                    # quantum 안 끝났지만 선점된 경우 다시 waiting_queue로
                    elif current_proc and current_proc.remaining_time > 0:
                        waiting_queue.append(current_proc)
                        running[i] = None

                    # 새 프로세스 할당
                    if waiting_queue:
                        proc = waiting_queue.popleft()
                        if proc.start_time is None:
                            proc.start_time = time
                        running[i] = proc
                        quantum_counter[i] = self.quantum

                        # 전력 및 부팅 비용
                        if core.is_idle:
                            core.total_power += core.startup_power
                            core.startup_count += 1
                        core.is_idle = False

                # 실행
                current_proc = running[i]
                if current_proc:
                    quantum_counter[i] -= 1
                    exec_unit = 2 if core.core_type == 'P' else 1
                    current_proc.remaining_time -= exec_unit
                    current_proc.real_burst += 1

                    core.timeline.append((time, current_proc.pid, 1))
                    core.total_power += core.power_rate

                    # 종료
                    if current_proc.remaining_time <= 0:
                        current_proc.finish_time = time + 1
                        current_proc.turn_around_time = current_proc.finish_time - current_proc.arrival_time
                        current_proc.waiting_time = current_proc.turn_around_time - current_proc.burst_time
                        current_proc.normalized_TT = round(current_proc.turn_around_time / current_proc.burst_time, 2)
                        current_proc.executed = True
                        running[i] = None
                        quantum_counter[i] = 0

            for i, core in enumerate(all_cores):
                if running[i] is None:
                    core.is_idle = True

            time += 1
