import math
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class FCFS:
    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        cores = pcores + ecores
        ready_queue.sort(key=lambda p: p.arrival_time)

        while not all(process.executed for process in ready_queue): # 프로세스가 모두 실행될 때 까지 반복복

            # 현재시각 기준으로 도착했으나 아직 실행되지 않은 프로세스 리스트
            arrived = [p for p in ready_queue if p.arrival_time <= time and not p.executed]

            # 사용 가능한 코어 리스트
            idle_cores = [core for core in cores if core.next_free_time <= time]

            # 1. 도착한 프로세스가 있고 할당 가능한 코어가 있는 경우🚩 -> 코어에 프로세스 할당 진행
            if arrived and idle_cores:
                for core in idle_cores:
                    if not arrived: # 할당 가능한 코어 수 > 할당 가능한 프로세스 수일 때, 프로세스를 모두 할당하여 arrived에 프로세스가 없을 경우우 반복문을 멈추기 위한 안전장치
                        break
                    process = arrived.pop(0)
                    process.executed = True
                    process.start_time = max(time, process.arrival_time)
                    process.real_burst = math.ceil(process.burst_time / core.performance)
                    process.finish_time = process.start_time + process.real_burst
                    process.waiting_time = process.start_time - process.arrival_time
                    process.turn_around_time = process.finish_time - process.arrival_time
                    process.normalized_TT = round(process.turn_around_time / process.real_burst,2)

                    core.next_free_time = process.finish_time
                    # 전력 계산: 유휴 상태라면 시동 전력 + 동작 전력
                    if core.is_idle:
                        core.total_power += core.startup_power
                    core.is_idle = False
                    core.total_power += core.power_rate * process.real_burst
                    core.timeline.append((process.start_time, process.pid, process.real_burst))

            # 2. 도착한 프로세스가 있고 할당 가능한 코어가 없는 경우🚩 -> 현재 시간을 작동중인 코어들의 next_free_time 중 가장 작은 값으로 이동
            elif arrived and not idle_cores:
                time = min(core.next_free_time for core in cores)

            # 3. 도착한 프로세스가 없고 할당 가능한 코어가 있는 경우🚩 -> 현재 시간을 도착 예정 프로세스들 중에서 가장 근접한 시간으로 이동
            elif not arrived and idle_cores:
                next_arrival = min(
                    (p.arrival_time for p in ready_queue if not p.executed and p.arrival_time > time), # ready_queue에서 아직 실행되지 않았고 현재 시간 이후에 도착하는 프로세스들 중 가장 이른 도착시간을 구함.
                    default=None # 마지막 프로세스라서 이후 도착 예정 프로세스가 없을 경우 None 반환
                )
                if next_arrival is not None: # 반환 값이 None이 아닐 경우 == 도착 예정 프로세스가 있을 경우
                    time = next_arrival # 현재 시간을 다음 프로세스 도착 예정시간으로 변경
                else:
                    break  # 더 이상 도착할 프로세스가 없음

            # 4. 도착한 프로세스가 없고 할당 가능한 코어가 없는 경우🚩
            else:
                next_arrival = min(
                    (p.arrival_time for p in ready_queue if not p.executed and p.arrival_time > time), # ready_queue에서 아직 실행되지 않았고 현재 시간 이후에 도착하는 프로세스들 중 가장 이른 도착시간을 구함.
                    default=float('inf') # 마지막 프로세스라서 이후 도착 예정 프로세스가 없을 경우 무한대 값 반환 (min 비교를 위해 무한대 반환)
                )
                next_core_free = min(core.next_free_time for core in cores) # 가장 먼저 비게 되는 코어가 언제 비는지를 구함
                time = min(next_arrival, next_core_free) # 두 시간을 비교해서 더 이른 시간으로 현재 시간을 이동
