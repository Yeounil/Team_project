from collections import deque

class Process:
    def __init__(this, pid, arrival, burst):
        this.pid = pid
        this.arrival = arrival
        this.burst = burst
        this.remaining = burst
        this.completion = 0
        this.waiting = 0
        this.turnaround = 0
        this.normalized_tt = 0


class Core:
    def __init__(self, cid, core_type):
        self.cid = cid  # 코어 번호
        self.core_type = core_type  # 'P' 또는 'E'
        self.is_idle = True  # 현재 유휴상태 여부
        self.current_process = None  # 현재 할당된 프로세스
        self.used_time = 0  # 사용 시간
        self.startup_count = 0  # 시동 횟수
        self.last_used = -1  # 마지막 사용 시점 -> 마지막 사용시점으로부터 몇초가 지나면 다시 idle(절전)상태로 진입할지 기준 결정 필요한가?

        if core_type == 'P':
            self.performance = 2
            self.power_rate = 3
            self.startup_power = 0.5
        else:
            self.performance = 1
            self.power_rate = 1
            self.startup_power = 0.1

class ProcessScheduler:
    def __init__(this, processes, cores, algorithm, time_quantum=None):
        this.processes = sorted(processes, key=lambda p: p.arrival)
        this.cores = cores
        this.algorithm = algorithm
        this.time_quantum = time_quantum
        this.current_time = 0
        this.ready_queue = deque()
        this.completed = []
        this.proc_index = 0
        this.execution_log = []  # (시간, 코어ID, 프로세스ID, 실행량)
        this.total_power = 0

    def add_arrived_processes(this):
        while this.proc_index < len(this.processes) and this.processes[this.proc_index].arrival <= this.current_time:
            this.ready_queue.append(this.processes[this.proc_index])
            this.proc_index += 1

    def run_round_robin(this):
        while len(this.completed) < len(this.processes):
            this.add_arrived_processes()
            # 빈 코어에 프로세스 할당
            for core in this.cores:
                if not core.busy and this.ready_queue:
                    proc = this.ready_queue.popleft()
                    core.current_proc = proc
                    core.busy = True
                    core.run_time = 0
                    if core.was_idle:
                        this.total_power += core.startup_power
                        core.was_idle = False

            # 1초 단위 실행
            for core in this.cores:
                if core.busy:
                    proc = core.current_proc
                    work_unit = min(core.performance, proc.remaining)
                    proc.remaining -= work_unit
                    core.run_time += 1
                    this.total_power += core.power_rate
                    this.execution_log.append((this.current_time, core.id, core.type, proc.pid, work_unit))

                    if proc.remaining == 0:
                        proc.completion = this.current_time + 1
                        proc.turnaround = proc.completion - proc.arrival
                        proc.waiting = proc.turnaround - proc.burst
                        proc.normalized_tt = proc.turnaround / proc.burst
                        this.completed.append(proc)
                        core.current_proc = None
                        core.busy = False
                        core.run_time = 0
                        core.was_idle = True
                    elif core.run_time == this.time_quantum:
                        this.ready_queue.append(proc)
                        core.current_proc = None
                        core.busy = False
                        core.run_time = 0
                        core.was_idle = True
                else:
                    core.was_idle = True

            this.current_time += 1

            # 모든 코어가 비어있고 큐도 비어있지만 아직 도착하지 않은 프로세스가 있는 경우
            if all(not core.busy for core in this.cores) and not this.ready_queue and this.proc_index < len(this.processes):
                this.current_time = this.processes[this.proc_index].arrival

    def run(this):
        if this.algorithm == 'RR':
            this.run_round_robin()
        # 다른 알고리즘은 여기에 추가 가능

    def print_results(this):
        print("\n[프로세스 결과 요약]")
        print("PID\t도착\t실행\t대기\t반환\tNTT")
        for p in sorted(this.completed, key=lambda x: x.pid):
            print(f"{p.pid}\t{p.arrival}\t{p.burst}\t{p.waiting}\t{p.turnaround}\t{p.normalized_tt:.2f}")

        print("\n[Gantt Chart]")
        for entry in this.execution_log:
            time, core_id, core_type, pid, work = entry
            print(f"Time {time}: Core {core_id}({core_type}) runs P{pid} ({work})")

        print(f"\n총 소비 전력: {this.total_power:.1f}W")

def main():
    n_proc = int(input("프로세스 개수: "))
    n_cores = int(input("코어 개수: "))
    n_p_cores = int(input("P코어 개수: "))
    arrival_times = list(map(int, input("도착시간 (공백 구분): ").split()))
    burst_times = list(map(int, input("실행시간 (공백 구분): ").split()))
    time_quantum = int(input("RR 타임퀀텀: "))

    processes = [Process(i+1, arrival_times[i], burst_times[i]) for i in range(n_proc)]
    cores = []
    for i in range(n_cores):
        if i < n_p_cores:
            cores.append(Core(i+1, 'P'))
        else:
            cores.append(Core(i+1, 'E'))

    scheduler = ProcessScheduler(processes, cores, 'RR', time_quantum)
    scheduler.run()
    scheduler.print_results()

if __name__ == "__main__":
    main()
