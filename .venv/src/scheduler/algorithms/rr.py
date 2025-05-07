from collections import deque
from scheduler.process import Process
from scheduler.multicore.scheduler import Core

class RoundRobin:
    def __init__(self, quantum=2):
        self.quantum = quantum  # RR 타임퀀텀 값 설정

    def schedule(self, ready_queue, pcores, ecores):
        time       = 0  # 전체 시뮬레이션 시간
        all_cores  = pcores + ecores  # 모든 코어 목록
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

        # ── 3) 메인 스케줄링 루프 ── , 모든 프로세스가 종료할 때 까지 아래 4가지의 로직을 반복
        while not all(p.executed for p in ready_queue):

            # 3-a) 현재 시간에 도착한 프로세스들을 큐에 추가
            while arrived_idx < len(arrival_sorted) and \
                  arrival_sorted[arrived_idx].arrival_time <= time:
                rr_queue.append(arrival_sorted[arrived_idx])
                arrived_idx += 1  # 도착한 프로세스는 rr_queue에 넣고 인덱스 증가
                      
            assigned_pid = set() # 이번 tick에서 이미 코어에 할당된 pid 집합(중복 할당 방지)


            # 3-b) 코어별 상태 갱신 후 프로세스 할당 과
            for i, core in enumerate(all_cores):
                proc = running[i]

             # (1) 프로세스가 완전 종료된 경우(타임 퀀텀에 의해 벗어난 것이 아닌, 프로세스 실행 시간이 다 된 경우: 종료 처리 및 코어 비우기)
                if proc and proc.remaining_time <= 0: # 순서대로, 종료시간을 기록하고 프로젝트 완료 표시 후 코어를 비우고 퀀텀을 초기화
                    if proc.finish_time is None:
                        proc.finish_time = time + 1 
                    proc.executed      = True
                    running[i]         = None
                    quantum_counter[i] = 0

                # (2) 퀀텀 소진 & 아직 남은 작업이 있다면: 프로세스를 다시 대기열로
                elif proc and quantum_counter[i] <= 0 and proc.remaining_time > 0:
                    rr_queue.append(proc)
                    running[i]         = None

                # (3) 코어가 비어있고 대기열에 프로세스가 있으면 새로 할당
                if running[i] is None and rr_queue:
                    for idx, p in enumerate(rr_queue):
                         # 아직 실행이 끝나지 않았고, 이번 tick에 이미 할당되지 않은 프로세스만
                        if (not p.executed) and (p.pid not in assigned_pid):
                            running[i]         = p       #코어 할당
                            quantum_counter[i] = self.quantum # 퀀텀 값 리셋
                            assigned_pid.add(p.pid) # 중복 방지용 pid 등
                            rr_queue.remove(p) # 대기열에서 제거하기
                            # 최초 실행 시간 기록
                            if p.start_time is None:
                                p.start_time = time
                            break

            # 3-c) 실제 실행 단계
            for i, core in enumerate(all_cores):
                proc = running[i]
                # 실행 조건: 프로세스가 있고, 남은 시간이 있고, 퀀텀이 남아야 함
                if not proc or proc.remaining_time <= 0 or quantum_counter[i] <= 0:
                    core.is_idle = True
                    continue

                # 코어 성능만큼 처리 (P: 2, E: 1)
                work = min(core.performance, proc.remaining_time)
                proc.remaining_time -= work              # 남은 실행시간 차감
                proc.real_burst     += 1                 # 실제 tick 수 증가
                quantum_counter[i]  -= 1                 # 퀀텀 차감

                # Gantt 차트 기록 (1초 단위)
                for _ in range(work):
                    core.timeline.append((time, proc.pid, 1))

                # 전력 계산, 유휴였다면 시동 전력, 동작 전력 추가
                if core.is_idle:
                    core.total_power   += core.startup_power
                    core.is_idle        = False
                core.total_power += core.power_rate * work

                # 프로세스가 종료된 경우 처리
                if proc.remaining_time == 0 and proc.finish_time is None:
                    proc.finish_time = time + 1
                    proc.executed    = True
                    running[i]       = None
                    quantum_counter[i] = 0

            # 3-d) 시간 증가 로직, 모든 코어가 비고 대기열도 비었고 도착 할 프로세스가 남았다면 불필요한 idle 시간을 넘김
            if all(r is None for r in running) and not rr_queue and arrived_idx < len(arrival_sorted):
                time = arrival_sorted[arrived_idx].arrival_time 
            else:
                time += 1  # 기본 1초 증가

        # ── 4) 최종 계산 ──
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
