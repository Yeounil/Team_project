from scheduler.process import Process

class SPN:
    def schedule(self, ready_queue, pcores, ecores):
        time = 0

        for p in ready_queue:
            p.executed = False

        #모든 프로세스가 실행이 완료될 때까지 실행
        while not all(p.executed for p in ready_queue):
            # 현재 도착한 프로세스 중 burst가 가장 짧은 것 우선
            available = [p for p in ready_queue if p.arrival_time <= time and not p.executed]
            available.sort(key=lambda p: p.burst_time)

            assigned = False

            for core in pcores + ecores:
                if core.next_free_time <= time and available:
                    process = available.pop(0)

                    # P코어는 성능이 더 높아 burst를 반으로 줄임
                    if core.core_type == 'P':
                        burst = (process.burst_time + 1) // 2
                    else:
                        burst = process.burst_time

                    start_time = max(time, process.arrival_time)
                    core.timeline.append((start_time, process.pid, burst))
                    core.next_free_time = start_time + burst
                    process.finish_time = core.next_free_time

                    # 전력 계산
                    core.total_power += core.startup_power + burst * core.power_rate
                    process.waiting_time = start_time - process.arrival_time
                    process.turn_around_time = core.next_free_time - process.arrival_time
                    process.normalized_TT = round(process.turn_around_time / burst, 2)
                    core.startup_count += 1
                    core.is_idle = False

                    process.executed = True
                    assigned = True

            if not assigned:
                time += 1
