import math
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class FCFS:
    def schedule(self, ready_queue, pcores, ecores):
        # P/E 코어 풀
        cores = pcores + ecores
        time = 0

        # 각 프로세스 실행 여부 초기화
        for proc in ready_queue:
            proc.executed = False

        # 모든 프로세스가 완료될 때까지 반복
        while not all(proc.executed for proc in ready_queue):
            assigned = False

            # 현재 시각까지 도착했으나 아직 실행되지 않은 프로세스 리스트
            available = [p for p in ready_queue
                         if p.arrival_time <= time and not p.executed]
            # FCFS: 도착순 정렬
            available.sort(key=lambda p: p.arrival_time)

            # 여유 코어에 순서대로 할당
            for core in cores:

                if core.next_free_time <= time and available:
                    proc = available.pop(0)
                    proc.executed = True
                    assigned = True

                    # 실행 시간 (초)
                    duration = math.ceil(proc.burst_time / core.performance)

                    # 시동 전력
                    if core.next_free_time < time:
                        core.total_power += core.startup_power

                    # 실행 전력
                    core.total_power += core.power_rate * duration

                    # 코어 일정 기록
                    start = time
                    finish = start + duration
                    core.timeline.append((start, proc.pid, duration))
                    core.next_free_time = finish

                    # 프로세스 메트릭 기록
                    proc.start_time       = start
                    proc.finish_time      = finish
                    proc.waiting_time     = start - proc.arrival_time
                    proc.turn_around_time = finish - proc.arrival_time
                    proc.normalized_TT    = proc.turn_around_time / proc.burst_time

            # 할당하지 못했으면 시간 1초 증가
            if not assigned:
                time += 1
