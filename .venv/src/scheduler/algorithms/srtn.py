from scheduler.process import Process  # 프로세스 클래스 import

class SRTN:
    def schedule(self, ready_queue, pcores, ecores):
        time = 0  # 현재 시뮬레이션 시간 초기화
        all_cores = pcores + ecores  # 모든 코어를 하나로 통합

        # ── 프로세스 상태 초기화 ──
        for p in ready_queue:
            p.remaining_time = p.burst_time  # 남은 시간 = 초기 burst 시간
            p.executed = False               # 아직 완료되지 않음
            p.start_time = None              # 시작 시간 초기화
            p.finish_time = None             # 종료 시간 초기화

        running = [None] * len(all_cores)  # 각 코어에서 실행 중인 프로세스 저장용

        # ── 모든 프로세스가 완료될 때까지 반복 ──
        while not all(p.executed for p in ready_queue):
            # 현재 시간까지 도착하고 실행할 수 있는 프로세스만 필터링
            available = [
                p for p in ready_queue
                if p.arrival_time <= time and not p.executed and p.remaining_time > 0
            ]
            assigned_pid = set()  # 이 tick 동안 이미 배정된 프로세스의 pid 저장

            for i, core in enumerate(all_cores):
                # 현재 코어에서 실행 중인 프로세스가 끝났다면 종료 처리
                if running[i] and running[i].remaining_time <= 0:
                    p = running[i]
                    p.executed = True
                    running[i] = None

                # 후보군 구성: 현재 available 프로세스 복사
                candidates = available.copy()
                # 현재 실행 중인 프로세스를 후보군에 포함 (선점 가능성 고려)
                if running[i] and running[i] not in candidates and running[i].remaining_time > 0:
                    candidates.append(running[i])

                # 이미 다른 코어에 배정된 프로세스는 제외
                candidates = [p for p in candidates if p.pid not in assigned_pid]
                if not candidates:
                    core.is_idle = True  # 할당 가능한 프로세스가 없으면 유휴 처리
                    continue

                # 남은 실행 시간이 가장 짧은 프로세스 선택
                candidates.sort(key=lambda p: p.remaining_time)
                next_proc = candidates[0]
                assigned_pid.add(next_proc.pid)  # 이 프로세스는 현재 tick에서 사용됨

                # 현재 실행 중인 프로세스와 다르다면 교체(선점)
                if running[i] != next_proc:
                    running[i] = next_proc

                # 실제 실행 시간 단위: 시뮬레이션은 1초 단위로 진행
                exec_time = 1

                next_proc.remaining_time -= core.performance  # P코어는 성능이 2배

                next_proc.real_burst += exec_time  # 실제 실행 tick 기록

                # 간트 차트에 실행 기록 저장
                core.timeline.append((time, next_proc.pid, exec_time))

                was_idle = [core.is_idle for core in all_cores]  # 이전 상태 저장
                if was_idle[i]:  # 유휴였다면 시동 전력 부과
                    core.total_power += core.startup_power

                # 실행 전력 추가
                core.total_power += core.power_rate * exec_time
                core.is_idle = False  # 코어는 이제 유휴 상태 아님

                # 첫 실행이라면 시작 시간 저장
                if next_proc.start_time is None:
                    next_proc.start_time = time

                # 프로세스가 종료되었다면 마무리 처리
                if next_proc.remaining_time <= 0:
                    next_proc.finish_time = time + exec_time
                    next_proc.turn_around_time = next_proc.finish_time - next_proc.arrival_time
                    next_proc.waiting_time = next_proc.turn_around_time - next_proc.real_burst
                    next_proc.normalized_TT = round(next_proc.turn_around_time / next_proc.real_burst, 2)
                    next_proc.executed = True
                    running[i] = None  # 해당 코어 비우기

            time += 1  # 다음 tick(1초)으로 시간 증가
