import math
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class HRRN:
    def schedule(self, ready_queue, pcores, ecores):
        # 모든 코어를 하나의 리스트로 합쳐 관리
        cores = pcores + ecores
        time = 0

        # 각 프로세스에 executed 플래그 초기화
        for proc in ready_queue:
            proc.executed = False

        # 프로세스가 모두 실행될 때까지 반복
        while not all(p.executed for p in ready_queue):
            assigned = False

            # 1) 현재 시각까지 도착했으나 미실행된 작업 수집
            available = [p for p in ready_queue
                         if p.arrival_time <= time and not p.executed]

            # 2) 각 작업의 응답비율 계산
            for proc in available:
                wait = time - proc.arrival_time
                proc.response_ratio = (wait + proc.burst_time) / proc.burst_time

            # 3) 응답비율 높은 순으로 정렬
            available.sort(key=lambda p: p.response_ratio, reverse=True)

            # 4) 여유(core.next_free_time <= time) 코어마다 작업 할당
            for core in cores:
                if not available:
                    break
                if core.next_free_time <= time:
                    # 가장 높은 비율의 프로세스 선택
                    proc = available.pop(0)
                    proc.executed = True
                    assigned = True

                    # 실행시간 = ceil(서비스시간 / 성능)
                    duration = math.ceil(proc.burst_time / core.performance)

                    # 시동 전력 필요 시 추가
                    if core.next_free_time < time:
                        core.total_power += core.startup_power

                    # 실행 전력 누적
                    core.total_power += core.power_rate * duration

                    # 스케줄 기록
                    start = time
                    finish = start + duration
                    core.timeline.append((start, proc.pid, duration))
                    core.next_free_time = finish

                    # 메트릭 기록
                    proc.start_time        = start
                    proc.finish_time       = finish
                    proc.waiting_time      = start - proc.arrival_time
                    proc.turn_around_time  = finish - proc.arrival_time
                    proc.normalized_TT     = proc.turn_around_time / proc.burst_time

            if not assigned:
                time += 1
