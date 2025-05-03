# 프로세스 정보 저장용 클래스
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

# 코어 정보 저장용 클래스
class Core:
    def __init__(self, cid, core_type):
        self.cid = cid  # 코어 번호
        self.core_type = core_type  # 'P' 또는 'E'
        self.is_idle = True  # 현재 유휴상태 여부
        self.current_allocate_process = None  # 현재 할당된 프로세스
        self.used_time = 0  # 사용 시간
        self.startup_count = 0  # 시동 횟수
        self.last_used = -1  # 마지막 사용 시점 -> 마지막 사용시점으로부터 몇초가 지나면 다시 idle(절전)상태로 진입할지 기준 결정 필요한가?


# 입력 받기
of_processes = int(input("of Processes: "))
of_Processors = int(input("of Processors: "))
of_P_core = int(input("of P core: "))
of_E_core = of_Processors - of_P_core

arrival_times = list(map(int, input("Arrival time(공백 구분): ").split()))
burst_times = list(map(int, input("Burst time(공백 구분): ").split()))
time_quantum = int(input("Time quantum for RR: "))


# 프로세스 리스트 생성
processes = []
for i in range(of_processes):
    processes.append(Process(f'P{i+1}', arrival_times[i], burst_times[i]))

# 코어 리스트 생성
cores = []
for i in range(of_P_core):
    cores.append(Core(i, 'P'))
for i in range(of_E_core):
    cores.append(Core(of_P_core + i, 'E'))



current_time = 0
ready_queue = []
of_finished_processes = 0

while of_finished_processes < of_processes:
    # 도착한 프로세스 ready_queue에 추가
    for process in processes:
        if process.arrival_time == current_time:
            ready_queue.append(process)
    
    # 각 코어에 프로세스 할당
    for core in cores:
        if core.current_allocate_process is None and ready_queue:
            core.current_allocate_process = ready_queue.pop(0)
            if core.current_allocate_process.start_time is None:
                core.current_allocate_process.start_time = current_time
            # 코어 시동전력 체크
            if core.is_idle:
                core.startup_count += 1
                core.is_idle = False
    
    # 각 코어에서 프로세스 실행
    for core in cores:
        if core.current_allocate_process:
            # 코어 종류에 따라 처리량 결정
            time_reduction_per_second = 2 if core.core_type == 'P' else 1
            # 실제 남은 일의 양이 speed보다 적어도 1초 소요
            core.current_allocate_process.remaining_time -= time_reduction_per_second
            core.used_time += 1
            if core.current_allocate_process.remaining_time <= 0:
                # 프로세스 종료
                core.current_allocate_process.finish_time = current_time + 1
                of_finished_processes += 1
                core.current_allocate_process = None
        else:
            core.is_idle = True
    current_time += 1



print("\n[FCFS 결과]")
print("Process  AT  BT  WT  TT  NTT")
for process in processes:
    process.turn_around_time = process.finish_time - process.arrival_time
    process.waiting_time = process.start_time - process.arrival_time  # 수정!
    process.normalized_TT = round(process.turn_around_time / process.burst_time, 2)
    print(f"{process.pid:>7}  {process.arrival_time:>2}  {process.burst_time:>2}  {process.waiting_time:>2}  {process.turn_around_time:>2}  {process.normalized_TT:>4}")

# 코어별 전력 계산
def calculate_power(core):
    if core.core_type == 'P':
        return core.used_time * 3 + core.startup_count * 0.5
    else:
        return core.used_time * 1 + core.startup_count * 0.1

total_power = 0
for core in cores:
    power = calculate_power(core)
    total_power += power
    print(f"Core {core.cid} ({core.core_type}-core): 사용시간 {core.used_time}, 시동 {core.startup_count}회, 전력 {power:.2f}W")
print(f"총 전력: {total_power:.2f}W")



# 궁금한 점
# 만약에 E core에 할당된 프로세스가 10만큼 남았는데 P core에 할당된 게 모두 종료돼서 P core가 할 일이 없으면 E core꺼를 P core로 옮겨야하나?

# # 프로세스 정보 저장용 클래스
# class Process:
#     def __init__(self, pid, arrival_time, burst_time):
#         self.pid = pid  # 프로세스 이름(번호)
#         self.arrival_time = arrival_time  # 도착시간
#         self.burst_time = burst_time  # 실행시간(일의 양)
#         self.remaining_time = burst_time  # 남은 실행시간
#         self.start_time = None  # 실제 시작시간
#         self.finish_time = None  # 종료시간
#         self.waiting_time = 0  # 대기시간
#         self.turn_around_time = 0  # 반환시간
#         self.normalized_TT = 0  # NTT

