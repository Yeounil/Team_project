from scheduler.process import Process
import math

class SPN:
    def schedule(self, ready_queue, pcores, ecores):
        time = 0

        #모든 프로세스가 실행이 완료될 때까지 실행, 한 번이라도 실행한 프로세스는 제외
        while not all(p.executed for p in ready_queue):
            # 현재 도착한 프로세스 중 burst가 가장 짧은 것 우선순위 정렬
            available = [p for p in ready_queue if p.arrival_time <= time and not p.executed]
            available.sort(key=lambda p: p.burst_time)

            assigned = False

            for core in pcores + ecores:
                #코어가 현재 실행이 끝난 상태 and 실행할 프로세스가 있을 때
                if core.next_free_time <= time and available:
                    if core.next_free_time < time:
                        core.is_idle = True

                    process = available.pop(0)
                    # P코어 성능에 따른 실제 burst time 계산
                    process.real_burst = math.ceil(process.burst_time / core.performance)
                    process.start_time = max(time, process.arrival_time) # 시작 시간 저장
                    core.timeline.append((process.start_time, process.pid, process.real_burst)) #core.timeline에 프로세스 정보 저장
                    core.next_free_time = process.start_time + process.real_burst # 코어가 일이 끝나는 시간 저장
                    process.finish_time = core.next_free_time # 프로세스 정보에 일이 끝나는 시간 정의

                    if core.is_idle:
                       core.total_power += core.startup_power
                       core.is_idle = False
                    # 전력 계산
                    core.total_power += process.real_burst * core.power_rate
                    process.waiting_time = process.start_time - process.arrival_time
                    process.turn_around_time = core.next_free_time - process.arrival_time
                    process.normalized_TT = round(process.turn_around_time / process.real_burst, 2)
                    process.executed = True
                    assigned = True

            if not assigned:
                time += 1
