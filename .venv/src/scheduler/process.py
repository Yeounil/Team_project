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