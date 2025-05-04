class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid  # 프로세스 이름(번호)
        self.arrival_time = arrival_time  # 도착시간
        self.burst_time = burst_time  # 실행시간(일의 양)
        self.remaining_time = burst_time  # 남은 실행시간
        self.start_time = None  # 실제 시작시간
        self.finish_time = None  # 종료시간
        self.waiting_time = 0  # 대기시간
        self.turn_around_time = 0  # 반환시간
        self.normalized_TT = 0  # NTT
        self.executed = 0 # 프로세스 실행 여부
