from collections import deque
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class RoundRobin:
    def __init__(self, quantum=2):
        self.quantum = quantum  # RR 타임퀀텀 값 설정

    def schedule(self, ready_queue, pcores, ecores):
        time       = 0  # 전체 시뮬레이션 시간
        all_cores  = pcores + ecores  # 전체 코어 묶기
        n_cores    = len(all_cores)

        # ── 1) 프로세스 상태 초기화 ──
        for p in ready_queue:
            p.remaining_time = p.burst_time  # 남은 실행시간
            p.real_burst     = 0             # 실제 수행된 tick 수
            p.start_time     = None          # 처음 실행된 시간
            p.finish_time    = None          # 종료된 시간
            p.executed       = False         # 완료 여부

        # ── 2) 스케줄러 상태용 변수 선언 ──
        running         = [None] * n_cores       # 각 코어에서 현재 실행 중인 프로세스
        quantum_counter = [0]    * n_cores       # 각 코어의 RR 퀀텀 카운터
        rr_queue        = deque()                # 준비 큐: RR 방식의 대기열
        arrival_sorted  = sorted(ready_queue, key=lambda p: (p.arrival_time, p.pid))  # 도착 순 정렬
        arrived_idx     = 0                      # 도착 큐 인덱스

        # ── 3) 메인 스케줄링 루프 ──
        while not all(p.executed for p in ready_queue):

            # 3-a) 현재 시간에 도착한 프로세스들을 큐에 추가
            while arrived_idx < len(arrival_sorted) and \
                  arrival_sorted[arrived_idx].arrival_time <= time:
                rr_queue.append(arrival_sorted[arrived_idx])
                arrived_idx += 1

            assigned_pid = set()  # 중복 실행 방지용 PID 저장

            # 3-b) 코어별 상태 갱신
            for i, core in enumerate(all_cores):
                proc = running[i]

                # 종료 처리
                if proc and proc.remaining_time <= 0:
                    if proc.finish_time is None:
                        proc.finish_time = time + 1
                    proc.executed      = True
                    running[i]         = None
                    quantum_counter[i] = 0

                # 타임 퀀텀 소진: 대기열로 복귀
                elif proc and quantum_counter[i] <= 0 and proc.remaining_time > 0:
                    rr_queue.append(proc)
                    running[i]         = None

                # 코어가 비어있고 대기열이 있으면 새로 할당
                if running[i] is None and rr_queue:
                    for idx, p in enumerate(rr_queue):
                        if (not p.executed) and (p.pid not in assigned_pid):
                            running[i]         = p
                            quantum_counter[i] = self.quantum
                            assigned_pid.add(p.pid)
                            rr_queue.remove(p)
                            # 최초 실행 시간 기록
                            if p.start_time is None:
                                p.start_time = time
                            break

            # 3-c) 실제 실행 단계
            for i, core in enumerate(all_cores):
                proc = running[i]
                # 실행 조건: 실행 가능한 프로세스가 있고 퀀텀이 남아야 함
                if not proc or proc.remaining_time <= 0 or quantum_counter[i] <= 0:
                    core.is_idle = True
                    continue

                # 코어 성능에 따라 처리할 작업량 계산 (P코어: 2, E코어: 1)
                work = min(core.performance, proc.remaining_time)
                proc.remaining_time -= work              # 남은 실행시간 차감
                proc.real_burst     += 1                 # 실제 tick 수 증가
                quantum_counter[i]  -= 1                 # 퀀텀 차감

                # Gantt 차트용 실행 기록: 1초 단위로 기록
                for _ in range(work):
                    core.timeline.append((time, proc.pid, 1))

                # 전력 계산
                if core.is_idle:
                    core.total_power   += core.startup_power
                    core.startup_count += 1
                    core.is_idle        = False
                core.total_power += core.power_rate * work

                # 종료 처리
                if proc.remaining_time == 0 and proc.finish_time is None:
                    proc.finish_time = time + 1
                    proc.executed    = True
                    running[i]       = None
                    quantum_counter[i] = 0

            # 3-d) 시간 증가 로직
            if all(r is None for r in running) and not rr_queue and arrived_idx < len(arrival_sorted):
                time = arrival_sorted[arrived_idx].arrival_time  # 다음 도착 시간으로 건너뛰기
            else:
                time += 1  # 기본 1초 증가

        # ── 4) 메트릭 계산 ──
        for p in ready_queue:
            # 실행 또는 종료 시간 보정
            if p.finish_time is None:
                p.finish_time = time
            if p.start_time is None:
                p.start_time = p.arrival_time

            # 반환 시간: 전체 걸린 시간
            p.turn_around_time = p.finish_time - p.arrival_time
            # 대기 시간 = 반환 - 실제 서비스 시간
            p.waiting_time     = p.turn_around_time - p.real_burst
            # 정규화 TT
            p.normalized_TT    = round(p.turn_around_time / p.real_burst, 2)
