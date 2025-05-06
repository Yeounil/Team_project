from collections import deque
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class RoundRobin:
    def __init__(self, quantum=2):
        self.quantum = quantum

    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        all_cores = pcores + ecores
        n_cores = len(all_cores)

        # 프로세스 초기화
        for p in ready_queue:
            p.remaining_time = p.burst_time
            p.start_time = None
            p.finish_time = None
            p.executed = False
            p.real_burst = 0

        running = [None] * n_cores
        quantum_counter = [0] * n_cores
        rr_queue = deque()
        arrival_sorted = sorted(ready_queue, key=lambda p: (p.arrival_time, p.pid))
        arrived_idx = 0

        while not all(p.executed for p in ready_queue):
            # 도착 프로세스 추가
            while arrived_idx < len(arrival_sorted) and arrival_sorted[arrived_idx].arrival_time <= time:
                rr_queue.append(arrival_sorted[arrived_idx])
                arrived_idx += 1

            assigned_pid = set()

            # 코어별 종료/선점/재할당
            for i, core in enumerate(all_cores):
                proc = running[i]

                if proc and proc.remaining_time <= 0:
                    proc.finish_time = time
                    proc.executed = True
                    running[i] = None
                    quantum_counter[i] = 0

                elif proc and quantum_counter[i] <= 0:
                    rr_queue.append(proc)
                    running[i] = None

                if running[i] is None:
                    for p in rr_queue:
                        if not p.executed and p.pid not in assigned_pid and p.remaining_time > 0:
                            running[i] = p
                            quantum_counter[i] = self.quantum
                            assigned_pid.add(p.pid)
                            rr_queue.remove(p)
                            break

            # 실행 처리: 각 코어는 1 tick 동안 성능만큼 수행
            for i, core in enumerate(all_cores):
                proc = running[i]
                if proc and proc.remaining_time > 0 and quantum_counter[i] > 0:
                    if proc.start_time is None:
                        proc.start_time = time

                    if(core.core_type == 'P'):
                        work = 2
                    else:
                        work = 1

                    proc.remaining_time -= work
                    proc.real_burst += 1  # 실제로 이 코어가 1 tick 동안 사용됨
                    core.timeline.append((time, proc.pid, self.quantum))
                    core.total_power += core.power_rate
                    if core.is_idle:
                        core.total_power += core.startup_power
                        core.startup_count += 1
                    core.is_idle = False

                    if proc.remaining_time <= 0:
                        proc.finish_time = time + 1
                        proc.executed = True
                        running[i] = None
                        quantum_counter[i] = 0
                        proc.turn_around_time = proc.finish_time - proc.arrival_time
                        proc.waiting_time = proc.turn_around_time - proc.real_burst
                        proc.normalized_TT = round(proc.turn_around_time / proc.real_burst, 2)

                else:
                    core.is_idle = True

            # 시간 이동
            if all(r is None for r in running) and not rr_queue and arrived_idx < len(arrival_sorted):
                time = arrival_sorted[arrived_idx].arrival_time
            else:
                time += 1

