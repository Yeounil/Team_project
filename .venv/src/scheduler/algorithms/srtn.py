from scheduler.process import Process

class SRTN:
    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        all_cores = pcores + ecores

        # 초기화
        for p in ready_queue:
            p.remaining_time = p.burst_time
            p.executed = False
            p.start_time = None
            p.finish_time = None

        running = [None] * len(all_cores)  # 각 코어의 현재 실행 중 프로세스

        while not all(p.executed for p in ready_queue):
            # 현재 시간까지 도착한 프로세스 중 실행 가능한 것
            available = [p for p in ready_queue if p.arrival_time <= time and not p.executed and p.remaining_time > 0]
            assigned_pid = set()

            for i, core in enumerate(all_cores):
                # 이전 프로세스 종료 확인
                if running[i] and running[i].remaining_time <= 0:
                    p = running[i]
                    p.executed = True
                    p.finish_time = time
                    p.turn_around_time = p.finish_time - p.arrival_time
                    p.waiting_time = p.start_time - p.arrival_time  # 정확한 WT
                    p.normalized_TT = round(p.turn_around_time / p.burst_time, 2)
                    running[i] = None

                # 후보군 구성
                candidates = available.copy()
                if running[i] and running[i] not in candidates and running[i].remaining_time > 0:
                    candidates.append(running[i])

                # 다른 코어에서 이미 할당된 프로세스 제외
                candidates = [p for p in candidates if p.pid not in assigned_pid]
                if not candidates:
                    core.is_idle = True
                    continue

                # 남은 시간 기준 정렬
                candidates.sort(key=lambda p: p.remaining_time)
                next_proc = candidates[0]
                assigned_pid.add(next_proc.pid)

                if running[i] != next_proc:
                    running[i] = next_proc  # 선점

                # 실제 실행 (1초 단위 시뮬레이션)
                exec_time = 1
                if core.core_type == 'P':
                    next_proc.remaining_time -= 2
                    burst = (next_proc.burst_time + 1) // 2
                else:
                    next_proc.remaining_time -= 1
                    burst = next_proc.burst_time

                # Gantt 차트용 기록
                core.timeline.append((time, next_proc.pid, exec_time))

                # 전력 계산
                core.total_power += core.power_rate * exec_time
                if core.is_idle:
                    core.total_power += core.startup_power
                    core.startup_count += 1
                core.is_idle = False

                if next_proc.start_time is None:
                    next_proc.start_time = time

                # 프로세스 종료 조건 다시 확인
                if next_proc.remaining_time <= 0:
                    next_proc.finish_time = time + exec_time
                    next_proc.turn_around_time = next_proc.finish_time - next_proc.arrival_time
                    next_proc.waiting_time = next_proc.start_time - next_proc.arrival_time
                    next_proc.normalized_TT = round(next_proc.turn_around_time / burst, 2)
                    next_proc.executed = True
                    running[i] = None

            # 실행하지 못한 코어들은 유휴 상태로 전환
            for i, core in enumerate(all_cores):
                if running[i] is None and core.is_idle is False:
                    core.is_idle = True

            time += 1
