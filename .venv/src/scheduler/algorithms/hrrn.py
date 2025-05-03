import math
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class HRRN:

    def schedule(self, ready_queue, pcores, ecores):
        # P와E 코어를 합쳐서 관리
        cores = pcores + ecores
        time = 0
        
        while ready_queue:
            # 다음 도착할 프로세스 중 가장 빠른 도착 시간
            next_arrival = min(p.arrival_time for p in ready_queue)
            # 모든 코어 중 가장 빠르게 일을 끝내는 시간
            next_free = min(c.next_free_time for c in cores)

            # 현재 시간에 도착한 프로세스 선택
            arrived = [p for p in ready_queue if p.arrival_time <= time]
            # 현재 시간에 사용 가능한 코어들만 선택
            free_cores = [c for c in cores if c.next_free_time <= time]

            # 도착한 게 없거나 코어가 전부 사용 중이면 다음 프로세스 도착이나 코어 해제 시간으로 점프
            if not arrived or not free_cores:
                # 두 값 중 더 빠른 값으로 시간 이동
                time = min(next_arrival, next_free)
                continue
            # 응답비율 계산 후 높은 순으로 정렬
            arrived.sort(key=lambda p: ((time - p.arrival_time) + p.burst_time) / p.burst_time, reverse=True)

            for core in free_cores:
                if not arrived:
                    break
                # 가장 높은 응답비율을 가진 프로세스 ready_queue에서 꺼냄
                proc = arrived.pop(0)
                ready_queue.remove(proc)
                start = time
                # 실행시간 = ceil(burst_time / 성능) // ceil은 ()안에 계산한 값 소수점을 반올림하는 함수
                duration = math.ceil(proc.burst_time / core.performance)

                # 시동 전력 처리
                # 코어가 놀고 있다면 시동 전력 추가
                if core.next_free_time < start:
                    core.total_power += core.startup_power

                # 실행 전력 처리 (power_rate * duration)
                core.total_power += core.power_rate * duration

                finish = start + duration
                # 코어 상태를 아무것도 안하고 있는 상태로 갱신
                core.next_free_time = finish
                core.timeline.append((start, proc.pid, duration))

                proc.start_time = start
                proc.finish_time = finish
                proc.waiting_time = start - proc.arrival_time
                proc.turn_around_time = finish - proc.arrival_time
                proc.normalized_TT = proc.turn_around_time / proc.burst_time
