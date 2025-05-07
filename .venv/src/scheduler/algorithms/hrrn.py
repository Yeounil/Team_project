from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class HRRN:
    def schedule(self, ready_queue, pcores, ecores):
        cores = pcores + ecores
        time  = 0
        # 프로세스 정보 초기화
        for p in ready_queue:
            p.executed = False
            p.start_time = None
            p.finish_time = None
            p.waiting_time = None
            p.turn_around_time = None
            p.normalized_TT = None
        # 코어 정보 초기화
        for core in cores:
            core.next_free_time = 0
            core.is_idle = True

        # 아직 실행되지 않은 모든 프로세스가 실행될 때까지 반복함
        while not all(p.executed for p in ready_queue):
            # 현재 시간까지 도착은 했으나 아직 실행안된  프로세스를 골라냄
            ready = [p for p in ready_queue if p.arrival_time <= time and not p.executed]

            # 만약에 아직 도착한 프로세스가 없다면, 다음 프로세스 도착 또는 완료까지 time을 올려 다시 확인
            if not ready:
                # 다음에 도착할 프로세스 시간
                next_arr = min((p.arrival_time for p in ready_queue if not p.executed and p.arrival_time > time), default=float('inf'))
                # 다음으로 끝나는 코어 시간
                next_core = min((c.next_free_time for c in cores if c.next_free_time > time), default=float('inf'))
                time = min(next_arr, next_core)
                continue

            # 남은 프로세스들의 "응답비율((대기시간 + 실행시간)/ 실행시간)" 계산
            for p in ready:
                wait = time - p.arrival_time
                p.rr = (wait + p.burst_time) / p.burst_time
            ready.sort(key=lambda p: p.rr, reverse=True)

            for core in cores:
                # 코어가 비어있는지 확인
                if core.next_free_time <= time and ready:
                    proc = ready.pop(0)
                    proc.executed = True
                    proc.start_time = time
                    proc.waiting_time = time - proc.arrival_time

                    if core.core_type == 'P':
                        burst = (proc.burst_time + 1) // 2
                    else:
                        burst = proc.burst_time
                    finish = time + burst

                    # 시동 전력
                    if core.is_idle:
                        core.total_power += core.startup_power
                        core.is_idle = False

                    # 실행 전력: 동작 시간만 측정함
                    core.total_power += core.power_rate * burst

                    core.timeline.append((time, proc.pid, burst))
                    core.next_free_time = finish

                    proc.finish_time = finish
                    proc.turn_around_time = finish - proc.arrival_time
                    proc.normalized_TT = proc.turn_around_time / burst

            # 다음 프로세스로 time 증가
            next_arr = min((p.arrival_time for p in ready_queue if not p.executed and p.arrival_time > time), default=float('inf'))
            next_fin = min((c.next_free_time for c in cores if c.next_free_time > time), default=float('inf'))
            time = min(next_arr, next_fin)
