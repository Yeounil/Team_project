import math
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

# First Come First Served (FCFS)

class FCFS:
    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        cores = pcores + ecores
        ready_queue.sort(key=lambda p: p.arrival_time)  # 입력을 도착순서대로 안할 수도 있나???

        while ready_queue or any(not core.is_idle for core in cores): # 레디큐에 프로세스가 남았거나 or 레디큐가 비었을 때에도 작동중인 코어가 하나라도 있을 경우 계속 반복✅
            # 현재 시간에 도착한 프로세스
            arrived = [p for p in ready_queue if p.arrival_time <= time]
            # 사용 가능한 코어
            free_cores = [c for c in cores if c.next_free_time <= time]

            if not arrived or not free_cores:
                # 다음 도착할 프로세스 중 가장 빠른 도착 시간
                next_arrival = min((p.arrival_time for p in ready_queue), default=float('inf'))  # 레디큐가 비어있을 때 무한대를 통해 도착예정 프로세스가 없다는것을 알림✅
                # 모든 코어 중 가장 빠르게 일을 끝내는 시간
                next_free = min((c.next_free_time for c in cores), default=float('inf'))
                # 다음 도착 or 코어 해제까지 점프
                time = min(next_arrival, next_free) # 타임슬라이스 vs 이벤트 드리븐 시뮬레이션 -> RR은 time을 초단위로 하는게 필수지만 fcfs는 그냥 이벤트 단위로 넘겨도 문제 없나?✅
                continue

            for core in free_cores:
                if not arrived: # 사용 가능 코어가 있지만 & 도착한 프로세스가 없으면 탈출
                    break

                process = arrived.pop(0)
                ready_queue.remove(process)

                process.start_time = time # max(time, process.arrival_time) -> gpt가 time 대신 이렇게 하라는데 차이 없는거 같음
                duration = math.ceil(process.burst_time / core.performance) # 코어별로 성능이 다르기 때문에 종료시간에 차이가 있음
                process.finish_time = process.start_time + duration
                process.waiting_time = process.start_time - process.arrival_time
                process.turn_around_time = process.finish_time - process.arrival_time
                process.normalized_TT = process.turn_around_time / process.burst_time

                # 시동 전력 처리 (1초라도 쉬면 시동 걸기)
                if core.next_free_time < process.start_time:
                    core.total_power += core.startup_power
                    core.startup_count += 1  # startup_count변수 필요없을 듯 한데 확인해보기✅

                # 실행 전력 처리
                core.total_power += core.power_rate * duration

                core.timeline.append((process.start_time, process.pid, duration))
                core.next_free_time = process.finish_time # next_free_time 갱신 필요? 🚩
