from collections import deque

class Process:
    def __init__(me, pid, arrival, burst):
        me.pid = pid
        me.arrival = arrival
        me.burst = burst
        me.remaining = burst
        me.completion = 0
        me.waiting = 0
        me.turnaround = 0

class RoundRobin:
    def __init__(me, processes, time_quantum):
        me.processes = sorted(processes, key=lambda p: p.arrival)
        me.time_quantum = time_quantum
        me.time = 0
        me.queue = deque()
        me.log = []

    def run(me):
        n = len(me.processes)
        completed = 0
        idx = 0

        while idx < n and me.processes[idx].arrival <= me.time:
            me.queue.append(me.processes[idx])
            idx += 1

        if not me.queue and idx < n:
            me.time = me.processes[idx].arrival
            me.queue.append(me.processes[idx])
            idx += 1

        while completed < n:
            if not me.queue:
                if idx < n:
                    me.time = me.processes[idx].arrival
                    me.queue.append(me.processes[idx])
                    idx += 1
                continue

            current = me.queue.popleft()
            run_time = min(current.remaining, me.time_quantum)
            me.log.append((me.time, current.pid, run_time))

            me.time += run_time
            current.remaining -= run_time

            while idx < n and me.processes[idx].arrival <= me.time:
                me.queue.append(me.processes[idx])
                idx += 1

            if current.remaining == 0:
                current.completion = me.time
                current.turnaround = current.completion - current.arrival
                current.waiting = current.turnaround - current.burst
                completed += 1
            else:
                me.queue.append(current)

    def print_results(me):
        print("\n[결과 프로세스 요약]")
        print("프로세스 이름\t도착\t시간\t대기\tTurnaround")
        for p in sorted(me.processes, key=lambda x: x.pid):
            print(f"{p.pid}\t{p.arrival}\t{p.burst}\t{p.waiting}\t{p.turnaround}")

        print("\n[Gantt Chart] - 차트입니다.")
        for start, pid, duration in me.log:
            print(f"| P{pid} ({start}~{start+duration}) ", end="")
        print("|")

def main():
    n = int(input("프로세스 개수는?"))
    print("각 프로세스 도착 시간을 공백으로 구분해서 입력해주세요.")
    arrivals = list(map(int, input().split()))
    print("동일하게, 실행 시간을 공백으로 입력하세요.")
    bursts = list(map(int, input().split()))
    tq = int(input("타임 퀀텀은 몇으로 설정할까요?"))

    processes = [Process(i+1, arrivals[i], bursts[i]) for i in range(n)]
    rr = RoundRobin(processes, tq)
    rr.run()
    rr.print_results()

if __name__ == "__main__":
    main()
