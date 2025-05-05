from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class HRRN:
    def schedule(self, ready_queue, pcores, ecores):
        cores = pcores + ecores
        time = 0
        # 각 프로세스에 executed(실행) 플래그 초기화
        for p in ready_queue:
            p.executed = False

        # 아직 실행되지 않은 모든 프로세스가 실행될 때까지 반복함
        while not all(p.executed for p in ready_queue):
            # 현재 시간까지 도착은 했으나 아직 실행안된  프로세스를 골라냄
            ready = [p for p in ready_queue if p.arrival_time <= time and not p.executed]
            # 만약에 아직 도착한 프로세스가 없다면, time을 1올려 다시 확인
            if not ready:
                time += 1
                continue

            # 남은 프로세스들의 "응답비율((대기시간 + 실행시간)/ 실행시간)" 계산
            for p in ready:
                wait = time - p.arrival_time
                p.response_ratio = (wait + p.burst_time) / p.burst_time
            # "응답비율"이 높은 순으로 정렬함
            ready.sort(key=lambda p: p.response_ratio, reverse=True)
            # 할당 플래그
            assigned = False

            # 각 코어가 놀고 있다면 각 코어마다 프로세스 할당
            for core in cores:
                # 코어가 비어있는지 확인
                if core.next_free_time <= time and ready:
                    # 가장 높은 "응답비율"의 프로세스를 선택
                    proc = ready.pop(0)
                    # 프로세스가 실행되고 있다고 표시함
                    proc.executed = True
                    # 실행시간 = (실행시간 / 성능)의 "반올림" 값
                    if core.core_type == 'P':
                        burst = (proc.burst_time + 1) // 2
                    else:
                        busrt = proc.burst_time
                        
                    # 만약 코어가 놀고 있다가 실행 된다면 시동 전력을 계산함
                    if core.next_free_time < time:
                        core.total_power += core.startup_power
                    core.total_power += core.power_rate * burst

                    start = time
                    finish = start + burst
                    core.timeline.append((start, proc.pid, burst))
                    # 코어가 일을 끝낸 시간을 알려줌. 즉 코어의 다음 빈 시간을 갱신하는 부분
                    core.next_free_time = finish

                    proc.start_time        = start
                    proc.finish_time       = finish
                    proc.waiting_time      = start - proc.arrival_time
                    proc.turn_around_time  = finish - proc.arrival_time
                    proc.normalized_TT     = proc.turn_around_time / proc.burst_time
                    # 할당 플래그
                    assigned = True
            # 할당 플래그로 할당된 프로세스가 없다면 time을 1로 증가 시켜줌
            if not assigned:
                time += 1