# # 코어 정보 저장용 클래스
# class Core:
#     def __init__(self, cid, core_type):
#         self.cid = cid  # 코어 번호
#         self.core_type = core_type  # 'P' 또는 'E'
#         self.is_idle = True  # 현재 유휴상태 여부
#         self.current_allocate_process = None  # 현재 할당된 프로세스
#         self.used_time = 0  # 사용 시간
#         self.startup_count = 0  # 시동 횟수
#         self.last_used = -1  # 마지막 사용 시점 -> 마지막 사용시점으로부터 몇초가 지나면 다시 idle(절전)상태로 진입할지 기준 결정 필요한가?


# # 입력 받기
# of_processes = int(input("of Processes: "))
# of_Processors = int(input("of Processors: "))
# of_P_core = int(input("of P core: "))
# of_E_core = of_Processors - of_P_core

# arrival_times = list(map(int, input("Arrival time(공백 구분): ").split()))
# burst_times = list(map(int, input("Burst time(공백 구분): ").split()))
# time_quantum = int(input("Time quantum for RR: "))


# # 프로세스 리스트 생성
# processes = []
# for i in range(of_processes):
#     processes.append(Process(f'P{i+1}', arrival_times[i], burst_times[i]))

# # 코어 리스트 생성
# cores = []
# for i in range(of_P_core):
#     cores.append(Core(i, 'P'))
# for i in range(of_E_core):
#     cores.append(Core(of_P_core + i, 'E'))



# current_time = 0
# ready_queue = []
# of_finished_processes = 0

# while of_finished_processes < of_processes:
#     # 도착한 프로세스 ready_queue에 추가
#     newly_arrived = []
#     for process in processes:
#         if process.arrival_time == current_time:
#             ready_queue.append(process)
#             newly_arrived.append(process)

#     # 대기시간 누적 (이번 초에 새로 도착한 건 빼고 누적)
#     for process in ready_queue:
#         if process not in newly_arrived:
#             process.waiting_time += 1

    
#     # 각 코어에 프로세스 할당
#     for core in cores:
#         if core.current_allocate_process is None and ready_queue:
#             core.current_allocate_process = ready_queue.pop(0)
#             if core.current_allocate_process.start_time is None:
#                 core.current_allocate_process.start_time = current_time
#             # 코어 시동전력 체크
#             if core.is_idle:
#                 core.startup_count += 1
#                 core.is_idle = False
    
#     # 각 코어에서 프로세스 실행
#     for core in cores:
#         if core.current_allocate_process:
#             # 코어 종류에 따라 처리량 결정
#             time_reduction_per_second = 2 if core.core_type == 'P' else 1
#             # 실제 남은 일의 양이 speed보다 적어도 1초 소요
#             core.current_allocate_process.remaining_time -= time_reduction_per_second
#             core.used_time += 1
#             if core.current_allocate_process.remaining_time <= 0:
#                 # 프로세스 종료
#                 core.current_allocate_process.finish_time = current_time + 1
#                 of_finished_processes += 1
#                 core.current_allocate_process = None
#         else:
#             core.is_idle = True
#     current_time += 1



# print("\n[FCFS 결과]")
# print("Process  AT  BT  WT  TT  NTT")
# for process in processes:
#     process.turn_around_time = process.finish_time - process.arrival_time
#     # process.waiting_time = process.star10t_time - process.arrival_time  # 수정!
#     process.normalized_TT = round(process.turn_around_time / process.burst_time, 2)
#     print(f"{process.pid:>7}  {process.arrival_time:>2}  {process.burst_time:>2}  {process.waiting_time:>2}  {process.turn_around_time:>2}  {process.normalized_TT:>4}")

# # 코어별 전력 계산
# def calculate_power(core):
#     if core.core_type == 'P':
#         return core.used_time * 3 + core.startup_count * 0.5
#     else:
#         return core.used_time * 1 + core.startup_count * 0.1

# total_power = 0
# for core in cores:
#     power = calculate_power(core)
#     total_power += power
#     print(f"Core {core.cid} ({core.core_type}-core): 사용시간 {core.used_time}, 시동 {core.startup_count}회, 전력 {power:.2f}W")
# print(f"총 전력: {total_power:.2f}W")



# # 궁금한 점
# # 만약에 E core에 할당된 프로세스가 10만큼 남았는데 P core에 할당된 게 모두 종료돼서 P core가 할 일이 없으면 E core꺼를 P core로 옮겨야하나?