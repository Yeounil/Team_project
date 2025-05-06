from scheduler.process import Process

class NPriority:
    def schedule(self, ready_queue, pcores, ecores):
        time = 0

        # 프로세스 초기화
        for p in ready_queue:
            p.executed = False
            p.priority = getattr(p, 'priority', 14)
            p.original_priority = p.priority  # 에이징 적용 전 원래 우선순위

        while not all(p.executed for p in ready_queue):
            # Aging: 대기 중인 프로세스의 우선순위 보정 (1마다 우선순위 1씩 상승)
            for p in ready_queue:
                if not p.executed and p.arrival_time <= time:
                    waited = time - p.arrival_time
                    # 1마다 우선순위 1씩 상승(값 감소, 최소 0까지)
                    p.priority = max(0, p.original_priority - waited)

            # 현재 도착한 미실행 프로세스 중 (우선순위, burst time 긴 것 우선) 정렬
            available = [p for p in ready_queue if p.arrival_time <= time and not p.executed]
            available.sort(key=lambda p: (p.priority, -p.burst_time))

            assigned = False

            for core in pcores + ecores:
                if core.next_free_time <= time and available:
                    process = available.pop(0)

                    # P코어는 burst time 절반(올림), E코어는 그대로
                    if core.core_type == 'P':
                        burst = (process.burst_time + 1) // 2
                    else:
                        burst = process.burst_time

                    start_time = max(time, process.arrival_time)
                    core.timeline.append((start_time, process.pid, burst))
                    core.next_free_time = start_time + burst
                    process.finish_time = core.next_free_time

                    # 전력 및 실행 통계
                    core.total_power += core.startup_power + burst * core.power_rate
                    core.startup_count += 1

                    process.waiting_time = start_time - process.arrival_time
                    process.turn_around_time = process.finish_time - process.arrival_time
                    process.normalized_TT = round(process.turn_around_time / process.burst_time, 2)
                    process.executed = True

                    assigned = True

            # 할당에 실패했다면, 다음 도착 프로세스 시간으로 점프
            if not assigned:
                future_arrivals = [p.arrival_time for p in ready_queue if not p.executed and p.arrival_time > time]
                if future_arrivals:
                    time = min(future_arrivals)
                else:
                    time += 1
