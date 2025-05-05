from scheduler.process import Process  # Process 클래스 임포트

class SRTN:
    def schedule(self, ready_queue, pcores, ecores):
        time = 0
        all_cores = pcores + ecores

        # 초기 설정
        for p in ready_queue:
            p.remaining_time = p.burst_time  # 남은 실행 시간 초기 설정
            p.executed = False               # 프로세스 실행 완료 여부
            p.start_time = None
            p.finish_time = None

        running = [None] * len(all_cores)  # 각 코어에서 실행 중인 프로세스

        # 모든 프로세스가 실행 완료될 때까지 루프
        while not all(p.executed for p in ready_queue):
            # 현재 시간에 도착하고 실행 가능한 프로세스만 필터링
            available = [
                p for p in ready_queue
                if p.arrival_time <= time and not p.executed and p.remaining_time > 0
            ]

            assigned_pid = set()  # 현재 시점에 이미 다른 코어에 할당된 PID (동시 실행 방지)

            # 모든 코어에 대해 순회
            for i, core in enumerate(all_cores):
                # 이전 실행 중이던 프로세스가 끝났다면 정리
                if running[i] and running[i].remaining_time <= 0:
                    p = running[i]
                    p.executed = True
                    p.finish_time = time
                    p.turn_around_time = p.finish_time - p.arrival_time
                    p.waiting_time = p.turn_around_time - p.burst_time
                    p.normalized_TT = round(p.turn_around_time / p.burst_time, 2)
                    running[i] = None  # 해당 코어는 유휴 상태로

                # 후보군 생성(현재 실행 중 프로세스도 포함)
                candidates = available.copy()
                if running[i] and running[i] not in candidates and running[i].remaining_time > 0:
                    candidates.append(running[i])

                # 다른 코어에서 이미 선택된 프로세스는 제외
                candidates = [p for p in candidates if p.pid not in assigned_pid]

                # 실행 가능한 프로세스가 없다면 유휴 처리
                if not candidates:
                    core.is_idle = True
                    continue

                # 남은 시간 기준으로 가장 짧은 프로세스 선택
                candidates.sort(key=lambda p: p.remaining_time)
                next_proc = candidates[0]

                assigned_pid.add(next_proc.pid)  # 이번 시간에 사용 중인 PID로 등록

                # 선점 필요시 실행 교체
                if running[i] != next_proc:
                    running[i] = next_proc  # 교체

                duration = 1  # 단위 시간
                if core.core_type == 'P':
                    next_proc.remaining_time -= 2  # P코어: 2만큼 실행
                else:
                    next_proc.remaining_time -= 1  # E코어: 1만큼 실행

                # 간트차트에 기록
                core.timeline.append((time, next_proc.pid, duration))

                core.total_power += core.power_rate * duration  # 실행 전력
                if core.is_idle:
                    core.total_power += core.startup_power       # 시동 전력
                    core.startup_count += 1
                core.is_idle = False  # 이제 유휴 아님

                # 최초 실행 시각 기록
                if next_proc.start_time is None:
                    next_proc.start_time = time

                # 프로세스 종료 처리
                if next_proc.remaining_time <= 0:
                    next_proc.finish_time = time + duration
                    next_proc.turn_around_time = next_proc.finish_time - next_proc.arrival_time
                    next_proc.waiting_time = next_proc.turn_around_time - next_proc.burst_time
                    next_proc.normalized_TT = round(next_proc.turn_around_time / next_proc.burst_time, 2)
                    next_proc.executed = True
                    running[i] = None

            # 실행하지 못한 코어들은 유휴 상태로 처리
            for i, core in enumerate(all_cores):
                if running[i] is None and core.is_idle is False:
                    core.is_idle = True

            time += 1  # 다음 시간으로 이동
