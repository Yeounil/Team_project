class Core:
    def __init__(self, core_id):
        self.core_id = core_id
        self.current_process = None
        self.timeline = []  # (start_time, pid)
        self.next_free_time = 0 # 현재 작업이 끝나는 시간
        self.core_type = core_type  # 'P' 또는 'E'
        self.is_idle = True  # 현재 유휴상태 여부
        self.used_time = 0  # 사용 시간
        self.startup_count = 0  # 시동 횟수

        if core_type == 'P':
            self.performance = 2
            self.power_rate = 3
            self.startup_power = 0.5
        else:
            self.performance = 1
            self.power_rate = 1
            self.startup_power = 0.1

class MultiCoreScheduler:
    def __init__(self, core_count, scheduler):
        self.cores = [Core(i) for i in range(core_count)]
        self.scheduler = scheduler
        self.processes = []

    def load_processes(self, process_list):
        self.processes = process_list

    def run(self):
        ready_queue = self.processes.copy()
        self.scheduler.schedule(ready_queue, self.cores)

    def get_results(self):
        output = ""
        for core in self.cores:
            output += f"Core {core.core_id}: {core.timeline}\n"
        return output
